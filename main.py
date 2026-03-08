# -*- coding: utf-8 -*-
"""
AeroPKG — PS4 Package Viewer.

Desktop application to read and display metadata from PS4 .pkg files.

Usage:
    python main.py

Auteur : PS4 Package Viewer
Licence : MIT
"""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from PyQt6.QtCore import Qt

from main_window import MainWindow


def charger_police_roboto(app: QApplication):
    """
    Charge la police Roboto depuis les fichiers système ou utilise
    une police sans-serif de substitution.

    La police Roboto est la plus proche de la police "SST" utilisée
    par Sony dans l'interface de la PlayStation 4.

    Args:
        app: Instance de l'application Qt
    """
    # Tentative de chargement de Roboto si installée sur le système
    polices_candidates = [
        "Roboto",
        "Segoe UI",       # Police Windows moderne (fallback)
        "SF Pro Display",  # macOS (fallback)
        "Noto Sans",       # Linux (fallback)
    ]

    police_choisie = None
    for nom_police in polices_candidates:
        # Vérifier si la police est disponible
        families = QFontDatabase.families()
        if nom_police in families:
            police_choisie = nom_police
            break

    if police_choisie is None:
        police_choisie = "Segoe UI"  # Fallback universel Windows

    # Appliquer la police globalement
    font = QFont(police_choisie, 11)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    return police_choisie


def main():
    """Point d'entrée principal de l'application."""
    # ── Paramètres d'environnement ──
    # Activer le support du High DPI
    os.environ.setdefault('QT_ENABLE_HIGHDPI_SCALING', '1')

    # ── Création de l'application ──
    app = QApplication(sys.argv)
    app.setApplicationName("FlowPKG")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AeroPKG")

    # ── App icon ──
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path_new = os.path.join(base_dir, 'pkg-removebg-preview.ico')
    icon_path_v1 = os.path.join(base_dir, 'icon_v1.png')
    icon_path_default = os.path.join(base_dir, 'icon.png')

    if os.path.exists(icon_path_new):
        app.setWindowIcon(QIcon(icon_path_new))
    elif os.path.exists(icon_path_v1):
        app.setWindowIcon(QIcon(icon_path_v1))
    elif os.path.exists(icon_path_default):
        app.setWindowIcon(QIcon(icon_path_default))

    # ── Chargement de la police ──
    police = charger_police_roboto(app)
    print(f"[INFO] Police utilisée : {police}")

    # ── Style global ──
    app.setStyle("Fusion")  # Style Fusion pour un rendu cohérent

    # ── Création et affichage de la fenêtre ──
    fenetre = MainWindow()
    fenetre.show()

    # ── Load file from command-line argument ("Open with...") ──
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.isfile(filepath) and filepath.lower().endswith('.pkg'):
            fenetre._load_pkg(filepath)

    # ── Event loop ──
    code_retour = app.exec()
    sys.exit(code_retour)


if __name__ == "__main__":
    main()
