# -*- coding: utf-8 -*-
"""Language-independent CAD layer aliases for international engineering drawings.

Aliases guide suggestions only. The user must confirm the actual CAD layer.
Geometric drainage-area delineation is not modified by this dictionary.
"""
import unicodedata

CAD_KEYWORDS = {
    "divisores": (
        "topographic_divide", "topographic divide", "watershed_divide",
        "drainage_divide", "water_divide", "ridgeline", "ridge_line",
        "crest_line", "crest", "divide", "divisor", "crista",
        "topografico", "topografica", "div_top", "divis", "separ", "limite"
    ),
    "canais": (
        "drainage_channel", "peripheral_channel", "perimeter_channel",
        "surface_drainage", "collector_channel", "channel", "ditch",
        "canal", "canaleta", "perif"
    ),
    "descidas": (
        "downchute", "down_chute", "down chute", "chute",
        "drainage_chute", "stepped_chute", "spillway_chute",
        "descida", "descida_agua", "queda", "down"
    ),
    "fluxo": ("flow_direction", "flow_arrow", "direction_of_flow", "flow", "arrow", "sentido", "fluxo", "seta"),
    "limite": ("outer_boundary", "boundary_line", "outer_limit", "boundary", "offset", "edge", "margin", "limite", "borda", "crista", "margem"),
}

def normalize_cad_name(value):
    text = unicodedata.normalize("NFKD", str(value or "").casefold())
    return "".join(ch for ch in text if not unicodedata.combining(ch))

def default_aliases(category, lang='en_US'):
    """English-first display even with Brazilian aliases retained for recognition."""
    aliases = CAD_KEYWORDS[category]
    if lang == 'pt_BR':
        portuguese = ('divisor', 'crista', 'canal', 'canaleta', 'descida', 'queda', 'dren', 'perif', 'topografico')
        aliases = tuple(sorted(aliases, key=lambda v: (not v.startswith(portuguese), aliases.index(v))))
    return ','.join(aliases)

def contains_alias(name, aliases):
    n = normalize_cad_name(name)
    return any(normalize_cad_name(alias).strip() in n for alias in aliases if alias and alias.strip())
