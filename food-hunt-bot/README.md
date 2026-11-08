# Bot Food Hunt (Pixel Puzzle)

Bot qui joue tout seul à **Food Hunt: Pixel Puzzle** sur un téléphone **Android**, piloté
depuis un **PC Windows** via ADB (câble USB ou Wi-Fi).

Toutes les une à deux secondes, il :
1. prend une capture d'écran du téléphone ;
2. lit l'image en pixels (grille, couleurs) et les blocs tireurs : munitions (chiffre lu
   par OCR), couleur, bloc jouable ou grisé, file d'attente des 5 places ;
3. simule le tour de tapis de chaque tireur possible et choisit le meilleur coup.
   Il privilégie les tireurs qui vident toutes leurs munitions et évite de remplir la
   file d'attente ;
4. touche le bloc, attend la fin de l'animation, puis recommence ;
5. entre deux niveaux, touche les boutons « Next / Continue / Suivant… ». Il ne touche
   jamais un bouton d'achat, de pièces ou de pub.

## Installation (une seule fois)

1. **Sur le téléphone** :
   - Paramètres → À propos → touche 7 fois « Numéro de build » ;
   - Paramètres → Options pour les développeurs → active **Débogage USB** ;
   - active aussi « Débogage USB (paramètres de sécurité) » si ton téléphone le propose
     (Xiaomi). Sans ça, les taps ne marchent pas.
2. **Sur le PC** :
   - installe [Python 3.10+](https://www.python.org/downloads/) en cochant « Add to PATH » ;
   - télécharge les [Android platform-tools](https://developer.android.com/tools/releases/platform-tools)
     et dézippe-les, par exemple dans `C:\platform-tools` ;
   - copie ce dossier `food-hunt-bot` sur le PC.
3. Si `adb` n'est pas dans le PATH, crée `config.json` dans ce dossier :
   ```json
   { "adb_path": "C:\\platform-tools\\adb.exe" }
   ```
4. Branche le téléphone et accepte l'autorisation « Autoriser le débogage USB ».

## Utilisation

Ouvre le jeu sur un niveau, puis double-clique sur **`lancer_bot.bat`**.
Pour arrêter : `Ctrl+C` dans la fenêtre.

Ligne de commande (dans le dossier, après la première installation) :

```
.venv\Scripts\python -m foodhunt run                 # joue sans fin
.venv\Scripts\python -m foodhunt run --levels 10     # 10 niveaux puis arrêt
.venv\Scripts\python -m foodhunt run --dry-run       # affiche le coup prévu sans toucher
.venv\Scripts\python -m foodhunt run --debug         # enregistre chaque analyse dans debug\
.venv\Scripts\python -m foodhunt screenshot          # capture du téléphone -> debug\capture.png
.venv\Scripts\python -m foodhunt analyze image.png   # analyse une capture (image annotée)
.venv\Scripts\python -m foodhunt init-config         # crée config.json avec tous les réglages
```

**Sans câble (Wi-Fi, Android 11+)** : Options pour les développeurs → Débogage sans fil →
« Associer avec un code », puis tape `adb pair IP:PORT` et `adb connect IP:PORT`.
Le téléphone peut ensuite jouer seul tant que le PC est allumé.

## Quand le bot s'arrête ou se trompe

- **« Aucun coup sûr »** : la file d'attente est pleine, ou aucune couleur jouable n'est
  accessible sur le bord de l'image. Utilise un bonus à la main ; le bot reprend tout seul.
- **« Écran non reconnu »** : une pub ou une fenêtre inconnue est affichée. Ferme-la à la
  main. Une capture est enregistrée dans `debug\`.
- **Mauvais bloc touché** : lance `run --debug` et envoie-moi les images de `debug\`.
  Les positions des blocs (`column_x`, `tray_y`, `grid_rows_y`) sont réglées pour un écran
  1440x3120 et se modifient dans `config.json`.

Conseil : active la vitesse **3x** dans le jeu, le bot ira 3 fois plus vite.

## Tests

```
python -m pytest tests
```

Les tests vérifient la lecture de `samples/level257.jpg` et la stratégie.

⚠️ Automatiser un jeu peut être contraire à ses conditions d'utilisation. Utilise ce bot
à tes risques.
