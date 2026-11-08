"""Tests : python -m pytest tests  (ou python tests/test_bot.py)."""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from foodhunt.config import Config  # noqa: E402
from foodhunt.strategy import choose_move, simulate_loop  # noqa: E402
from foodhunt.vision import EMPTY, Block, GameState, Picture, read_level, read_state  # noqa: E402

SAMPLE = ROOT / "samples" / "level257.jpg"


def test_sample_screenshot_is_read_correctly():
    img = cv2.imread(str(SAMPLE))
    s = read_state(img, Config())
    assert s.picture is not None
    assert s.picture.grid.shape[1] == 40
    assert s.picture.remaining > 1000
    tray = [(b.ammo, b.color) for b in s.tray]
    assert [a for a, _ in tray] == [14, 36, 4, 8, 9]
    # même couleur pour les deux rouges et les deux oranges
    assert tray[0][1] == tray[2][1] and tray[3][1] == tray[4][1]
    grid = [(b.col, b.ammo) for b in s.grid_tappable]
    assert grid == [(0, 34), (3, 4)]
    assert s.grid_tappable[0].color == tray[1][1]      # 34 jaune = 36 jaune
    assert read_level(img) == 257
    # file pleine et aucune couleur accessible : le bot ne doit rien risquer
    assert choose_move(s, Config()) is None


def test_simulation_only_hits_exposed_pixels():
    g = np.array([[0, 0, 0],
                  [0, 1, 0],
                  [0, 0, 0]])
    d, _ = simulate_loop(g, 1, 10)
    assert d == 0                                    # le 1 est caché
    d, g2 = simulate_loop(g, 0, 100)
    assert d == 8 and g2[1, 1] == 1


def _state(grid, tray, gridb):
    pic = Picture((0, 0, 1, 1), np.array(grid), [np.zeros(3), np.ones(3)], (0, 0), (1, 1))
    blocks = [Block("tray", 0, i, 0, 0, True, a, color=c) for i, (a, c) in enumerate(tray)]
    blocks += [Block("grid", 0, i, 0, 0, True, a, color=c) for i, (a, c) in enumerate(gridb)]
    return GameState(pic, blocks)


def test_prefers_exact_clear_and_avoids_full_tray():
    grid = [[0, 0, 1, 1]]
    # bloc rouge(0) de 2 = vide exactement ; bloc bleu(1) de 9 laisserait des munitions
    s = _state(grid, [], [(9, 1), (2, 0)])
    m = choose_move(s, Config())
    assert m.block.ammo == 2 and m.leftover == 0
    # file presque pleine : on ne prend pas un bloc qui reviendrait dans la file
    s = _state(grid, [(5, 1)] * 4, [(9, 0)])
    m = choose_move(s, Config())
    assert m.block.zone == "tray"                       # on vide la file d'abord


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("OK", name)
