# AeroPKG (FlowPKG) — PS4 Package Viewer

AeroPKG (également connu sous le nom interne de FlowPKG) est une application de bureau fluide et moderne permettant d'analyser et d'afficher les métadonnées des fichiers `.pkg` de PlayStation 4. 

Doté d'une interface graphique élégante (fortement inspirée de l'esthétique et de l'interface utilisateur de la PS4) utilisant PyQt6, AeroPKG parvient à extraire instantanément les informations critiques sans avoir à charger l'intégralité des fichiers massifs en mémoire.

## ✨ Fonctionnalités

* **Lecture optimisée (Streaming)** : Utilise des lectures ciblées dans les fichiers (seek + read) pour traiter instantanément les fichiers PKG de plus de 50 Go sans saturer la RAM.
* **Extraction détaillée des métadonnées `param.sfo`** :
  * Titre du jeu (`TITLE`) et Identifiant de titre (`TITLE_ID`)
  * Version de l'application et version minimale de Firmware requise
  * Code de région (CUSA, etc.)
  * Catégorie et Type de Contenu (Jeu complet, Patch, DLC, Thème, etc.)
* **Détection FPKG** : Détermine automatiquement si le paquet est un PKG officiel ou un Fake PKG (FPKG) homebrew/dump.
* **Extraction d'icône** : Charge et affiche intelligemment l'image interne `icon0.png` du paquet.
* **Intégration Windows Explorer** : S'intègre directement au menu contextuel de Windows ("Ouvrir avec AeroPKG") via les fichiers de registre `.reg` fournis.
* **Interface "PS4-Style"** : Une UI soignée dotée d'animations fluides, utilisant la police *Roboto* (pour répliquer le style SST de Sony) et un mode sombre/bleuté immersif.

## 🛠️ Prérequis et Installation

### Dépendances

AeroPKG fonctionne sous Python 3 et requiert quelques bibliothèques listées dans `requirements.txt`:
* `PyQt6` >= 6.5.0 (Framework d'interface graphique)
* `Pillow` >= 10.0.0 (Manipulation et conversion d'images)

### Lancer via Python

1. Clonez ce dépôt sur votre machine :
   ```bash
   git clone https://github.com/votre_pseudo/AeroPKG.git
   cd AeroPKG
   ```
2. Installez les dépendances nécessaires :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancez le programme :
   ```bash
   python main.py
   ```
   *(Vous pouvez également glisser/déposer un fichier .pkg sur la fenêtre ou le passer en argument de ligne de commande : `python main.py chemin/vers/le/jeu.pkg`)*

## 📦 Compilation en Exécutable Standalone (.exe)

Vous pouvez compiler ce projet Python en un exécutable simple pour Windows :

1. Installez PyInstaller : `pip install pyinstaller`
2. Lancez le build avec le fichier Spec fourni :
   ```bash
   pyinstaller AeroPKG.spec
   ```
3. L'exécutable fonctionnel se trouvera dans le dossier `dist\`.

### Menu contextuel Windows ("Ouvrir avec...")

Si vous utilisez la version compilée, vous pouvez ajouter facilement AeroPKG à votre menu de clic droit sur Windows :

1. Double-cliquez sur `install_context_menu.reg` (assurez-vous d'abord de l'ouvrir dans un éditeur de texte et d'adapter les chemins vers `dist/AeroPKG.exe` selon votre ordinateur).
2. Pour désinstaller cette intégration contextuelle, utilisez `uninstall_context_menu.reg`.

## 📂 Architecture du Code

* `main.py` : Point d'entrée de l'application (DPI Scaling, configuration Qt, chargement de polices).
* `main_window.py` : Logique et style (qss) de la fenêtre principale.
* `pkg_parser.py` : Le cœur du parsing binaire et optimisé du header `.pkg` et de sa table d'entrées.
* `sfo_parser.py` : Module dédié au parsing du format SFO interne pour extraire le texte brut et les métadonnées.

## 📝 Licence

Ce projet est distribué sous la licence **MIT**. N'hésitez pas à l'étudier, le modifier et le partager.
