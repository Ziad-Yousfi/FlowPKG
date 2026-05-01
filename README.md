AeroPKG (FlowPKG) — PS4 Package Viewer
<details open> <summary><strong>English</strong></summary>
AeroPKG (also known internally as FlowPKG) is a fluid and modern desktop application designed to analyze and display metadata from PlayStation 4 .pkg files.

Featuring a sleek graphical interface (heavily inspired by the PS4 UI aesthetic) built with PyQt6, AeroPKG instantly extracts critical information without loading entire massive files into memory.

✨ Features
Optimized (Streaming) reading: Uses targeted file reads (seek + read) to instantly process PKG files over 50GB without saturating RAM.
Detailed param.sfo metadata extraction:
Game title (TITLE) and Title ID (TITLE_ID)
App version and minimum required firmware version
Region code (CUSA, etc.)
Category and content type (Full game, Patch, DLC, Theme, etc.)
FPKG detection: Automatically determines whether the package is an official PKG or a homebrew/dump Fake PKG (FPKG).
Icon extraction: Smartly loads and displays the internal icon0.png image from the package.
Windows Explorer integration: Integrates directly into the Windows context menu ("Open with AeroPKG") via the provided .reg files.
"PS4-Style" interface: A polished UI with smooth animations, using the Roboto font (to replicate Sony’s SST style) and an immersive dark/blue theme.
🛠️ Requirements & Installation
Dependencies
AeroPKG runs on Python 3 and requires a few libraries listed in requirements.txt:

PyQt6 >= 6.5.0 (GUI framework)
Pillow >= 10.0.0 (Image manipulation and conversion)
Run with Python
Clone this repository:
bash
git clone https://github.com/votre_pseudo/AeroPKG.git
cd AeroPKG
Install dependencies:
bash
pip install -r requirements.txt
Run the program:
bash
python main.py
(You can also drag & drop a .pkg file onto the window or pass it as a command-line argument: python main.py path/to/game.pkg)
📦 Build a Standalone Executable (.exe)
You can compile this Python project into a standalone Windows executable:

Install PyInstaller: pip install pyinstaller
Build using the provided spec file:
bash
pyinstaller AeroPKG.spec
The working executable will be located in the dist\ folder.
Windows context menu ("Open with...")
If you use the compiled version, you can easily add AeroPKG to the Windows right-click menu:

Double-click install_context_menu.reg (open it first in a text editor and adjust paths to dist/AeroPKG.exe for your machine).
To uninstall this context menu integration, use uninstall_context_menu.reg.
📂 Code Architecture
main.py: Application entry point (DPI scaling, Qt configuration, font loading).
main_window.py: Main window logic and style (qss).
pkg_parser.py: Core optimized binary parsing of the .pkg header and entry table.
sfo_parser.py: Dedicated module to parse the internal SFO format to extract raw text and metadata.
📝 License
This project is distributed under the MIT license. Feel free to study it, modify it, and share it.

</details> <details> <summary><strong>Français</strong></summary>
AeroPKG (également connu sous le nom interne de FlowPKG) est une application de bureau fluide et moderne permettant d'analyser et d'afficher les métadonnées des fichiers .pkg de PlayStation 4.

Doté d'une interface graphique élégante (fortement inspirée de l'esthétique et de l'interface utilisateur de la PS4) utilisant PyQt6, AeroPKG parvient à extraire instantanément les informations critiques sans avoir à charger l'intégralité des fichiers massifs en mémoire.

✨ Fonctionnalités
Lecture optimisée (Streaming) : Utilise des lectures ciblées dans les fichiers (seek + read) pour traiter instantanément les fichiers PKG de plus de 50 Go sans saturer la RAM.
Extraction détaillée des métadonnées param.sfo :
Titre du jeu (TITLE) et Identifiant de titre (TITLE_ID)
Version de l'application et version minimale de Firmware requise
Code de région (CUSA, etc.)
Catégorie et Type de Contenu (Jeu complet, Patch, DLC, Thème, etc.)
Détection FPKG : Détermine automatiquement si le paquet est un PKG officiel ou un Fake PKG (FPKG) homebrew/dump.
Extraction d'icône : Charge et affiche intelligemment l'image interne icon0.png du paquet.
Intégration Windows Explorer : S'intègre directement au menu contextuel de Windows ("Ouvrir avec AeroPKG") via les fichiers de registre .reg fournis.
Interface "PS4-Style" : Une UI soignée dotée d'animations fluides, utilisant la police Roboto (pour répliquer le style SST de Sony) et un mode sombre/bleuté immersif.
🛠️ Prérequis et Installation
Dépendances
AeroPKG fonctionne sous Python 3 et requiert quelques bibliothèques listées dans requirements.txt:

PyQt6 >= 6.5.0 (Framework d'interface graphique)
Pillow >= 10.0.0 (Manipulation et conversion d'images)
Lancer via Python
Clonez ce dépôt sur votre machine :
bash
git clone https://github.com/votre_pseudo/AeroPKG.git
cd AeroPKG
Installez les dépendances nécessaires :
bash
pip install -r requirements.txt
Lancez le programme :
bash
python main.py
(Vous pouvez également glisser/déposer un fichier .pkg sur la fenêtre ou le passer en argument de ligne de commande : python main.py chemin/vers/le/jeu.pkg)
📦 Compilation en Exécutable Standalone (.exe)
Vous pouvez compiler ce projet Python en un exécutable simple pour Windows :

Installez PyInstaller : pip install pyinstaller
Lancez le build avec le fichier Spec fourni :
bash
pyinstaller AeroPKG.spec
L'exécutable fonctionnel se trouvera dans le dossier dist\.
Menu contextuel Windows ("Ouvrir avec...")
Si vous utilisez la version compilée, vous pouvez ajouter facilement AeroPKG à votre menu de clic droit sur Windows :

Double-cliquez sur install_context_menu.reg (assurez-vous d'abord de l'ouvrir dans un éditeur de texte et d'adapter les chemins vers dist/AeroPKG.exe selon votre ordinateur).
Pour désinstaller cette intégration contextuelle, utilisez uninstall_context_menu.reg.
📂 Architecture du Code
main.py : Point d'entrée de l'application (DPI Scaling, configuration Qt, chargement de polices).
main_window.py : Logique et style (qss) de la fenêtre principale.
pkg_parser.py : Le cœur du parsing binaire et optimisé du header .pkg et de sa table d'entrées.
sfo_parser.py : Module dédié au parsing du format SFO interne pour extraire le texte brut et les métadonnées.
📝 Licence
Ce projet est distribué sous la licence MIT. N'hésitez pas à l'étudier, le modifier et le partager.

</details>
