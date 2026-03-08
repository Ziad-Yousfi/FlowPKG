# -*- coding: utf-8 -*-
"""
Module de parsing du format binaire param.sfo (System File Object).

Le fichier param.sfo contient les métadonnées d'un jeu ou d'une application PS4
sous forme de paires clé/valeur (ex: TITLE, CONTENT_ID, APP_VER...).

Structure binaire :
  - Header (20 octets) : magic, version, offsets des tables clé/données, nb entrées
  - Index Table : une entrée par paramètre (16 octets chacune)
  - Key Table : chaînes de caractères null-terminated pour les noms de clés
  - Data Table : valeurs associées aux clés (chaînes UTF-8 ou entiers 32-bit)
"""

import struct
from typing import Dict, Any, Optional


# ─── Constantes ───────────────────────────────────────────────────────────────

SFO_MAGIC = b'\x00PSF'          # Magic bytes identifiant un fichier SFO
SFO_HEADER_SIZE = 20            # Taille du header en octets
SFO_INDEX_ENTRY_SIZE = 16       # Taille d'une entrée d'index

# Types de données SFO
FMT_UTF8_SPECIAL = 0x0004       # Chaîne UTF-8 non null-terminated
FMT_UTF8_STRING = 0x0204        # Chaîne UTF-8 null-terminated
FMT_INT32 = 0x0404              # Entier 32-bit little-endian


# ─── Classes ──────────────────────────────────────────────────────────────────

class SFOError(Exception):
    """Exception levée lors d'une erreur de parsing du fichier SFO."""
    pass


class SFOEntry:
    """Représente une entrée du fichier SFO (une paire clé/valeur)."""

    def __init__(self, key: str, value: Any, fmt: int):
        self.key = key          # Nom de la clé (ex: "TITLE")
        self.value = value      # Valeur associée
        self.fmt = fmt          # Format des données (UTF-8, INT32)

    def __repr__(self) -> str:
        return f"SFOEntry(key={self.key!r}, value={self.value!r})"


class SFOParser:
    """
    Parseur de fichiers param.sfo.

    Utilisation :
        parser = SFOParser()
        params = parser.parse(données_binaires)
        # params = {"TITLE": "Mon Jeu", "CONTENT_ID": "EP0001-CUSA00001_00-...", ...}
    """

    def parse(self, data: bytes) -> Dict[str, Any]:
        """
        Parse les données binaires d'un fichier param.sfo.

        Args:
            data: Données brutes du fichier param.sfo

        Returns:
            Dictionnaire contenant toutes les paires clé/valeur

        Raises:
            SFOError: Si le format est invalide ou les données corrompues
        """
        if len(data) < SFO_HEADER_SIZE:
            raise SFOError("SFO file too small to contain a valid header.")

        # ── Lecture du header ──
        magic = data[0:4]
        if magic != SFO_MAGIC:
            raise SFOError(
                f"Invalid SFO magic: {magic.hex()} (expected: {SFO_MAGIC.hex()})"
            )

        # Version (4 octets), offset table des clés (4), offset table des données (4),
        # nombre d'entrées (4)
        version, key_table_offset, data_table_offset, num_entries = struct.unpack_from(
            '<IIII', data, 4
        )

        # ── Validation basique ──
        if num_entries == 0:
            return {}

        index_table_offset = SFO_HEADER_SIZE
        required_size = index_table_offset + (num_entries * SFO_INDEX_ENTRY_SIZE)
        if len(data) < required_size:
            raise SFOError(
                f"Truncated SFO file: {len(data)} bytes "
                f"(minimum required: {required_size})"
            )

        # ── Lecture des entrées ──
        result: Dict[str, Any] = {}

        for i in range(num_entries):
            entry_offset = index_table_offset + (i * SFO_INDEX_ENTRY_SIZE)

            # Chaque entrée d'index : key_offset (2), fmt (2), data_len (4),
            # data_max_len (4), data_offset (4)
            key_offset, fmt, data_len, data_max_len, data_offset = struct.unpack_from(
                '<HHIII', data, entry_offset
            )

            # ── Extraction de la clé ──
            key_start = key_table_offset + key_offset
            key_end = data.index(b'\x00', key_start)
            key = data[key_start:key_end].decode('utf-8', errors='replace')

            # ── Extraction de la valeur ──
            value_start = data_table_offset + data_offset
            value_end = value_start + data_len

            if value_end > len(data):
                raise SFOError(
                    f"Truncated data for key '{key}' "
                    f"(offset: {value_start}, size: {data_len})"
                )

            raw_value = data[value_start:value_end]
            value = self._decode_value(raw_value, fmt, key)

            result[key] = value

        return result

    def _decode_value(self, raw: bytes, fmt: int, key: str) -> Any:
        """
        Décode une valeur brute selon son format SFO.

        Args:
            raw: Données brutes de la valeur
            fmt: Code de format (UTF-8 string, INT32, etc.)
            key: Nom de la clé (pour le formatage spécial de SYSTEM_VER)

        Returns:
            Valeur décodée (str ou int)
        """
        if fmt == FMT_INT32:
            if len(raw) >= 4:
                value = struct.unpack('<I', raw[:4])[0]
                # Formatage spécial pour SYSTEM_VER (version firmware)
                if key == 'SYSTEM_VER':
                    return self._format_firmware_version(value)
                return value
            return 0

        elif fmt in (FMT_UTF8_STRING, FMT_UTF8_SPECIAL):
            # Suppression des null bytes de fin
            decoded = raw.rstrip(b'\x00').decode('utf-8', errors='replace')
            return decoded

        else:
            # Format inconnu : retour en hexadécimal
            return raw.hex()

    @staticmethod
    def _format_firmware_version(version_int: int) -> str:
        """
        Formate un entier SYSTEM_VER en chaîne de version firmware lisible.

        Ex: 0x05050000 → "5.050" (firmware 5.05)

        Args:
            version_int: Valeur entière du SYSTEM_VER

        Returns:
            Chaîne formatée "X.YZ0"
        """
        if version_int == 0:
            return "0.000"

        major = (version_int >> 24) & 0xFF
        minor = (version_int >> 16) & 0xFF
        patch = (version_int >> 8) & 0xFF

        return f"{major}.{minor:02d}{patch}"


# ─── Fonctions utilitaires ────────────────────────────────────────────────────

def detect_region(content_id: str) -> str:
    """
    Détecte la région du jeu à partir du Content ID.

    Le Content ID commence par un préfixe de 2 lettres indiquant la région :
      - EP = Europe
      - UP = USA
      - JP / JP = Japon
      - HP = Asie (Hong Kong)
      - KP = Corée

    Args:
        content_id: Identifiant de contenu (ex: "EP0001-CUSA00001_00-...")

    Returns:
        Nom de la région ou "Inconnue"
    """
    if not content_id or len(content_id) < 2:
        return "Unknown"

    prefix = content_id[:2].upper()
    regions = {
        'EP': 'Europe (EU)',
        'UP': 'USA (US)',
        'JP': 'Japan (JP)',
        'HP': 'Asia (HK)',
        'KP': 'Korea (KR)',
        'IP': 'Internal',
    }
    return regions.get(prefix, f"Unknown ({prefix})")


def get_category_name(category: str) -> str:
    """
    Convertit le code de catégorie SFO en nom lisible.

    Args:
        category: Code de catégorie (ex: "gd", "gp", "ac")

    Returns:
        Nom lisible de la catégorie
    """
    categories = {
        'gd': 'Game Data',
        'gp': 'Game Patch',
        'ac': 'Additional Content (DLC)',
        'al': 'Application',
        'gpc': 'Game Patch (Cumulative)',
        'gdk': 'Game Data (Dev Kit)',
        'gdl': 'Game Data (Free Location)',
        'gda': 'System Application',
        'gdb': 'System Application (Big)',
    }
    return categories.get(category, f"Unknown ({category})")
