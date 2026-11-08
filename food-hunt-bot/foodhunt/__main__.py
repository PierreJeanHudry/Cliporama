"""Point d'entrée : python -m foodhunt <commande>."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2


def main(argv=None) -> int:
    from .config import Config

    ap = argparse.ArgumentParser(prog="foodhunt", description="Bot automatique pour Food Hunt (Android, ADB).")
    ap.add_argument("--config", default="config.json", help="fichier de réglages (optionnel)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="jouer automatiquement")
    r.add_argument("--levels", type=int, default=0, help="nombre de niveaux à jouer (0 = sans fin)")
    r.add_argument("--dry-run", action="store_true", help="analyse l'écran et affiche le coup sans toucher")
    r.add_argument("--debug", action="store_true", help="enregistre chaque analyse dans debug/")

    a = sub.add_parser("analyze", help="analyser une capture d'écran (image)")
    a.add_argument("image")
    a.add_argument("--out", default=None, help="image annotée en sortie")

    sub.add_parser("screenshot", help="enregistrer une capture du téléphone")
    sub.add_parser("init-config", help="créer config.json avec les valeurs par défaut")

    args = ap.parse_args(argv)
    cfg = Config.load(args.config)

    if args.cmd == "init-config":
        cfg.dump(args.config)
        print(f"Créé : {args.config}")
        return 0

    if args.cmd == "analyze":
        from .strategy import choose_move
        from .vision import annotate, read_level, read_state
        img = cv2.imread(args.image)
        if img is None:
            print("Image illisible :", args.image)
            return 1
        state = read_state(img, cfg)
        print("Niveau :", read_level(img))
        if state.picture is None:
            print("Pas de tableau détecté sur cette image.")
            return 0
        p = state.picture
        print(f"Tableau : {p.grid.shape[1]}x{p.grid.shape[0]} cases, {p.remaining} pixels, {len(p.palette)} couleurs")
        for b in state.blocks:
            if b.tappable:
                print(f"  {b.zone:5s} col {b.col + 1}: munitions={b.ammo} couleur={b.color}")
        move = choose_move(state, cfg)
        if move:
            print(f"Coup conseillé : bloc {move.block.ammo} ({move.block.zone}, col {move.block.col + 1}) "
                  f"→ détruit {move.destroyed}, reste {move.leftover}")
        else:
            print("Aucun coup sûr trouvé.")
        out = args.out or str(Path(args.image).with_suffix("")) + "-analyse.jpg"
        cv2.imwrite(out, annotate(img, state, move))
        print("Image annotée :", out)
        return 0

    from .bot import Bot
    from .device import AdbError, Device
    try:
        if args.cmd == "screenshot":
            dev = Device(cfg.adb_path, cfg.device_serial)
            dev.check()
            Path(cfg.debug_dir).mkdir(exist_ok=True)
            out = Path(cfg.debug_dir) / "capture.png"
            cv2.imwrite(str(out), dev.screenshot())
            print("Capture :", out)
            return 0
        Bot(cfg, dry_run=args.dry_run, save_debug=args.debug).run(max_levels=args.levels)
    except AdbError as e:
        print("Erreur ADB :", e)
        return 2
    except KeyboardInterrupt:
        print("\nArrêt demandé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
