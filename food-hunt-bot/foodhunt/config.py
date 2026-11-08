"""Paramètres du bot. Toutes les positions sont en fractions de la taille de l'écran
(calibrées sur une capture 1440x3120). Surchargeables via un fichier config.json."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict, fields
from pathlib import Path


@dataclass
class Config:
    # --- ADB ---
    adb_path: str = "adb"            # chemin vers adb.exe si pas dans le PATH
    device_serial: str = ""          # vide = premier appareil connecté

    # --- Plateau (image en pixels) ---
    board_bg_bgr: tuple = (210, 218, 235)   # couleur beige du fond du tableau
    board_bg_tolerance: int = 12

    # --- Blocs tireurs ---
    # Centres des 5 colonnes (fraction de la largeur)
    column_x: list = field(default_factory=lambda: [0.1764, 0.3382, 0.4993, 0.6611, 0.8222])
    # Ligne de la file d'attente (les 5 emplacements du haut)
    tray_y: float = 0.670
    # Lignes de la grille de blocs (la première est celle qu'on peut toucher)
    grid_rows_y: list = field(default_factory=lambda: [0.766, 0.840, 0.904])
    tray_capacity: int = 5
    # Un bloc est « jouable » si son chiffre a un contour sombre (bloc non grisé)
    min_dark_pixels: int = 300
    block_half_w: float = 0.059      # demi-largeur d'un bloc (fraction de la largeur)
    block_half_h: float = 0.0225     # demi-hauteur de la zone analysée (fraction de la hauteur)
    unknown_ammo: int = 10           # munitions supposées quand le chiffre est illisible

    # --- Boucle de jeu ---
    tap_delay_s: float = 0.6         # pause minimale après un tap
    settle_timeout_s: float = 12.0   # attente max que le plateau se stabilise
    settle_threshold: float = 1.5    # différence moyenne (0-255) considérée comme « stable »
    max_idle_loops: int = 25         # écrans non reconnus d'affilée avant de s'arrêter

    # Boutons des écrans de fin de niveau, reconnus par OCR (minuscules)
    continue_words: list = field(default_factory=lambda: [
        "next", "continue", "tap to continue", "claim", "ok", "play", "retry", "try again",
        "suivant", "continuer", "jouer", "réessayer", "recommencer", "récupérer"])
    # Mots qui interdisent un bouton (achats, pièces, pubs)
    forbidden_words: list = field(default_factory=lambda: [
        "€", "$", "buy", "acheter", "purchase", "coins", "pièces", "shop", "boutique",
        "no ads", "sans pub", "watch", "regarder", "free", "gratuit", "x2", "revive"])

    debug_dir: str = "debug"

    @classmethod
    def load(cls, path: str | Path | None) -> "Config":
        cfg = cls()
        if path and Path(path).exists():
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            names = {f.name for f in fields(cls)}
            for k, v in data.items():
                if k in names:
                    setattr(cfg, k, tuple(v) if k == "board_bg_bgr" else v)
        return cfg

    def dump(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")
