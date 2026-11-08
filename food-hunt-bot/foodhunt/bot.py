"""Boucle principale du bot."""
from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from .config import Config
from .device import Device
from .strategy import choose_move
from .vision import annotate, find_text_buttons, read_level, read_state


def log(msg: str) -> None:
    print(time.strftime("[%H:%M:%S] ") + msg, flush=True)


class Bot:
    def __init__(self, cfg: Config, dry_run: bool = False, save_debug: bool = False):
        self.cfg = cfg
        self.dev = Device(cfg.adb_path, cfg.device_serial)
        self.dry_run = dry_run
        self.save_debug = save_debug
        self.debug_dir = Path(cfg.debug_dir)
        self.level: int | None = None
        self.levels_done = 0
        self.banned: set = set()
        self.last_tap: tuple | None = None
        self.same_tap_count = 0

    # ------------------------------------------------------------------ utils
    def _save(self, name: str, img: np.ndarray) -> Path:
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        p = self.debug_dir / f"{time.strftime('%Y%m%d-%H%M%S')}-{name}.jpg"
        cv2.imwrite(str(p), img)
        return p

    def _tap(self, x: int, y: int) -> None:
        if self.dry_run:
            log(f"   (simulation) tap {x},{y}")
            return
        self.dev.tap(x, y)

    def _board_signature(self, img: np.ndarray) -> np.ndarray:
        small = cv2.resize(img, (90, 195), interpolation=cv2.INTER_AREA)
        return small[: int(195 * 0.75)].astype(float)   # tableau + file, sans les bonus

    def _wait_settle(self) -> np.ndarray:
        """Attend que l'écran ne bouge plus (tireurs revenus, animations finies)."""
        time.sleep(self.cfg.tap_delay_s)
        deadline = time.time() + self.cfg.settle_timeout_s
        prev = self.dev.screenshot()
        while time.time() < deadline:
            cur = self.dev.screenshot()
            if np.abs(self._board_signature(cur) - self._board_signature(prev)).mean() < self.cfg.settle_threshold:
                return cur
            prev = cur
        return prev

    # ------------------------------------------------------------ écrans menu
    def _handle_menu(self, img: np.ndarray) -> bool:
        """Écran sans tableau (victoire, défaite, bonus…) : touche un bouton autorisé."""
        texts = find_text_buttons(img)
        for word in self.cfg.continue_words:
            for text, x, y in texts:
                if any(f in text for f in self.cfg.forbidden_words):
                    continue
                if text == word or text.startswith(word + " ") or (len(word) > 3 and word in text):
                    log(f"Écran « {text} » → je touche le bouton")
                    self._tap(x, y)
                    return True
        return False

    # ------------------------------------------------------------- boucle
    def run(self, max_levels: int = 0) -> None:
        serial = self.dev.check()
        log(f"Téléphone connecté : {serial}")
        idle = 0
        no_move = 0
        while True:
            img = self.dev.screenshot()
            state = read_state(img, self.cfg)

            if state.picture is None:
                if self._handle_menu(img):
                    idle = 0
                    time.sleep(1.5)
                    continue
                idle += 1
                if idle == 5:
                    p = self._save("ecran-inconnu", img)
                    log(f"Écran non reconnu, capture enregistrée : {p}")
                if idle >= self.cfg.max_idle_loops:
                    log("Je suis bloqué sur un écran inconnu, j'arrête. "
                        "(Pub ? Ferme-la puis relance le bot.)")
                    return
                time.sleep(2)
                continue
            idle = 0

            level = read_level(img)
            if level is not None and level != self.level:
                if self.level is not None:
                    self.levels_done += 1
                    log(f"Niveau {self.level} terminé ({self.levels_done} au total)")
                    if max_levels and self.levels_done >= max_levels:
                        log("Nombre de niveaux demandé atteint, j'arrête.")
                        return
                self.level = level
                self.banned.clear()
                log(f"=== Niveau {level} ===")

            if state.picture.remaining == 0:
                time.sleep(1.5)
                continue

            move = choose_move(state, self.cfg, self.banned)
            if self.save_debug:
                self._save(f"niv{self.level}", annotate(img, state, move))
            if move is None:
                no_move += 1
                if no_move == 3:
                    p = self._save("bloque", annotate(img, state))
                    log("Aucun coup sûr : la file d'attente est pleine ou aucune couleur n'est "
                        f"accessible. Utilise un bonus à la main. Capture : {p}")
                time.sleep(3)
                continue
            no_move = 0

            b = move.block
            key = (b.zone, b.row, b.col, b.ammo, b.color)
            self.same_tap_count = self.same_tap_count + 1 if key == self.last_tap else 1
            self.last_tap = key
            if self.same_tap_count > 3:
                log(f"Le bloc {b.ammo} ({b.zone}) ne réagit pas, je l'ignore pour ce niveau.")
                self.banned.add((b.zone, b.row, b.col))
                continue

            log(f"Tir : bloc {b.ammo if b.ammo is not None else '?'} ({move.reason}, "
                f"col {b.col + 1}) → {move.destroyed} pixels, reste {move.leftover} "
                f"| pixels restants {state.picture.remaining}, file {len(state.tray)}/{self.cfg.tray_capacity}")
            self._tap(b.x, b.y)
            if self.dry_run:
                return
            self._wait_settle()
