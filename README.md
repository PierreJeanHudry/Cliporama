# Cliporama

Programme de création d'une animation à partir d'un fichier srt et d'un fichier mp3 associés.

Réalisé dans le cadre du module PRO3600.

## Problème d'absence de son

Mettre à jour jdk

```
Version fonctionnelle : jdk1.8.0_171
```

## Informations sur le programme

* Api Key Giphy créée avec le compte yopmail biket@yopmail.com: Fxe6Ib7RS60Vx30kVKbD5UpXlOarp3dR

* La librairie giphy4j interroge giphy mais dépend de plusieurs autres librairies à inclure en faisant sur les 4:

```
* clic droit sur la librairie
* Build Path
* Configure Build Path
* Add .jar
* Se balader dans les dossiers
* pour nous: Projet --> PRO3600/git/PRO3600-18-LAL-12/lib
```
		
* Pour changer le fond du clip : Changer le gif dans PRO3600/git/PRO3600-18-LAL-12/data/fond/fond.gif en gardant bien le même nom

* Temps de chargement important au démarrage dû au redimenssionnement de toutes les images/gifs

## Pour lancer une musique de son choix

Il faut télécharger un fichier mp3 et un fichier srt pour un même audio:

```
* Choisir une chanson anglaise
* Vérifier sur http://www.rentanadviser.com/en/subtitles qu'il y ait bien les sous-titres pour la même version de la chanson
* Selectionner la chanson sur Youtube via le site précédent
* Ouvrir un terminal
* Taper "youtube-dl -x --audio-format mp3 *url_youtube*"
```
											
## JUnit
										
Pour pouvoir utiliser JUnit 4

```
* clic droit sur le projet
* build path
* add libraries
* selectionner JUnit
```

## Pour gérer les problèmes de Java Heap Space

La gestion de beaucoup de Gifs et/ou d'images peut demander à la machine beaucoup de mémoire pour arriver à tout gérer.
On va donc augmenter la capacité allouée à eclipse en faisant une nouvelle configuration de lancement:

```
* Ouvrir le menu déroulant du bouton Run
* Run configurations
* Onglet "Arguments"
* VM Arguments
* Coller "-Xmx3g" (3g correspond à 3Giga octets de mémoire, cette valeur peut-être changé en fonction des besoins)
```

## Pour Eclipse et GitLab

Utiliser : https://gitlab.tem-tsp.eu/alexandre.dupuy-zini/PRO3600-18-LAL-12.git
