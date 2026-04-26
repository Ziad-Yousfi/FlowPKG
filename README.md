# AeroPKG (FlowPKG) — PS4 Package Viewer

AeroPKG (also known internally as FlowPKG) is a smooth, modern desktop application for parsing and displaying the metadata of PlayStation 4 `.pkg` files.

Featuring an elegant GUI (heavily inspired by the PS4 aesthetic and UI) built with PyQt6, AeroPKG can instantly extract critical information without having to load massive files entirely into memory.

## ✨ Features

* **Optimized Reading (Streaming)**: Uses targeted file reads (seek + read) to instantly process PKG files larger than 50 GB without saturating RAM.
* **Detailed `param.sfo` metadata extraction**:
  * Game title (`TITLE`) and Title ID (`TITLE_ID`)
  * Application version and minimum required Firmware version
  * Region code (CUSA, etc.)
  * Category and Content Type (Full game, Patch, DLC, Theme, etc.)
* **FPKG Detection**: Automatically determines whether the package is an official PKG or a Fake PKG (FPKG) homebrew/dump.
* **Icon Extraction**: Intelligently loads and displays the internal `icon0.png` image from the package.
* **Windows Explorer Integration**: Integrates directly into the Windows context menu ("Open with AeroPKG") via the provided `.reg` registry files.
* **"PS4-Style" Interface**: A polished UI with smooth animations, using the *Roboto* font (to replicate Sony's SST style) and an immersive dark/bluish theme.

## 🛠️ Prerequisites & Installation

### Dependencies

AeroPKG runs on Python 3 and requires a few libraries listed in `requirements.txt`:
* `PyQt6` >= 6.5.0 (GUI framework)
* `Pillow` >= 10.0.0 (Image manipulation and conversion)

### Running via Python

1. Clone this repository:
   ```bash
   git clone https://github.com/Ziad-Yousfi/FlowPKG.git
   cd FlowPKG
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   python main.py
   ```
   *(You can also drag and drop a `.pkg` file onto the window, or pass it as a command-line argument: `python main.py path/to/game.pkg`)*

## 📦 Compiling to a Standalone Executable (.exe)

You can compile this Python project into a single executable for Windows:

1. Install PyInstaller: `pip install pyinstaller`
2. Run the build using the provided Spec file:
   ```bash
   pyinstaller AeroPKG.spec
   ```
3. The functional executable will be located in the `dist\` folder.

### Windows Context Menu ("Open with…")

If you are using the compiled version, you can easily add AeroPKG to your Windows right-click menu:

1. Double-click `install_context_menu.reg` (make sure to open it in a text editor first and adjust the paths to `dist/AeroPKG.exe` for your machine).
2. To uninstall this context menu integration, use `uninstall_context_menu.reg`.

## 📂 Code Architecture

* `main.py`: Application entry point (DPI Scaling, Qt configuration, font loading).
* `main_window.py`: Logic and style (qss) of the main window.
* `pkg_parser.py`: The core of the optimised binary parsing of the `.pkg` header and its entry table.
* `sfo_parser.py`: Module dedicated to parsing the internal SFO format to extract raw text and metadata.

## 📝 License

This project is distributed under the **MIT** license. Feel free to study, modify, and share it.

---

<details>
<summary>🇫🇷 Lire en français / Read in French</summary>

# AeroPKG (FlowPKG) — Lecteur de Paquets PS4

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
   git clone https://github.com/Ziad-Yousfi/FlowPKG.git
   cd FlowPKG
   ```
2. Installez les dépendances nécessaires :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancez le programme :
   ```bash
   python main.py
   ```
   *(Vous pouvez également glisser/déposer un fichier `.pkg` sur la fenêtre ou le passer en argument de ligne de commande : `python main.py chemin/vers/le/jeu.pkg`)*

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

</details>
