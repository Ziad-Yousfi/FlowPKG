# -*- coding: utf-8 -*-
"""
Module de parsing binaire des fichiers .pkg de la PlayStation 4.

OPTIMISÉ : Utilise des lectures ciblées (seek + read) au lieu de charger
le fichier entier en mémoire. Les fichiers PKG peuvent faire 20-50 GB,
seuls les headers, la table d'entrées et les fichiers internes nécessaires
(param.sfo ~1Ko, icon0.png ~50Ko) sont lus.
"""

import struct
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, BinaryIO

from sfo_parser import SFOParser, SFOError, detect_region, get_category_name


# ─── Constantes ───────────────────────────────────────────────────────────────

PKG_MAGIC = b'\x7FCNT'

# IDs des entrées dans la table du PKG
ENTRY_ID_PARAM_SFO = 0x1000
ENTRY_ID_ICON0_PNG = 0x1200


# ─── Classes de données ──────────────────────────────────────────────────────

@dataclass
class PKGEntry:
    """Représente une entrée dans la table des fichiers du PKG."""
    entry_id: int
    filename_offset: int
    flags1: int
    flags2: int
    data_offset: int
    data_size: int


@dataclass
class PKGInfo:
    """Contient toutes les informations extraites d'un fichier PKG."""
    # Header
    pkg_type: int = 0
    pkg_file_count: int = 0
    pkg_entry_count: int = 0
    pkg_table_offset: int = 0
    content_id: str = ""
    content_type: int = 0
    file_size: int = 0

    # Données extraites
    sfo_params: Dict[str, Any] = field(default_factory=dict)
    icon_data: Optional[bytes] = None

    # Informations dérivées
    title: str = ""
    title_id: str = ""
    region: str = ""
    app_version: str = ""
    firmware_version: str = ""
    category: str = ""
    category_name: str = ""
    is_fake_pkg: bool = False  # FPKG ou PKG officiel


class PKGError(Exception):
    """Exception levée lors d'une erreur de parsing du fichier PKG."""
    pass


# ─── Parseur PKG (lecture streaming) ─────────────────────────────────────────

class PKGParser:
    """
    Parseur de fichiers .pkg PS4 — version optimisée.
    Ne lit que les octets nécessaires (header + table + param.sfo + icon0).
    """

    def __init__(self):
        self._sfo_parser = SFOParser()

    def parse(self, filepath: str) -> PKGInfo:
        """Parse un fichier PKG par lectures ciblées (seek + read)."""
        try:
            with open(filepath, 'rb') as f:
                # Taille du fichier (sans tout lire)
                f.seek(0, 2)
                file_size = f.tell()
                f.seek(0)

                if file_size < 0x100:
                    raise PKGError("File too small to be a valid PKG.")

                return self._parse_streaming(f, file_size)
        except IOError as e:
            raise PKGError(f"Unable to read file: {e}")

    def _parse_streaming(self, f: BinaryIO, file_size: int) -> PKGInfo:
        """Parse le PKG en ne lisant que les parties nécessaires."""
        info = PKGInfo(file_size=file_size)

        # ── Header (lire seulement les 256 premiers octets) ──
        f.seek(0)
        header = f.read(256)

        if header[:4] != PKG_MAGIC:
            raise PKGError(
                f"Invalid PKG magic: {header[:4].hex()} "
                f"(expected: {PKG_MAGIC.hex()} = \\x7FCNT)"
            )

        info.pkg_type = struct.unpack_from('>H', header, 0x006)[0]
        info.pkg_file_count = struct.unpack_from('>I', header, 0x00C)[0]
        info.pkg_entry_count = struct.unpack_from('>I', header, 0x010)[0]
        info.pkg_table_offset = struct.unpack_from('>I', header, 0x018)[0]

        # Content ID (offset 0x40, 36 octets)
        info.content_id = header[0x40:0x40 + 36].split(b'\x00')[0].decode(
            'utf-8', errors='replace'
        )

        # Content Type (offset 0x74)
        if len(header) >= 0x78:
            info.content_type = struct.unpack_from('>I', header, 0x074)[0]

        # ── Détection FPKG (Fake PKG) ──
        # Les FPKG utilisent souvent le type 0x02 (revision debug/fake)
        pkg_revision = struct.unpack_from('>H', header, 0x004)[0]
        # Les PKG retail ont revision 0x8000+, les FPKG typiquement 0x0001-0x0002
        info.is_fake_pkg = (pkg_revision & 0x8000) == 0

        # ── Lecture de la table d'entrées ──
        table_offset = info.pkg_table_offset
        entry_count = info.pkg_entry_count

        if table_offset == 0 or entry_count == 0:
            table_offset = 0x2B30 if file_size > 0x2B50 else 0
            entry_count = min(info.pkg_file_count, 50) if info.pkg_file_count > 0 else 50

        # Lire toute la table d'entrées d'un coup (32 octets × N entrées)
        table_size = entry_count * 32
        if table_offset + table_size > file_size:
            table_size = min(table_size, file_size - table_offset)

        f.seek(table_offset)
        table_data = f.read(table_size)

        # ── Trouver param.sfo et icon0.png dans la table ──
        sfo_entry = None
        icon_entry = None

        for i in range(entry_count):
            pos = i * 32
            if pos + 24 > len(table_data):
                break

            entry_id, fn_offset, flags1, flags2, d_offset, d_size = struct.unpack_from(
                '>IIIIII', table_data, pos
            )

            if entry_id == ENTRY_ID_PARAM_SFO:
                sfo_entry = PKGEntry(entry_id, fn_offset, flags1, flags2, d_offset, d_size)
            elif entry_id == ENTRY_ID_ICON0_PNG:
                icon_entry = PKGEntry(entry_id, fn_offset, flags1, flags2, d_offset, d_size)

            # Dès qu'on a les deux, on arrête
            if sfo_entry and icon_entry:
                break

        # ── Lire param.sfo (typiquement ~1 Ko) ──
        if sfo_entry and sfo_entry.data_size > 0:
            if sfo_entry.data_offset + sfo_entry.data_size <= file_size:
                f.seek(sfo_entry.data_offset)
                sfo_data = f.read(sfo_entry.data_size)
                try:
                    info.sfo_params = self._sfo_parser.parse(sfo_data)
                except SFOError as e:
                    raise PKGError(f"param.sfo parse error: {e}")

                info.title = info.sfo_params.get('TITLE', 'Unknown title')
                info.title_id = info.sfo_params.get('TITLE_ID', '')
                info.app_version = info.sfo_params.get('APP_VER', '')
                info.category = info.sfo_params.get('CATEGORY', '')
                info.category_name = get_category_name(info.category)

                fw = info.sfo_params.get('SYSTEM_VER', '')
                info.firmware_version = str(fw) if fw else ''

                cid = info.sfo_params.get('CONTENT_ID', info.content_id)
                if cid:
                    info.content_id = cid

        info.region = detect_region(info.content_id)

        # ── Lire icon0.png (typiquement ~50 Ko) ──
        if icon_entry and icon_entry.data_size > 0:
            if icon_entry.data_offset + icon_entry.data_size <= file_size:
                f.seek(icon_entry.data_offset)
                info.icon_data = f.read(icon_entry.data_size)

        return info


# ─── Fonctions utilitaires ───────────────────────────────────────────────────

def format_content_type(content_type: int) -> str:
    """Convertit un code de type de contenu en description lisible."""
    types = {
        0x1A: 'Full Game',
        0x1B: 'Update (Patch)',
        0x1C: 'DLC',
        0x01: 'Game Data',
        0x04: 'Application',
        0x09: 'PS4 Theme',
    }
    return types.get(content_type, f"Type 0x{content_type:02X}")


def format_file_size(size_bytes: int) -> str:
    """Formate une taille de fichier en unité lisible."""
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} Ko"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} Mo"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} Go"
