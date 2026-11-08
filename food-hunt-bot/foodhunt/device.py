"""Accès au téléphone Android via ADB (captures d'écran et taps)."""
from __future__ import annotations

import subprocess

import cv2
import numpy as np


class AdbError(RuntimeError):
    pass


class Device:
    def __init__(self, adb_path: str = "adb", serial: str = ""):
        self.adb = adb_path
        self.serial = serial

    def _cmd(self, *args: str) -> list[str]:
        base = [self.adb]
        if self.serial:
            base += ["-s", self.serial]
        return base + list(args)

    def _run(self, *args: str, timeout: float = 15) -> bytes:
        try:
            out = subprocess.run(self._cmd(*args), capture_output=True, timeout=timeout)
        except FileNotFoundError as e:
            raise AdbError(f"adb introuvable ({self.adb}). Installe les platform-tools Android "
                           "ou renseigne adb_path dans config.json.") from e
        if out.returncode != 0:
            raise AdbError(out.stderr.decode(errors="replace").strip() or "erreur adb")
        return out.stdout

    def check(self) -> str:
        lines = self._run("devices").decode().strip().splitlines()[1:]
        devs = [l.split()[0] for l in lines if l.strip().endswith("device")]
        if not devs:
            raise AdbError("Aucun téléphone détecté. Active le débogage USB et accepte "
                           "l'autorisation sur le téléphone.")
        if self.serial and self.serial not in devs:
            raise AdbError(f"Appareil {self.serial} absent. Trouvés : {devs}")
        return self.serial or devs[0]

    def screenshot(self) -> np.ndarray:
        png = self._run("exec-out", "screencap", "-p")
        img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise AdbError("Capture d'écran illisible.")
        return img

    def tap(self, x: int, y: int) -> None:
        self._run("shell", "input", "tap", str(int(x)), str(int(y)))
