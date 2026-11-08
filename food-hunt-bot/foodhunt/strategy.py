"""Choix du prochain bloc à envoyer sur le tapis.

Modèle du jeu (hypothèse) : un tireur fait un tour du tableau. À chaque ligne/colonne
qu'il longe, il détruit le premier pixel visible depuis l'extérieur si ce pixel est de
sa couleur (1 munition par pixel). S'il lui reste des munitions à la fin du tour, il va
dans la file d'attente (5 places) ; si la file est pleine, la partie est perdue.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import Config
from .vision import EMPTY, Block, GameState


@dataclass
class Move:
    block: Block
    destroyed: int
    leftover: int
    score: float
    reason: str


def _first(line: np.ndarray) -> int | None:
    idx = np.nonzero(line != EMPTY)[0]
    return int(idx[0]) if len(idx) else None


def simulate_loop(grid: np.ndarray, color: int, ammo: int) -> tuple[int, np.ndarray]:
    """Simule un tour complet d'un tireur. Renvoie (pixels détruits, nouvelle grille)."""
    g = grid.copy()
    rows, cols = g.shape
    destroyed = 0
    # haut (gauche→droite), droite (haut→bas), bas (droite→gauche), gauche (bas→haut)
    lanes = ([("top", c) for c in range(cols)] + [("right", r) for r in range(rows)]
             + [("bottom", c) for c in reversed(range(cols))] + [("left", r) for r in reversed(range(rows))])
    for side, i in lanes:
        if ammo <= 0:
            break
        if side == "top":
            j = _first(g[:, i]); cell = (j, i) if j is not None else None
        elif side == "bottom":
            j = _first(g[::-1, i]); cell = (rows - 1 - j, i) if j is not None else None
        elif side == "left":
            j = _first(g[i, :]); cell = (i, j) if j is not None else None
        else:
            j = _first(g[i, ::-1]); cell = (i, cols - 1 - j) if j is not None else None
        if cell is not None and g[cell] == color:
            g[cell] = EMPTY
            ammo -= 1
            destroyed += 1
    return destroyed, g


def exposed_count(grid: np.ndarray, color: int) -> int:
    d, _ = simulate_loop(grid, color, 10 ** 6)
    return d


def choose_move(state: GameState, cfg: Config, banned: set | None = None) -> Move | None:
    pic = state.picture
    if pic is None or pic.grid.size == 0 or pic.remaining == 0:
        return None
    banned = banned or set()
    grid = pic.grid
    tray = state.tray
    tray_used = len(tray)
    remaining_by_color = {k: int((grid == k).sum()) for k in range(len(pic.palette))}

    candidates: list[Move] = []
    for b in tray + state.grid_tappable:
        key = (b.zone, b.row, b.col)
        if key in banned or b.color is None:
            continue
        ammo = b.ammo if b.ammo is not None else cfg.unknown_ammo
        destroyed, _ = simulate_loop(grid, b.color, ammo)
        leftover = max(0, ammo - destroyed)
        score = float(destroyed)
        if b.zone == "tray":
            if destroyed == 0:
                continue
            reason = "file d'attente"
            if leftover == 0:
                score += 60          # libère une place
        else:
            after = tray_used + (1 if leftover > 0 else 0)
            if after > cfg.tray_capacity:
                continue             # ferait perdre
            reason = "grille"
            if leftover == 0:
                score += 40
            else:
                score -= 15 + 12 * after
                if after == cfg.tray_capacity:
                    score -= 200     # dernière place : seulement en dernier recours
                # un tireur qui pourra tout vider plus tard est moins grave
                if ammo <= remaining_by_color.get(b.color, 0):
                    score += 5
        candidates.append(Move(b, destroyed, leftover, score, reason))

    useful = [m for m in candidates if m.destroyed > 0]
    if useful:
        return max(useful, key=lambda m: m.score)
    # rien ne détruit de pixel tout de suite : on débloque avec le bloc de la grille
    # qui a le plus de pixels de sa couleur restants, si la file a de la place
    fallback = [m for m in candidates if m.block.zone == "grid"
                and tray_used + 1 < cfg.tray_capacity]
    if fallback:
        m = max(fallback, key=lambda m: remaining_by_color.get(m.block.color, 0))
        m.reason = "déblocage"
        return m
    return None
