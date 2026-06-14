"""
Universal helper functions: config, pickle, text features, styles.
Author: M. M. Nurhussein, A. B. Pascal
"""

import re
import pickle
import configparser
from typing import Any, Tuple
import os

import pandas as pd
import tkinter as tk
from tkinter import ttk


def load_config(config_path: str = "config.ini") -> configparser.RawConfigParser:
    """Load configuration from .ini file (no interpolation)."""
    config = configparser.RawConfigParser()
    config.read(config_path, encoding='utf-8')
    return config


def save_config(config: configparser.RawConfigParser, config_path: str = "config.ini") -> None:
    """Save configuration to .ini file."""
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)


def load_pickle(filepath: str) -> Any:
    """Load object from pickle file."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def save_pickle(obj: Any, filepath: str) -> None:
    """Save object to pickle file."""
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)


def count_words(text: str) -> int:
    """Return number of words in text."""
    return len(text.split())


def has_url(text: str) -> bool:
    """Check if text contains a URL (http, https, or www)."""
    pattern = r'https?://\S+|www\.\S+'
    return bool(re.search(pattern, text))


def has_phone(text: str) -> bool:
    """Check for a phone number pattern (simplified)."""
    pattern = r'\+?\d[\d\-(). ]{7,}\d'
    return bool(re.search(pattern, text))


def has_exclamation(text: str) -> bool:
    """Return True if '!' is present."""
    return '!' in text


def is_all_caps(text: str) -> bool:
    """
    Check if all alphabetic characters (Latin and Cyrillic) are uppercase.
    Digits and punctuation are ignored.
    """
    letters = re.sub(r'[^a-zA-Zа-яА-Я]', '', text)
    if not letters:
        return False
    return letters.isupper()


def get_font(config: configparser.RawConfigParser, prefix: str = "") -> Tuple[str, int, str]:
    """
    Extract font properties from config and return a tuple (family, size, weight).
    prefix can be "" (general) or "button_" for button-specific settings.
    """
    family = config.get('Interface', prefix + 'font_family', fallback='Calibri Light')
    size = config.getint('Interface', prefix + 'font_size', fallback=12)
    weight = config.get('Interface', prefix + 'font_weight', fallback='normal')
    return (family, size, weight)


def apply_styles(widget, config):
    """
    Apply modern ttk styles to a widget and its children.
    Uses colors and fonts from the config.
    """
    style = ttk.Style()
    style.theme_use('clam')

    bg = config.get('Interface', 'bg_color', fallback='#F0F0F0')
    btn_bg = config.get('Interface', 'button_bg', fallback='#4CAF50')
    btn_fg = config.get('Interface', 'button_fg', fallback='white')

    font_family = config.get('Interface', 'font_family', fallback='Calibri Light')
    font_size = config.getint('Interface', 'font_size', fallback=12)
    btn_font_family = config.get('Interface', 'button_font_family', fallback='Calibri Light')
    btn_font_size = config.getint('Interface', 'button_font_size', fallback=11)
    btn_font_weight = config.get('Interface', 'button_font_weight', fallback='bold')

    style.configure('TButton', background=btn_bg, foreground=btn_fg,
                    font=(btn_font_family, btn_font_size, btn_font_weight), padding=6)
    style.map('TButton', background=[('active', '#45a049')])

    style.configure('TLabel', background=bg, font=(font_family, font_size))
    style.configure('TFrame', background=bg)
    style.configure('TMenubutton', background=bg, font=(font_family, font_size))

    if isinstance(widget, (tk.Tk, tk.Toplevel)):
        widget.configure(bg=bg)


def get_data_path(filename: str) -> str:
    """Return the absolute path to a file in the data/ directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', filename)