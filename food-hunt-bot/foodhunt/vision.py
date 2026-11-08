"""Lecture de l'écran : image en pixels à détruire et blocs tireurs."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import cv2
import numpy as np

from .config import Config

EMPTY = -1


@dataclass
class Picture:
    rect: tuple            # (x, y, w, h) du tableau dans l'écran
    grid: np.ndarray       # (rows, cols) : index de couleur, EMPTY si vide
    palette: list          # couleurs Lab (np.array de 3 floats) par index
    origin: tuple          # (x, y) du coin de la première cellule, en coordonnées écran
    pitch: tuple           # (px, py) taille d'une cellule

    @property
    def remaining(self) -> int:
        return int((self.grid != EMPTY).sum())


@dataclass
class Block:
    zone: str              # "tray" (file d'attente) ou "grid"
    row: int
    col: int
    x: int
    y: int
    tappable: bool
    ammo: int | None = None
    text: str = ""
    color_bgr: tuple | None = None
    color: int | None = None   # index dans la palette de l'image


@dataclass
class GameState:
    picture: Picture | None
    blocks: list = field(default_factory=list)

    @property
    def tray(self) -> list:
        return [b for b in self.blocks if b.zone == "tray" and b.tappable]

    @property
    def grid_tappable(self) -> list:
        return [b for b in self.blocks if b.zone == "grid" and b.tappable]


def bgr_to_lab(bgr) -> np.ndarray:
    return cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2LAB)[0, 0].astype(float)


def lab_to_bgr(lab) -> tuple:
    v = np.clip(np.round(lab), 0, 255).astype(np.uint8)
    return tuple(int(c) for c in cv2.cvtColor(np.uint8([[v]]), cv2.COLOR_LAB2BGR)[0, 0])


# ---------------------------------------------------------------- tableau ----

def find_board(img: np.ndarray, cfg: Config) -> tuple | None:
    bg = np.array(cfg.board_bg_bgr, int)
    mask = (np.abs(img.astype(int) - bg).sum(2) < cfg.board_bg_tolerance).astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask)
    if n < 2:
        return None
    i = int(np.argmax(stats[1:, 4])) + 1
    x, y, w, h, area = stats[i]
    H, W = img.shape[:2]
    if area < 0.03 * H * W or w < 0.5 * W:
        return None
    return int(x), int(y), int(w), int(h)


def _period(profile: np.ndarray, lo: int, hi: int) -> float:
    p = profile - profile.mean()
    ac = np.correlate(p, p, "full")[len(p) - 1:]
    if ac[0] <= 0:
        return 0.0
    ac = ac / ac[0]
    hi = min(hi, len(ac) - 1)
    seg = ac[lo:hi]
    if len(seg) < 3:
        return 0.0
    thr = 0.6 * seg.max()
    k = None
    for j in range(1, len(seg) - 1):
        if seg[j] >= thr and seg[j] >= seg[j - 1] and seg[j] >= seg[j + 1]:
            k = lo + j
            break
    if k is None:
        return 0.0
    # affine la période grâce aux multiples (précision sub-pixel)
    best = float(k)
    for mult in (4, 8):
        a, b = int((k - 1) * mult), int((k + 1) * mult) + 1
        if b < len(ac):
            best = (a + int(np.argmax(ac[a:b]))) / mult
    return best


def _phase(profile: np.ndarray, period: float) -> float:
    best_s, best_o = -1.0, 0.0
    for o in np.arange(0, period, 0.5):
        idx = np.arange(o, len(profile), period).astype(int)
        s = profile[idx].mean()
        if s > best_s:
            best_s, best_o = s, o
    return float(best_o)


def read_picture(img: np.ndarray, cfg: Config) -> Picture | None:
    rect = find_board(img, cfg)
    if rect is None:
        return None
    x, y, w, h = rect
    roi = img[y:y + h, x:x + w]
    bg = np.array(cfg.board_bg_bgr, float)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(float)
    gx = np.abs(np.diff(gray, axis=1)).sum(0)
    gy = np.abs(np.diff(gray, axis=0)).sum(1)
    px, py = _period(gx, 8, 120), _period(gy, 8, 120)
    if px <= 0 or py <= 0:
        # plateau vide (niveau terminé) ou texture illisible
        return Picture(rect, np.full((0, 0), EMPTY), [], (x, y), (0, 0))
    ox, oy = _phase(gx, px), _phase(gy, py)
    cols = int((w - 2 * ox) // px)          # marge symétrique : ignore les tireurs sur le bord
    rows = int((h - oy) // py)
    r = max(2, int(min(px, py) * 0.12))

    samples, pos = [], []
    for ri in range(rows):
        cy = int(oy + ri * py + py * 0.45)
        for ci in range(cols):
            cx = int(ox + ci * px + px / 2)
            patch = roi[max(0, cy - r):cy + r + 1, max(0, cx - r):cx + r + 1].reshape(-1, 3)
            col = np.median(patch, 0)
            if np.abs(col - bg).sum() >= 40:
                samples.append(col)
                pos.append((ri, ci))

    grid = np.full((rows, cols), EMPTY, int)
    if not samples:
        return Picture(rect, grid, [], (x + ox, y + oy), (px, py))

    labs = cv2.cvtColor(np.array(samples, np.uint8)[None], cv2.COLOR_BGR2LAB)[0].astype(float)
    # regroupement glouton des couleurs
    centers, counts, assign = [], [], []
    for v in labs:
        if centers:
            d = np.linalg.norm(np.array(centers) - v, axis=1)
            k = int(np.argmin(d))
            if d[k] < 18:
                counts[k] += 1
                centers[k] = centers[k] + (v - centers[k]) / counts[k]
                assign.append(k)
                continue
        centers.append(v.copy())
        counts.append(1)
        assign.append(len(centers) - 1)
    # les très petits groupes sont du bruit : on les rattache au groupe le plus proche
    keep = [k for k, c in enumerate(counts) if c >= 3] or list(range(len(centers)))
    remap = {}
    for k in range(len(centers)):
        if k in keep:
            remap[k] = keep.index(k)
        else:
            d = [np.linalg.norm(centers[k] - centers[j]) for j in keep]
            remap[k] = int(np.argmin(d))
    palette = [centers[k] for k in keep]
    for (ri, ci), k in zip(pos, assign):
        grid[ri, ci] = remap[k]
    return Picture(rect, grid, palette, (x + ox, y + oy), (px, py))


# ----------------------------------------------------------------- blocs -----

_ocr_engine = None


def _ocr():
    global _ocr_engine
    if _ocr_engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr_engine = RapidOCR()
    return _ocr_engine


def read_number(crop_bgr: np.ndarray) -> tuple[int | None, str]:
    """Lit le nombre blanc (contour sombre) inscrit sur un bloc."""
    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
    mask = ((hsv[:, :, 1] < 70) & (hsv[:, :, 2] > 170)).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(mask)
    H, W = mask.shape
    parts = []
    for s in st[1:]:
        x, y, w, h, a = s
        touches = x <= 1 or y <= 1 or x + w >= W - 1 or y + h >= H - 1
        if not touches and h > 0.3 * H and a > 80:
            parts.append(s)
    if not parts:
        return None, ""
    x0 = min(p[0] for p in parts); y0 = min(p[1] for p in parts)
    x1 = max(p[0] + p[2] for p in parts); y1 = max(p[1] + p[3] for p in parts)
    pad = 10
    crop = crop_bgr[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad]
    try:
        res = _ocr().text_recognizer([crop])[0]
    except Exception:
        return None, ""
    text = unicodedata.normalize("NFKC", res[0][0]) if res else ""
    digits = re.sub(r"\D", "", text)
    return (int(digits) if digits else None), text


def read_blocks(img: np.ndarray, cfg: Config, ocr: bool = True) -> list[Block]:
    H, W = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hw, hh = int(cfg.block_half_w * W), int(cfg.block_half_h * H)
    rows = [("tray", 0, cfg.tray_y)] + [("grid", i, fy) for i, fy in enumerate(cfg.grid_rows_y)]
    blocks = []
    for zone, ri, fy in rows:
        for ci, fx in enumerate(cfg.column_x):
            cx, cy = int(fx * W), int(fy * H)
            x0, y0 = max(0, cx - hw), max(0, cy - hh)
            region = hsv[y0:cy + hh, x0:cx + hw].reshape(-1, 3).astype(int)
            dark = int((region[:, 2] < 90).sum())
            tappable = dark >= cfg.min_dark_pixels
            b = Block(zone, ri, ci, cx, cy, tappable)
            if tappable:
                # couleur du corps du bloc (zone centrale, sans le blanc ni le contour)
                iw, ih = int(hw * 0.75), int(hh * 0.9)
                body = img[cy - ih:cy + ih, cx - iw:cx + iw].reshape(-1, 3)
                bh = hsv[cy - ih:cy + ih, cx - iw:cx + iw].reshape(-1, 3)
                sel = (bh[:, 1] > 60) & (bh[:, 2] > 80)
                if sel.sum() > 30:
                    b.color_bgr = tuple(int(v) for v in np.median(body[sel], 0))
                if ocr:
                    b.ammo, b.text = read_number(img[y0:cy + hh, x0:cx + hw])
            blocks.append(b)
    return blocks


def match_colors(blocks: list[Block], picture: Picture | None) -> None:
    if picture is None or not picture.palette:
        return
    pal = np.array(picture.palette)
    for b in blocks:
        if b.color_bgr is not None:
            d = np.linalg.norm(pal - bgr_to_lab(b.color_bgr), axis=1)
            k = int(np.argmin(d))
            b.color = k if d[k] < 40 else None


def read_state(img: np.ndarray, cfg: Config, ocr: bool = True) -> GameState:
    pic = read_picture(img, cfg)
    if pic is None:
        return GameState(None, [])
    blocks = read_blocks(img, cfg, ocr=ocr)
    match_colors(blocks, pic)
    return GameState(pic, blocks)


def read_level(img: np.ndarray) -> int | None:
    H = img.shape[0]
    try:
        res, _ = _ocr()(img[: int(H * 0.08)])
    except Exception:
        return None
    for _, text, _ in res or []:
        m = re.search(r"(?:level|niveau)\s*(\d+)", text, re.I)
        if m:
            return int(m.group(1))
    return None


def find_text_buttons(img: np.ndarray) -> list[tuple[str, int, int]]:
    """Toutes les zones de texte de l'écran : (texte en minuscules, x, y)."""
    try:
        res, _ = _ocr()(img)
    except Exception:
        return []
    out = []
    for box, text, _ in res or []:
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        out.append((text.lower().strip(), int(sum(xs) / 4), int(sum(ys) / 4)))
    return out


# --------------------------------------------------------------- debug -------

def annotate(img: np.ndarray, state: GameState, move=None) -> np.ndarray:
    out = img.copy()
    pic = state.picture
    if pic is not None:
        x, y, w, h = pic.rect
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 255), 3)
        ox, oy = pic.origin
        px, py = pic.pitch
        for ri in range(pic.grid.shape[0]):
            for ci in range(pic.grid.shape[1]):
                k = pic.grid[ri, ci]
                if k == EMPTY:
                    continue
                cx, cy = int(ox + ci * px + px / 2), int(oy + ri * py + py * 0.45)
                cv2.circle(out, (cx, cy), 4, lab_to_bgr(pic.palette[k]), -1)
                cv2.circle(out, (cx, cy), 4, (0, 0, 0), 1)
    for b in state.blocks:
        colr = (0, 200, 0) if b.tappable else (128, 128, 128)
        cv2.rectangle(out, (b.x - 80, b.y - 60), (b.x + 80, b.y + 60), colr, 3)
        if b.tappable:
            label = f"{b.ammo if b.ammo is not None else '?'} c{b.color}"
            cv2.putText(out, label, (b.x - 75, b.y + 95), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 5)
            cv2.putText(out, label, (b.x - 75, b.y + 95), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)
    if move is not None:
        cv2.circle(out, (move.block.x, move.block.y), 70, (0, 0, 255), 8)
    return out
