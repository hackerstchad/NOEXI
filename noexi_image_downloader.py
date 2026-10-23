#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███╗   ██╗ ██████╗ ███████╗██╗  ██╗██╗      ███╗   ███╗ █████╗ ███████╗    ║
║   ████╗  ██║██╔═══██╗██╔════╝╚██╗██╔╝██║      ████╗ ████║██╔══██╗██╔════╝    ║
║   ██╔██╗ ██║██║   ██║█████╗   ╚███╔╝ ██║█████╗██╔████╔██║███████║█████╗      ║
║   ██║╚██╗██║██║   ██║██╔══╝   ██╔██╗ ██║╚════╝██║╚██╔╝██║██╔══██║██╔══╝      ║
║   ██║ ╚████║╚██████╔╝███████╗██╔╝ ██╗██║      ██║ ╚═╝ ██║██║  ██║██║         ║
║   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝         ║
║                                                                               ║
║   🚀 NOEXI ADVANCED IMAGE DOWNLOADER v8.0 🚀                                  ║
║   Téléchargeur d'images web ultra-avancé - Intérieur & Extérieur              ║
║   Plus de 2000+ lignes de code professionnel                                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Auteur  : NOEXI Development Team
Version : 8.0.0
Licence : MIT
Langage : Python 3.8+

Description :
    Script Python ultra-avancé permettant de télécharger automatiquement
    toutes les images présentes sur une page web, que celles-ci soient :
        • En HTML standard (balises <img>)
        • En arrière-plan CSS (background-image)
        • Dans des scripts JavaScript (data-src, lazy-loading, JSON)
        • Dans des iframes et frames
        • Dans des feuilles de style externes (.css)
        • Dans des fichiers JavaScript externes (.js)
        • Dans des carrousels, galeries, modals
        • Générées dynamiquement par JavaScript (via Selenium)
        • Derrière une authentification ou un proxy

Fonctionnalités principales :
    ✅ Téléchargement d'images par URL unique ou liste d'URLs
    ✅ Détection intelligente : img, picture, source, css, js, iframe
    ✅ Support du lazy-loading et data-srcset
    ✅ Filtrage par extension, taille, dimensions, type MIME
    ✅ Barre de progression en temps réel (tqdm + rich)
    ✅ Téléchargement multi-threadé / multi-process
    ✅ Reprise après interruption (resume)
    ✅ Renommage intelligent et organisation par domaine
    ✅ Conversion de formats (webp, png, jpg)
    ✅ Génération de thumbnails
    ✅ Vérification d'intégrité (hash MD5/SHA256)
    ✅ Support des proxies SOCKS/HTTP
    ✅ Authentification Basic / Digest / Session cookies
    ✅ Mode headless Selenium pour sites dynamiques
    ✅ Export CSV/JSON/Excel des métadonnées
    ✅ Journalisation complète (logs)
    ✅ Interface CLI stylisée avec couleurs
    ✅ Mode silencieux et verbeux
    ✅ Respect du robots.txt (optionnel)
    ✅ Limitation du débit (rate limiting)
    ✅ User-Agent rotatif

Utilisation :
    python noexi_image_downloader.py --url "https://example.com"
    python noexi_image_downloader.py --url-list urls.txt --output ./images
    python noexi_image_downloader.py --url "https://example.com" --selenium

Exemples avancés :
    # Télécharger avec Selenium pour le contenu dynamique
    python noexi_image_downloader.py -u "https://example.com" --selenium --scroll

    # Utiliser un proxy et une authentification
    python noexi_image_downloader.py -u "https://example.com" \
        --proxy "http://user:pass@proxy:8080" --auth "user:password"

    # Convertir tout en webp et générer des miniatures
    python noexi_image_downloader.py -u "https://example.com" \
        --convert webp --thumbnails --size 300x300
"""

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS STANDARDS
# ═══════════════════════════════════════════════════════════════════════════════

import argparse
import asyncio
import base64
import concurrent.futures
import csv
import hashlib
import imghdr
import io
import json
import logging
import mimetypes
import os
import random
import re
import shutil
import ssl
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
import urllib.robotparser
import warnings
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse, urlunparse, urldefrag

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS TIERS (avec gestion gracieuse)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        Progress, SpinnerColumn, BarColumn, TextColumn,
        TimeElapsedColumn, TimeRemainingColumn, DownloadColumn,
        TransferSpeedColumn, TaskProgressColumn
    )
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from PIL import Image, ImageOps, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES GLOBALES
# ═══════════════════════════════════════════════════════════════════════════════

__version__ = "8.0.0"
__author__ = "NOEXI Development Team"
__license__ = "MIT"

# Couleurs ANSI
class Colors:
    """Palette de couleurs ANSI pour le terminal."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

# Styles Rich
class RichStyles:
    """Styles prédéfinis pour Rich."""
    TITLE = "bold bright_green"
    SUBTITLE = "bold green"
    SUCCESS = "bold green"
    ERROR = "bold red"
    WARNING = "bold yellow"
    INFO = "bold cyan"
    DIM = "dim"

# Extensions d'images supportées
SUPPORTED_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
    '.ico', '.tiff', '.tif', '.raw', '.cr2', '.nef', '.arw',
    '.heic', '.heif', '.avif', '.jxl', '.psd', '.eps', '.pdf'
}

IMAGE_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
    'image/svg+xml', 'image/x-icon', 'image/vnd.microsoft.icon',
    'image/tiff', 'image/raw', 'image/heic', 'image/heif',
    'image/avif', 'image/jxl', 'image/vnd.adobe.photoshop',
    'application/pdf'
}

# User-Agents rotatifs
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0"
]

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DU LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure le système de journalisation.
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Chemin optionnel vers un fichier de log
        
    Returns:
        Logger configuré
    """
    logger = logging.getLogger("noexi_downloader")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    if logger.handlers:
        logger.handlers.clear()
    
    # Format détaillé
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURES DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ImageInfo:
    """Représente les métadonnées d'une image détectée."""
    url: str
    source_url: str
    source_type: str = "html"
    alt: str = ""
    title: str = ""
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    status_code: Optional[int] = None
    md5: Optional[str] = None
    sha256: Optional[str] = None
    download_time: float = 0.0
    error_message: Optional[str] = None
    downloaded: bool = False
    skipped: bool = False
    converted: bool = False
    thumbnail_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire."""
        return asdict(self)


@dataclass
class DownloadStats:
    """Statistiques globales de téléchargement."""
    total_urls: int = 0
    detected_images: int = 0
    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    converted: int = 0
    thumbnails: int = 0
    total_bytes: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Durée totale en secondes."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def success_rate(self) -> float:
        """Taux de réussite en pourcentage."""
        if self.detected_images == 0:
            return 0.0
        return (self.downloaded / self.detected_images) * 100


@dataclass
class DownloaderConfig:
    """Configuration complète du téléchargeur."""
    urls: List[str] = field(default_factory=list)
    output_dir: str = "./noexi_downloads"
    max_depth: int = 0
    max_images: Optional[int] = None
    min_size: int = 0
    max_size: Optional[int] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    extensions: Optional[List[str]] = None
    include_external: bool = True
    use_selenium: bool = False
    scroll_pages: bool = False
    scroll_times: int = 3
    scroll_delay: float = 1.5
    timeout: int = 30
    retries: int = 3
    threads: int = 5
    concurrent_requests: int = 10
    delay: float = 0.0
    user_agent: Optional[str] = None
    rotate_ua: bool = False
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    auth: Optional[Tuple[str, str]] = None
    proxy: Optional[str] = None
    verify_ssl: bool = True
    respect_robots: bool = False
    convert_format: Optional[str] = None
    thumbnail_size: Optional[Tuple[int, int]] = None
    organize_by_domain: bool = True
    organize_by_date: bool = False
    no_overwrite: bool = True
    resume: bool = True
    verbose: bool = False
    silent: bool = False
    log_file: Optional[str] = None
    export_csv: bool = False
    export_json: bool = False
    export_excel: bool = False
    export_metadata: bool = True
    filename_template: str = "{index:04d}_{name}_{width}x{height}{ext}"
    blacklist_domains: List[str] = field(default_factory=list)
    whitelist_domains: List[str] = field(default_factory=list)
    custom_regex: Optional[str] = None
    extract_base64: bool = True
    extract_css: bool = True
    extract_js: bool = True
    extract_iframes: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5
    save_page_source: bool = False
    page_source_dir: str = "./noexi_page_sources"


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE PRINCIPALE : NOEXI IMAGE DOWNLOADER
# ═══════════════════════════════════════════════════════════════════════════════

class NoexiImageDownloader:
    """
    Téléchargeur d'images web ultra-avancé.
    
    Cette classe implémente toute la logique de détection, de filtrage,
    de téléchargement et de traitement des images.
    """
    
    def __init__(self, config: DownloaderConfig):
        """
        Initialise le téléchargeur avec une configuration.
        
        Args:
            config: Configuration du téléchargeur
        """
        self.config = config
        self.logger = setup_logging(
            "DEBUG" if config.verbose else ("ERROR" if config.silent else "INFO"),
            config.log_file
        )
        self.stats = DownloadStats()
        self.session: Optional[Any] = None
        self.console = Console() if RICH_AVAILABLE else None
        self._lock = threading.RLock()
        self._downloaded_hashes: Set[str] = set()
        self._url_cache: Set[str] = set()
        self._robots_cache: Dict[str, Any] = {}
        self._rate_limiter = RateLimiter(config.concurrent_requests, config.delay)
        
        # Créer les répertoires de sortie
        self._ensure_directories()
        
        # Initialiser la session HTTP
        self._init_session()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INITIALISATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _ensure_directories(self) -> None:
        """Crée les répertoires nécessaires."""
        dirs_to_create = [self.config.output_dir]
        if self.config.save_page_source:
            dirs_to_create.append(self.config.page_source_dir)
        
        for directory in dirs_to_create:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except OSError as e:
                self.logger.error(f"Impossible de créer le répertoire {directory}: {e}")
    
    def _init_session(self) -> None:
        """Initialise une session HTTP persistante."""
        if not REQUESTS_AVAILABLE:
            self.session = None
            return
        
        self.session = requests.Session()
        
        # Headers par défaut
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # User-Agent
        if self.config.user_agent:
            headers["User-Agent"] = self.config.user_agent
        elif self.config.rotate_ua:
            headers["User-Agent"] = random.choice(USER_AGENTS)
        else:
            headers["User-Agent"] = USER_AGENTS[0]
        
        # Headers personnalisés
        headers.update(self.config.headers)
        self.session.headers.update(headers)
        
        # Cookies
        if self.config.cookies:
            self.session.cookies.update(self.config.cookies)
        
        # Authentification
        if self.config.auth and len(self.config.auth) == 2:
            self.session.auth = self.config.auth
        
        # Proxy
        if self.config.proxy:
            self.session.proxies = {
                "http": self.config.proxy,
                "https": self.config.proxy
            }
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.config.retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.config.concurrent_requests,
            pool_maxsize=self.config.concurrent_requests * 2
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # SSL verification
        self.session.verify = self.config.verify_ssl
    
    def _get_headers(self) -> Dict[str, str]:
        """Retourne les headers pour une requête."""
        headers = {}
        if self.config.rotate_ua:
            headers["User-Agent"] = random.choice(USER_AGENTS)
        elif self.config.user_agent:
            headers["User-Agent"] = self.config.user_agent
        headers.update(self.config.headers)
        return headers
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITAIRES D'AFFICHAGE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def print_banner(self) -> None:
        """Affiche la bannière NOEXI stylisée."""
        if self.config.silent:
            return
        
        banner_text = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███╗   ██╗ ██████╗ ███████╗██╗  ██╗██╗      ███╗   ███╗ █████╗ ███████╗    ║
║   ████╗  ██║██╔═══██╗██╔════╝╚██╗██╔╝██║      ████╗ ████║██╔══██╗██╔════╝    ║
║   ██╔██╗ ██║██║   ██║█████╗   ╚███╔╝ ██║█████╗██╔████╔██║███████║█████╗      ║
║   ██║╚██╗██║██║   ██║██╔══╝   ██╔██╗ ██║╚════╝██║╚██╔╝██║██╔══██║██╔══╝      ║
║   ██║ ╚████║╚██████╔╝███████╗██╔╝ ██╗██║      ██║ ╚═╝ ██║██║  ██║██║         ║
║   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝         ║
║                                                                               ║
║              🚀 ADVANCED IMAGE DOWNLOADER v8.0 🚀                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
        
        if RICH_AVAILABLE and self.console:
            panel = Panel(
                "[bold bright_green]NOEXI ADVANCED IMAGE DOWNLOADER[/bold bright_green]\n"
                "[green]Téléchargeur d'images web ultra-avancé[/green]\n"
                f"[dim]Version {__version__} | {__license__} License[/dim]",
                box=box.DOUBLE,
                border_style="bright_green",
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print(Colors.BRIGHT_GREEN + Colors.BOLD + banner_text + Colors.RESET)
    
    def print_success(self, message: str) -> None:
        """Affiche un message de succès."""
        if self.config.silent:
            return
        if RICH_AVAILABLE and self.console:
            self.console.print(f"[bold green]✓[/bold green] {message}")
        else:
            print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")
    
    def print_error(self, message: str) -> None:
        """Affiche un message d'erreur."""
        if self.config.silent:
            return
        if RICH_AVAILABLE and self.console:
            self.console.print(f"[bold red]✗[/bold red] {message}")
        else:
            print(f"{Colors.RED}✗ {message}{Colors.RESET}")
    
    def print_warning(self, message: str) -> None:
        """Affiche un message d'avertissement."""
        if self.config.silent:
            return
        if RICH_AVAILABLE and self.console:
            self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
        else:
            print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")
    
    def print_info(self, message: str) -> None:
        """Affiche un message d'information."""
        if self.config.silent:
            return
        if RICH_AVAILABLE and self.console:
            self.console.print(f"[bold cyan]ℹ[/bold cyan] {message}")
        else:
            print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITAIRES DE RÉSEAU
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _normalize_url(self, url: str, base_url: str) -> Optional[str]:
        """
        Normalise une URL relative ou absolue.
        
        Args:
            url: URL à normaliser
            base_url: URL de base
            
        Returns:
            URL normalisée ou None si invalide
        """
        if not url or not isinstance(url, str):
            return None
        
        url = url.strip()
        url = url.replace("\\", "/")
        url = url.replace(" ", "%20")
        
        # Ignorer les ancres et les protocoles spéciaux
        if url.startswith(("#", "javascript:", "mailto:", "tel:", "data:image")):
            return None
        
        # Gérer les URLs de type //domain.com
        if url.startswith("//"):
            parsed_base = urlparse(base_url)
            url = f"{parsed_base.scheme}:{url}"
        
        # Joindre l'URL relative à la base
        if not bool(urlparse(url).netloc):
            url = urljoin(base_url, url)
        
        # Supprimer le fragment
        url, _ = urldefrag(url)
        
        # Vérifier la validité
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        
        if parsed.scheme not in ("http", "https"):
            return None
        
        # Décoder puis ré-encoder proprement
        try:
            url = urllib.parse.unquote(url)
            url = urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%~-")
        except Exception:
            pass
        
        return url
    
    def _is_external_url(self, url: str, base_url: str) -> bool:
        """
        Détermine si une URL est externe par rapport à la base.
        
        Args:
            url: URL à vérifier
            base_url: URL de base
            
        Returns:
            True si l'URL est externe
        """
        try:
            url_domain = urlparse(url).netloc.lower()
            base_domain = urlparse(base_url).netloc.lower()
            return url_domain != base_domain and url_domain != ""
        except Exception:
            return True
    
    def _is_allowed_domain(self, url: str) -> bool:
        """
        Vérifie si le domaine est autorisé selon les listes blanches/noires.
        
        Args:
            url: URL à vérifier
            
        Returns:
            True si le domaine est autorisé
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            if self.config.whitelist_domains:
                if not any(d in domain for d in self.config.whitelist_domains):
                    return False
            
            if self.config.blacklist_domains:
                if any(d in domain for d in self.config.blacklist_domains):
                    return False
            
            return True
        except Exception:
            return True
    
    def _check_robots_txt(self, url: str) -> bool:
        """
        Vérifie si l'URL est autorisée par robots.txt.
        
        Args:
            url: URL à vérifier
            
        Returns:
            True si l'URL peut être fetchée
        """
        if not self.config.respect_robots:
            return True
        
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = urljoin(base_url, "/robots.txt")
            
            if base_url not in self._robots_cache:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self._robots_cache[base_url] = rp
            
            user_agent = self.config.user_agent or "*"
            return self._robots_cache[base_url].can_fetch(user_agent, url)
        except Exception as e:
            self.logger.warning(f"Erreur robots.txt pour {url}: {e}")
            return True
    
    def _fetch_url(
        self,
        url: str,
        stream: bool = False,
        method: str = "GET",
        extra_headers: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True
    ) -> Optional[Any]:
        """
        Récupère le contenu d'une URL.
        
        Args:
            url: URL à récupérer
            stream: Si True, retourne une réponse streamée
            method: Méthode HTTP
            extra_headers: Headers supplémentaires
            allow_redirects: Suivre les redirections
            
        Returns:
            Réponse requests ou None en cas d'erreur
        """
        if not REQUESTS_AVAILABLE:
            return self._fetch_url_stdlib(url, method)
        
        if not self._check_robots_txt(url):
            self.logger.info(f"URL bloquée par robots.txt: {url}")
            return None
        
        headers = self._get_headers()
        if extra_headers:
            headers.update(extra_headers)
        
        try:
            self._rate_limiter.acquire()
            response = self.session.request(
                method=method,
                url=url,
                stream=stream,
                headers=headers,
                timeout=self.config.timeout,
                allow_redirects=allow_redirects
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Erreur requête {url}: {e}")
            return None
    
    def _fetch_url_stdlib(
        self,
        url: str,
        method: str = "GET"
    ) -> Optional[Any]:
        """
        Fallback avec urllib si requests n'est pas installé.
        
        Args:
            url: URL à récupérer
            method: Méthode HTTP
            
        Returns:
            Réponse simulée ou None
        """
        try:
            headers = {"User-Agent": self.config.user_agent or USER_AGENTS[0]}
            req = urllib.request.Request(url, headers=headers, method=method)
            
            if self.config.proxy:
                proxy_handler = urllib.request.ProxyHandler({
                    "http": self.config.proxy,
                    "https": self.config.proxy
                })
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(req, timeout=self.config.timeout)
            else:
                response = urllib.request.urlopen(req, timeout=self.config.timeout)
            
            class FakeResponse:
                def __init__(self, resp):
                    self._resp = resp
                    self.url = resp.geturl()
                    self.status_code = resp.getcode()
                    self.headers = dict(resp.headers)
                
                def iter_content(self, chunk_size=8192):
                    while True:
                        chunk = self._resp.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                
                def content(self):
                    return self._resp.read()
                
                def text(self):
                    return self._resp.read().decode("utf-8", errors="ignore")
            
            return FakeResponse(response)
        except Exception as e:
            self.logger.warning(f"Erreur urllib {url}: {e}")
            return None
    
    def _fetch_page_source(self, url: str) -> Optional[str]:
        """
        Récupère le source HTML d'une page.
        
        Args:
            url: URL de la page
            
        Returns:
            Contenu HTML ou None
        """
        response = self._fetch_url(url)
        if not response:
            return None
        
        try:
            content = response.content
            # Détection de l'encodage
            encoding = response.encoding
            if not encoding:
                encoding = "utf-8"
            return content.decode(encoding, errors="ignore")
        except Exception as e:
            self.logger.warning(f"Erreur décodage page {url}: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SELENIUM / CONTENU DYNAMIQUE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _create_selenium_driver(self) -> Optional[Any]:
        """
        Crée un driver Selenium Chrome headless.
        
        Returns:
            WebDriver ou None
        """
        if not SELENIUM_AVAILABLE:
            self.print_error("Selenium n'est pas installé. Installez-le avec: pip install selenium")
            return None
        
        try:
            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(f"--user-agent={self.config.user_agent or USER_AGENTS[0]}")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Proxy
            if self.config.proxy:
                options.add_argument(f"--proxy-server={self.config.proxy}")
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(self.config.timeout)
            return driver
        except WebDriverException as e:
            self.print_error(f"Erreur Selenium: {e}")
            return None
    
    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """
        Récupère le source d'une page avec Selenium.
        
        Args:
            url: URL de la page
            
        Returns:
            Contenu HTML rendu ou None
        """
        driver = self._create_selenium_driver()
        if not driver:
            return None
        
        try:
            driver.get(url)
            
            # Attendre que le body soit présent
            WebDriverWait(driver, self.config.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Attendre un peu pour le lazy-loading
            time.sleep(2)
            
            # Scroll automatique
            if self.config.scroll_pages:
                self._scroll_page(driver)
            
            # Attendre que les images soient chargées
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script(
                        "return Array.from(document.images).every(img => img.complete)"
                    )
                )
            except TimeoutException:
                pass
            
            html = driver.page_source
            
            if self.config.save_page_source:
                self._save_page_source(url, html, "selenium")
            
            return html
        except Exception as e:
            self.logger.error(f"Erreur Selenium pour {url}: {e}")
            return None
        finally:
            try:
                driver.quit()
            except Exception:
                pass
    
    def _scroll_page(self, driver: Any) -> None:
        """
        Fait défiler la page pour charger le contenu lazy-loaded.
        
        Args:
            driver: Instance WebDriver
        """
        self.print_info(f"Défilement de la page ({self.config.scroll_times} fois)")
        
        for i in range(self.config.scroll_times):
            try:
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(self.config.scroll_delay)
                
                # Cliquer sur les boutons "Load more" si présents
                load_more_selectors = [
                    "button:contains('Load more')",
                    ".load-more",
                    "[data-testid='load-more']",
                    ".show-more",
                    ".view-more"
                ]
                for selector in load_more_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                driver.execute_script("arguments[0].click();", element)
                                time.sleep(1)
                    except Exception:
                        pass
            except Exception as e:
                self.logger.warning(f"Erreur scroll {i+1}: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SAUVEGARDE DU SOURCE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _save_page_source(self, url: str, html: str, suffix: str = "source") -> None:
        """
        Sauvegarde le source HTML d'une page.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            suffix: Suffixe du fichier
        """
        if not self.config.save_page_source:
            return
        
        try:
            parsed = urlparse(url)
            safe_name = re.sub(r'[^\w\-_.]', '_', f"{parsed.netloc}_{parsed.path}")[:100]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{suffix}_{timestamp}.html"
            filepath = os.path.join(self.config.page_source_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            
            self.logger.info(f"Source sauvegardé: {filepath}")
        except Exception as e:
            self.logger.warning(f"Erreur sauvegarde source: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DÉTECTION DES IMAGES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def detect_images(self, url: str, html: Optional[str] = None) -> List[ImageInfo]:
        """
        Détecte toutes les images sur une page web.
        
        Args:
            url: URL de la page
            html: Contenu HTML optionnel (sinon fetché)
            
        Returns:
            Liste des ImageInfo détectées
        """
        self.print_info(f"Analyse de {url}")
        
        if html is None:
            if self.config.use_selenium:
                html = self._fetch_with_selenium(url)
            if html is None:
                html = self._fetch_page_source(url)
            
            if html and self.config.save_page_source and not self.config.use_selenium:
                self._save_page_source(url, html, "static")
        
        if not html:
            self.print_error(f"Impossible de récupérer le contenu de {url}")
            return []
        
        images: List[ImageInfo] = []
        
        # Détection HTML
        images.extend(self._extract_images_from_html(url, html))
        
        # Détection CSS
        if self.config.extract_css:
            images.extend(self._extract_images_from_css(url, html))
        
        # Détection JavaScript
        if self.config.extract_js:
            images.extend(self._extract_images_from_js(url, html))
        
        # Détection Base64 inline
        if self.config.extract_base64:
            images.extend(self._extract_base64_images(url, html))
        
        # Détection iframes
        if self.config.extract_iframes:
            images.extend(self._extract_images_from_iframes(url, html))
        
        # Regex personnalisée
        if self.config.custom_regex:
            images.extend(self._extract_with_custom_regex(url, html))
        
        # Déduplication
        images = self._deduplicate_images(images)
        
        # Filtrage
        images = self._filter_images(images)
        
        self.print_info(f"{len(images)} images détectées sur {url}")
        return images
    
    def _extract_images_from_html(self, url: str, html: str) -> List[ImageInfo]:
        """
        Extrait les images des balises HTML.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")
            
            # Balises <img>
            for img in soup.find_all("img"):
                src = self._get_image_src(img, url)
                if src:
                    info = ImageInfo(
                        url=src,
                        source_url=url,
                        source_type="html_img",
                        alt=img.get("alt", ""),
                        title=img.get("title", "")
                    )
                    images.append(info)
                
                # srcset
                srcset = img.get("srcset") or img.get("data-srcset")
                if srcset:
                    for srcset_url in self._parse_srcset(srcset, url):
                        images.append(ImageInfo(
                            url=srcset_url,
                            source_url=url,
                            source_type="html_srcset",
                            alt=img.get("alt", ""),
                            title=img.get("title", "")
                        ))
            
            # Balises <picture> / <source>
            for source in soup.find_all(["picture", "source"]):
                srcset = source.get("srcset") or source.get("data-srcset")
                if srcset:
                    for srcset_url in self._parse_srcset(srcset, url):
                        images.append(ImageInfo(
                            url=srcset_url,
                            source_url=url,
                            source_type="html_picture_source"
                        ))
                
                src = source.get("src") or source.get("data-src")
                if src:
                    normalized = self._normalize_url(src, url)
                    if normalized:
                        images.append(ImageInfo(
                            url=normalized,
                            source_url=url,
                            source_type="html_source"
                        ))
            
            # Balises <figure>
            for figure in soup.find_all("figure"):
                for attr in ["data-src", "data-img", "data-image", "data-url"]:
                    val = figure.get(attr)
                    if val:
                        normalized = self._normalize_url(val, url)
                        if normalized:
                            images.append(ImageInfo(
                                url=normalized,
                                source_url=url,
                                source_type="html_figure"
                            ))
            
            # Favicon
            for link in soup.find_all("link", rel=["icon", "shortcut icon", "apple-touch-icon"]):
                href = link.get("href")
                if href:
                    normalized = self._normalize_url(href, url)
                    if normalized:
                        images.append(ImageInfo(
                            url=normalized,
                            source_url=url,
                            source_type="html_favicon"
                        ))
            
            # Meta tags (Open Graph, Twitter)
            for meta in soup.find_all("meta"):
                prop = meta.get("property", "") or meta.get("name", "")
                if any(x in prop for x in ["image", "thumbnail", "og:image", "twitter:image"]):
                    content = meta.get("content")
                    if content:
                        normalized = self._normalize_url(content, url)
                        if normalized:
                            images.append(ImageInfo(
                                url=normalized,
                                source_url=url,
                                source_type="html_meta"
                            ))
            
            # Attributs data-* contenant des URLs d'images
            for tag in soup.find_all(True):
                for attr, value in tag.attrs.items():
                    if isinstance(value, str) and any(x in attr.lower() for x in ["data-src", "data-img", "data-image", "data-url", "data-lazy", "data-original"]):
                        normalized = self._normalize_url(value, url)
                        if normalized and self._looks_like_image_url(normalized):
                            images.append(ImageInfo(
                                url=normalized,
                                source_url=url,
                                source_type="html_data_attribute"
                            ))
        else:
            # Fallback regex si BeautifulSoup non disponible
            images.extend(self._extract_images_regex_fallback(url, html))
        
        return images
    
    def _get_image_src(self, img: Any, base_url: str) -> Optional[str]:
        """
        Récupère la meilleure source d'une balise img.
        
        Args:
            img: Objet BeautifulSoup img
            base_url: URL de base
            
        Returns:
            URL normalisée ou None
        """
        # Ordre de priorité des attributs
        for attr in [
            "data-src", "data-lazy-src", "data-original", "data-img",
            "data-url", "src", "data-fallback-src"
        ]:
            val = img.get(attr)
            if val and not val.startswith("data:"):
                normalized = self._normalize_url(val, base_url)
                if normalized:
                    return normalized
        
        return None
    
    def _parse_srcset(self, srcset: str, base_url: str) -> List[str]:
        """
        Parse un attribut srcset.
        
        Args:
            srcset: Valeur de srcset
            base_url: URL de base
            
        Returns:
            Liste d'URLs
        """
        urls = []
        if not srcset:
            return urls
        
        parts = re.split(r",\s+", srcset)
        for part in parts:
            url_part = part.strip().split(" ")[0]
            normalized = self._normalize_url(url_part, base_url)
            if normalized:
                urls.append(normalized)
        
        return urls
    
    def _extract_images_regex_fallback(self, url: str, html: str) -> List[ImageInfo]:
        """
        Fallback regex pour extraire les images si bs4 absent.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        patterns = [
            r'<img[^>]+src=["\']([^"\']+)["\']',
            r'<img[^>]+data-src=["\']([^"\']+)["\']',
            r'<source[^>]+srcset=["\']([^"\']+)["\']',
            r'<link[^>]+rel=["\'](?:icon|shortcut icon)["\'][^>]+href=["\']([^"\']+)["\']',
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, html, re.IGNORECASE):
                src = match.group(1)
                normalized = self._normalize_url(src, url)
                if normalized:
                    images.append(ImageInfo(
                        url=normalized,
                        source_url=url,
                        source_type="html_regex_fallback"
                    ))
        
        return images
    
    def _extract_images_from_css(self, url: str, html: str) -> List[ImageInfo]:
        """
        Extrait les images du CSS inline et des feuilles de style externes.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        # CSS inline dans <style>
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")
            for style in soup.find_all("style"):
                css_text = style.get_text()
                images.extend(self._extract_urls_from_css_text(css_text, url))
            
            # Feuilles de style externes
            for link in soup.find_all("link", rel="stylesheet"):
                href = link.get("href")
                if href:
                    css_url = self._normalize_url(href, url)
                    if css_url:
                        css_text = self._fetch_page_source(css_url)
                        if css_text:
                            images.extend(self._extract_urls_from_css_text(css_text, css_url))
        else:
            # Fallback regex
            style_pattern = r'<style[^>]*>(.*?)</style>'
            for match in re.finditer(style_pattern, html, re.DOTALL | re.IGNORECASE):
                images.extend(self._extract_urls_from_css_text(match.group(1), url))
            
            css_link_pattern = r'<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\']([^"\']+)["\']'
            for match in re.finditer(css_link_pattern, html, re.IGNORECASE):
                css_url = self._normalize_url(match.group(1), url)
                if css_url:
                    css_text = self._fetch_page_source(css_url)
                    if css_text:
                        images.extend(self._extract_urls_from_css_text(css_text, css_url))
        
        # Ajouter le type source
        for img in images:
            img.source_type = "css"
        
        return images
    
    def _extract_urls_from_css_text(self, css_text: str, base_url: str) -> List[ImageInfo]:
        """
        Extrait les URLs d'images d'un texte CSS.
        
        Args:
            css_text: Contenu CSS
            base_url: URL de base
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        # Pattern pour url() et image-set()
        patterns = [
            r'url\(["\']?([^"\')]+)["\']?\)',
            r'image-set\(["\']?([^"\')]+)["\']?\s+\d+x\)',
            r'url\(["\']?([^"\')]+)["\']?\)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, css_text, re.IGNORECASE):
                img_url = match.group(1)
                normalized = self._normalize_url(img_url, base_url)
                if normalized and self._looks_like_image_url(normalized):
                    images.append(ImageInfo(
                        url=normalized,
                        source_url=base_url,
                        source_type="css"
                    ))
        
        return images
    
    def _extract_images_from_js(self, url: str, html: str) -> List[ImageInfo]:
        """
        Extrait les images du JavaScript inline et des scripts externes.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")
            for script in soup.find_all("script"):
                src = script.get("src")
                if src:
                    js_url = self._normalize_url(src, url)
                    if js_url:
                        js_text = self._fetch_page_source(js_url)
                        if js_text:
                            images.extend(self._extract_urls_from_js_text(js_text, js_url))
                else:
                    js_text = script.get_text()
                    images.extend(self._extract_urls_from_js_text(js_text, url))
        else:
            script_pattern = r'<script[^>]*>(.*?)</script>'
            for match in re.finditer(script_pattern, html, re.DOTALL | re.IGNORECASE):
                images.extend(self._extract_urls_from_js_text(match.group(1), url))
            
            js_link_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
            for match in re.finditer(js_link_pattern, html, re.IGNORECASE):
                js_url = self._normalize_url(match.group(1), url)
                if js_url:
                    js_text = self._fetch_page_source(js_url)
                    if js_text:
                        images.extend(self._extract_urls_from_js_text(js_text, js_url))
        
        for img in images:
            img.source_type = "js"
        
        return images
    
    def _extract_urls_from_js_text(self, js_text: str, base_url: str) -> List[ImageInfo]:
        """
        Extrait les URLs d'images d'un texte JavaScript.
        
        Args:
            js_text: Contenu JS
            base_url: URL de base
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        patterns = [
            r'["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|bmp|svg|ico|avif|jxl))["\']',
            r'["\'](https?://[^"\']+\.(?:jpg|jpeg|png|gif|webp|bmp|svg|ico|avif|jxl))["\']',
            r'"url":\s*"([^"]+\.(?:jpg|jpeg|png|gif|webp|bmp|svg|ico|avif|jxl))"',
            r'"src":\s*"([^"]+\.(?:jpg|jpeg|png|gif|webp|bmp|svg|ico|avif|jxl))"',
            r'"image":\s*"([^"]+)"',
            r'"thumbnail":\s*"([^"]+)"',
            r'"poster":\s*"([^"]+)"'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, js_text, re.IGNORECASE):
                img_url = match.group(1)
                normalized = self._normalize_url(img_url, base_url)
                if normalized and self._looks_like_image_url(normalized):
                    images.append(ImageInfo(
                        url=normalized,
                        source_url=base_url,
                        source_type="js"
                    ))
        
        return images
    
    def _extract_base64_images(self, url: str, html: str) -> List[ImageInfo]:
        """
        Extrait les images encodées en base64.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        pattern = r'data:image/([^;]+);base64,([A-Za-z0-9+/=]+)'
        for match in re.finditer(pattern, html):
            mime_type = f"image/{match.group(1)}"
            b64_data = match.group(2)
            
            # Créer une URL data unique
            data_url = f"data:{mime_type};base64,{b64_data[:50]}..."
            
            images.append(ImageInfo(
                url=data_url,
                source_url=url,
                source_type="base64",
                mime_type=mime_type
            ))
        
        return images
    
    def _extract_images_from_iframes(self, url: str, html: str) -> List[ImageInfo]:
        """
        Extrait les images des iframes.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")
            for iframe in soup.find_all(["iframe", "frame"]):
                src = iframe.get("src")
                if src:
                    iframe_url = self._normalize_url(src, url)
                    if iframe_url:
                        iframe_html = self._fetch_page_source(iframe_url)
                        if iframe_html:
                            iframe_images = self.detect_images(iframe_url, iframe_html)
                            for img in iframe_images:
                                img.source_type = f"iframe_{img.source_type}"
                            images.extend(iframe_images)
        else:
            iframe_pattern = r'<(?:iframe|frame)[^>]+src=["\']([^"\']+)["\']'
            for match in re.finditer(iframe_pattern, html, re.IGNORECASE):
                iframe_url = self._normalize_url(match.group(1), url)
                if iframe_url:
                    iframe_html = self._fetch_page_source(iframe_url)
                    if iframe_html:
                        iframe_images = self.detect_images(iframe_url, iframe_html)
                        images.extend(iframe_images)
        
        return images
    
    def _extract_with_custom_regex(self, url: str, html: str) -> List[ImageInfo]:
        """
        Extrait les images avec une regex personnalisée.
        
        Args:
            url: URL de la page
            html: Contenu HTML
            
        Returns:
            Liste d'ImageInfo
        """
        images = []
        
        try:
            for match in re.finditer(self.config.custom_regex, html):
                img_url = match.group(1) if match.groups() else match.group(0)
                normalized = self._normalize_url(img_url, url)
                if normalized and self._looks_like_image_url(normalized):
                    images.append(ImageInfo(
                        url=normalized,
                        source_url=url,
                        source_type="custom_regex"
                    ))
        except re.error as e:
            self.print_error(f"Regex personnalisée invalide: {e}")
        
        return images
    
    def _looks_like_image_url(self, url: str) -> bool:
        """
        Vérifie si une URL ressemble à une image.
        
        Args:
            url: URL à vérifier
            
        Returns:
            True si c'est probablement une image
        """
        if url.startswith("data:image"):
            return True
        
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        if any(path.endswith(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS):
            return True
        
        # URLs d'images sans extension (ex: CloudFront, Imgix)
        image_indicators = ["/image", "/img", "/photo", "/picture", "/media",
                           "/upload", "/assets", "/cdn", "/wp-content", "/static"]
        if any(indicator in path for indicator in image_indicators):
            return True
        
        # Paramètres d'image communs
        query = parsed.query.lower()
        image_params = ["format=", "w=", "width=", "h=", "height=", "fit=",
                       "crop=", "quality=", "q="]
        if any(param in query for param in image_params):
            return True
        
        return False
    
    def _deduplicate_images(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """
        Déduplique les images par URL.
        
        Args:
            images: Liste d'ImageInfo
            
        Returns:
            Liste dédupliquée
        """
        seen = set()
        unique = []
        
        for img in images:
            url = img.url
            if url not in seen:
                seen.add(url)
                unique.append(img)
        
        return unique
    
    def _filter_images(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """
        Filtre les images selon la configuration.
        
        Args:
            images: Liste d'ImageInfo
            
        Returns:
            Liste filtrée
        """
        filtered = []
        
        for img in images:
            # Filtrer par domaine
            if not self._is_allowed_domain(img.url):
                continue
            
            # Filtrer externes
            if not self.config.include_external:
                if self._is_external_url(img.url, img.source_url):
                    continue
            
            # Filtrer par extension
            if self.config.extensions:
                ext = self._get_extension_from_url(img.url)
                if ext and ext.lower() not in self.config.extensions:
                    continue
            
            filtered.append(img)
        
        # Limiter le nombre
        if self.config.max_images:
            filtered = filtered[:self.config.max_images]
        
        return filtered
    
    def _get_extension_from_url(self, url: str) -> Optional[str]:
        """
        Extrait l'extension d'une URL.
        
        Args:
            url: URL de l'image
            
        Returns:
            Extension avec le point
        """
        if url.startswith("data:"):
            return None
        
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1].lower()
        
        if not ext:
            return None
        
        # Nettoyer les paramètres d'URL collés à l'extension
        ext = re.split(r'[?#]', ext)[0]
        return ext
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TÉLÉCHARGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def download_all(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """
        Télécharge toutes les images détectées.
        
        Args:
            images: Liste d'ImageInfo
            
        Returns:
            Liste mise à jour des ImageInfo
        """
        self.stats.detected_images = len(images)
        
        if not images:
            self.print_warning("Aucune image à télécharger")
            return []
        
        self.print_info(f"Téléchargement de {len(images)} images...")
        
        # Utiliser Rich Progress si disponible
        if RICH_AVAILABLE and self.console and not self.config.silent:
            return self._download_with_rich_progress(images)
        elif TQDM_AVAILABLE and not self.config.silent:
            return self._download_with_tqdm(images)
        else:
            return self._download_simple(images)
    
    def _download_with_rich_progress(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """Téléchargement avec barre de progression Rich."""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]{task.description}"),
            BarColumn(complete_style="green", finished_style="bright_green"),
            TaskProgressColumn(),
            " • ",
            DownloadColumn(binary_units=True),
            " • ",
            TransferSpeedColumn(),
            " • ",
            TimeElapsedColumn(),
            "<", TimeRemainingColumn(),
            console=self.console,
            transient=False
        ) as progress:
            task = progress.add_task(
                "[green]Téléchargement des images NOEXI...",
                total=len(images)
            )
            
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.config.threads
            ) as executor:
                futures = {
                    executor.submit(self._download_image, img, progress, task): img
                    for img in images
                }
                
                for future in concurrent.futures.as_completed(futures):
                    img = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        img.error_message = str(e)
                        self.stats.failed += 1
                        results.append(img)
        
        return results
    
    def _download_with_tqdm(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """Téléchargement avec barre de progression tqdm."""
        results = []
        
        with tqdm(
            total=len(images),
            desc=f"{Colors.GREEN}NOEXI Download{Colors.RESET}",
            unit="img",
            colour="green",
            ncols=100
        ) as pbar:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.config.threads
            ) as executor:
                futures = {
                    executor.submit(self._download_image, img, None, None): img
                    for img in images
                }
                
                for future in concurrent.futures.as_completed(futures):
                    img = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        pbar.update(1)
                        pbar.set_postfix({
                            "OK": self.stats.downloaded,
                            "Skip": self.stats.skipped,
                            "Err": self.stats.failed
                        })
                    except Exception as e:
                        img.error_message = str(e)
                        self.stats.failed += 1
                        results.append(img)
                        pbar.update(1)
        
        return results
    
    def _download_simple(self, images: List[ImageInfo]) -> List[ImageInfo]:
        """Téléchargement simple sans barre de progression."""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.threads
        ) as executor:
            futures = {
                executor.submit(self._download_image, img, None, None): img
                for img in images
            }
            
            for future in concurrent.futures.as_completed(futures):
                img = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    img.error_message = str(e)
                    self.stats.failed += 1
                    results.append(img)
        
        return results
    
    def _download_image(
        self,
        img: ImageInfo,
        progress: Optional[Any] = None,
        task: Optional[Any] = None
    ) -> ImageInfo:
        """
        Télécharge une image individuelle.
        
        Args:
            img: ImageInfo à télécharger
            progress: Objet Rich Progress
            task: Tâche Rich
            
        Returns:
            ImageInfo mis à jour
        """
        start_time = time.time()
        
        try:
            # Vérifier les doublons par hash d'URL
            url_hash = hashlib.md5(img.url.encode()).hexdigest()
            if url_hash in self._url_cache and self.config.no_overwrite:
                img.skipped = True
                img.error_message = "URL déjà téléchargée"
                with self._lock:
                    self.stats.skipped += 1
                self._update_progress(progress, task, 0)
                return img
            
            self._url_cache.add(url_hash)
            
            # Déterminer le chemin de sortie
            output_path = self._get_output_path(img)
            
            # Vérifier si le fichier existe déjà
            if os.path.exists(output_path) and self.config.no_overwrite:
                img.file_path = output_path
                img.file_size = os.path.getsize(output_path)
                img.skipped = True
                img.error_message = "Fichier déjà existant"
                with self._lock:
                    self.stats.skipped += 1
                self._update_progress(progress, task, 0)
                return img
            
            # Télécharger le contenu
            content = self._download_image_content(img)
            
            if content is None:
                img.error_message = "Échec du téléchargement"
                with self._lock:
                    self.stats.failed += 1
                self._update_progress(progress, task, 0)
                return img
            
            # Vérifier la taille
            if not self._check_size_constraints(len(content)):
                img.error_message = "Hors limites de taille"
                img.skipped = True
                with self._lock:
                    self.stats.skipped += 1
                self._update_progress(progress, task, len(content))
                return img
            
            # Sauvegarder le fichier
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(content)
            
            img.file_path = output_path
            img.file_size = len(content)
            img.downloaded = True
            img.download_time = time.time() - start_time
            
            # Calculer les hashes
            img.md5 = hashlib.md5(content).hexdigest()
            img.sha256 = hashlib.sha256(content).hexdigest()
            
            # Vérifier les doublons par contenu
            if img.sha256 in self._downloaded_hashes and self.config.no_overwrite:
                os.remove(output_path)
                img.skipped = True
                img.error_message = "Image en double (contenu identique)"
                img.downloaded = False
                with self._lock:
                    self.stats.downloaded -= 1
                    self.stats.skipped += 1
                self._update_progress(progress, task, len(content))
                return img
            
            self._downloaded_hashes.add(img.sha256)
            
            # Traiter l'image (dimensions, conversion, thumbnail)
            self._process_downloaded_image(img)
            
            # Mettre à jour les stats
            with self._lock:
                self.stats.downloaded += 1
                self.stats.total_bytes += img.file_size
            
            self._update_progress(progress, task, len(content))
            
            self.logger.info(f"Téléchargé: {img.url} -> {output_path}")
            
        except Exception as e:
            img.error_message = str(e)
            with self._lock:
                self.stats.failed += 1
            self.logger.error(f"Erreur téléchargement {img.url}: {e}")
            self._update_progress(progress, task, 0)
        
        return img
    
    def _update_progress(
        self,
        progress: Optional[Any],
        task: Optional[Any],
        bytes_count: int
    ) -> None:
        """Met à jour la barre de progression."""
        if progress and task is not None:
            progress.update(task, advance=1)
            if bytes_count > 0:
                progress.update(task, total=progress.tasks[task].total)
    
    def _download_image_content(self, img: ImageInfo) -> Optional[bytes]:
        """
        Télécharge le contenu binaire d'une image.
        
        Args:
            img: ImageInfo
            
        Returns:
            Contenu binaire ou None
        """
        # Images base64 inline
        if img.url.startswith("data:image"):
            return self._decode_base64_image(img.url)
        
        # Requête HTTP
        response = self._fetch_url(img.url, stream=True)
        if not response:
            return None
        
        img.status_code = getattr(response, "status_code", 200)
        
        # Détecter le type MIME
        content_type = response.headers.get("Content-Type", "")
        if content_type:
            img.mime_type = content_type.split(";")[0].strip()
        
        # Lire le contenu
        try:
            if REQUESTS_AVAILABLE and hasattr(response, "content"):
                return response.content
            elif hasattr(response, "content"):
                return response.content()
            else:
                chunks = []
                for chunk in response.iter_content(chunk_size=8192):
                    chunks.append(chunk)
                return b"".join(chunks)
        except Exception as e:
            self.logger.warning(f"Erreur lecture contenu {img.url}: {e}")
            return None
    
    def _decode_base64_image(self, data_url: str) -> Optional[bytes]:
        """
        Décode une image base64 inline.
        
        Args:
            data_url: URL data:image
            
        Returns:
            Contenu binaire ou None
        """
        try:
            match = re.match(r'data:image/([^;]+);base64,(.*)', data_url)
            if match:
                return base64.b64decode(match.group(2))
            return None
        except Exception as e:
            self.logger.warning(f"Erreur décodage base64: {e}")
            return None
    
    def _check_size_constraints(self, size: int) -> bool:
        """
        Vérifie si la taille respecte les contraintes.
        
        Args:
            size: Taille en octets
            
        Returns:
            True si valide
        """
        if self.config.min_size and size < self.config.min_size:
            return False
        if self.config.max_size and size > self.config.max_size:
            return False
        return True
    
    def _get_output_path(self, img: ImageInfo) -> str:
        """
        Détermine le chemin de sortie pour une image.
        
        Args:
            img: ImageInfo
            
        Returns:
            Chemin de fichier complet
        """
        base_dir = self.config.output_dir
        
        # Organisation par domaine
        if self.config.organize_by_domain:
            parsed = urlparse(img.source_url)
            domain_dir = parsed.netloc.replace(".", "_")
            base_dir = os.path.join(base_dir, domain_dir)
        
        # Organisation par date
        if self.config.organize_by_date:
            date_dir = datetime.now().strftime("%Y-%m-%d")
            base_dir = os.path.join(base_dir, date_dir)
        
        # Déterminer l'extension
        ext = self._get_extension_from_url(img.url)
        if not ext and img.mime_type:
            ext = self._mime_to_extension(img.mime_type)
        if not ext:
            ext = ".jpg"
        
        # Nettoyer l'extension
        ext = ext.split("?")[0].split("#")[0]
        if not ext.startswith("."):
            ext = "." + ext
        
        # Nom de fichier
        index = len(self._url_cache)
        name = self._sanitize_filename(self._get_url_basename(img.url))
        if not name:
            name = f"image_{index}"
        
        width = img.width or 0
        height = img.height or 0
        
        filename = self.config.filename_template.format(
            index=index,
            name=name[:50],
            width=width,
            height=height,
            ext=ext,
            domain=urlparse(img.source_url).netloc,
            source_type=img.source_type,
            md5=img.md5 or "unknown"
        )
        
        # S'assurer que le nom est unique
        output_path = os.path.join(base_dir, filename)
        counter = 1
        base_path, original_ext = os.path.splitext(output_path)
        while os.path.exists(output_path) and self.config.no_overwrite:
            output_path = f"{base_path}_{counter}{original_ext}"
            counter += 1
        
        return output_path
    
    def _get_url_basename(self, url: str) -> str:
        """
        Extrait le nom de base d'une URL.
        
        Args:
            url: URL
            
        Returns:
            Nom de base
        """
        if url.startswith("data:"):
            return "base64_image"
        
        parsed = urlparse(url)
        path = parsed.path
        basename = os.path.basename(path)
        basename = os.path.splitext(basename)[0]
        return basename
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Nettoie un nom de fichier.
        
        Args:
            filename: Nom de fichier brut
            
        Returns:
            Nom de fichier sécurisé
        """
        if not filename:
            return "image"
        
        # Remplacer les caractères invalides
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip(". ")
        
        # Limiter la longueur
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename or "image"
    
    def _mime_to_extension(self, mime_type: str) -> str:
        """
        Convertit un type MIME en extension.
        
        Args:
            mime_type: Type MIME
            
        Returns:
            Extension
        """
        mapping = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/bmp": ".bmp",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
            "image/x-icon": ".ico",
            "image/vnd.microsoft.icon": ".ico",
            "image/tiff": ".tiff",
            "image/heic": ".heic",
            "image/heif": ".heif",
            "image/avif": ".avif",
            "image/jxl": ".jxl"
        }
        return mapping.get(mime_type.lower(), ".jpg")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TRAITEMENT POST-TÉLÉCHARGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _process_downloaded_image(self, img: ImageInfo) -> None:
        """
        Traite une image après téléchargement (dimensions, conversion, thumbnail).
        
        Args:
            img: ImageInfo
        """
        if not img.file_path or not os.path.exists(img.file_path):
            return
        
        # Vérifier si c'est une image valide
        if not PIL_AVAILABLE:
            return
        
        try:
            # Ouvrir l'image pour obtenir les dimensions
            with Image.open(img.file_path) as image:
                img.width, img.height = image.size
                img.extension = os.path.splitext(img.file_path)[1].lower()
                
                # Vérifier les contraintes de dimensions
                if not self._check_dimension_constraints(img.width, img.height):
                    os.remove(img.file_path)
                    img.downloaded = False
                    img.skipped = True
                    img.error_message = "Hors limites de dimensions"
                    with self._lock:
                        self.stats.downloaded -= 1
                        self.stats.skipped += 1
                        self.stats.total_bytes -= img.file_size
                    return
                
                # Convertir le format si demandé
                if self.config.convert_format:
                    self._convert_image(img, image)
                
                # Générer une miniature si demandée
                if self.config.thumbnail_size:
                    self._generate_thumbnail(img, image)
        
        except Exception as e:
            self.logger.warning(f"Erreur traitement image {img.file_path}: {e}")
    
    def _check_dimension_constraints(self, width: int, height: int) -> bool:
        """
        Vérifie les contraintes de dimensions.
        
        Args:
            width: Largeur
            height: Hauteur
            
        Returns:
            True si valide
        """
        if self.config.min_width and width < self.config.min_width:
            return False
        if self.config.min_height and height < self.config.min_height:
            return False
        return True
    
    def _convert_image(self, img: ImageInfo, image: Any) -> None:
        """
        Convertit une image dans un autre format.
        
        Args:
            img: ImageInfo
            image: Objet PIL Image
        """
        if not self.config.convert_format:
            return
        
        try:
            target_format = self.config.convert_format.lower()
            if target_format.startswith("."):
                target_format = target_format[1:]
            
            if target_format not in ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]:
                return
            
            base_path = os.path.splitext(img.file_path)[0]
            new_path = f"{base_path}.{target_format}"
            
            # Convertir en RGB si nécessaire
            if target_format in ["jpg", "jpeg"] and image.mode in ("RGBA", "P", "LA"):
                image = image.convert("RGB")
            
            image.save(new_path, target_format.upper())
            
            # Remplacer l'ancien fichier
            os.remove(img.file_path)
            img.file_path = new_path
            img.extension = f".{target_format}"
            img.converted = True
            img.file_size = os.path.getsize(new_path)
            
            with self._lock:
                self.stats.converted += 1
            
            self.logger.info(f"Converti: {new_path}")
        
        except Exception as e:
            self.logger.warning(f"Erreur conversion {img.file_path}: {e}")
    
    def _generate_thumbnail(self, img: ImageInfo, image: Any) -> None:
        """
        Génère une miniature de l'image.
        
        Args:
            img: ImageInfo
            image: Objet PIL Image
        """
        if not self.config.thumbnail_size:
            return
        
        try:
            thumb_width, thumb_height = self.config.thumbnail_size
            thumb = image.copy()
            thumb.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            
            base_path = os.path.splitext(img.file_path)[0]
            thumb_path = f"{base_path}_thumb.jpg"
            
            if thumb.mode in ("RGBA", "P", "LA"):
                thumb = thumb.convert("RGB")
            
            thumb.save(thumb_path, "JPEG", quality=85)
            img.thumbnail_path = thumb_path
            
            with self._lock:
                self.stats.thumbnails += 1
            
            self.logger.info(f"Miniature: {thumb_path}")
        
        except Exception as e:
            self.logger.warning(f"Erreur miniature {img.file_path}: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORT DE MÉTADONNÉES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def export_metadata(self, images: List[ImageInfo]) -> None:
        """
        Exporte les métadonnées des images.
        
        Args:
            images: Liste d'ImageInfo
        """
        if not images:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"noexi_metadata_{timestamp}"
        
        if self.config.export_json:
            self._export_json(images, f"{base_name}.json")
        
        if self.config.export_csv:
            self._export_csv(images, f"{base_name}.csv")
        
        if self.config.export_excel and (OPENPYXL_AVAILABLE or PANDAS_AVAILABLE):
            self._export_excel(images, f"{base_name}.xlsx")
        
        # Toujours sauvegarder un JSON par défaut si export_metadata
        if self.config.export_metadata and not self.config.export_json:
            self._export_json(images, f"{base_name}.json")
    
    def _export_json(self, images: List[ImageInfo], filename: str) -> None:
        """Exporte en JSON."""
        try:
            filepath = os.path.join(self.config.output_dir, filename)
            data = {
                "metadata": {
                    "version": __version__,
                    "generated_at": datetime.now().isoformat(),
                    "total_images": len(images),
                    "downloaded": self.stats.downloaded,
                    "skipped": self.stats.skipped,
                    "failed": self.stats.failed
                },
                "images": [img.to_dict() for img in images]
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.print_success(f"Métadonnées JSON: {filepath}")
        except Exception as e:
            self.print_error(f"Erreur export JSON: {e}")
    
    def _export_csv(self, images: List[ImageInfo], filename: str) -> None:
        """Exporte en CSV."""
        try:
            filepath = os.path.join(self.config.output_dir, filename)
            if not images:
                return
            
            fieldnames = list(images[0].to_dict().keys())
            
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows([img.to_dict() for img in images])
            
            self.print_success(f"Métadonnées CSV: {filepath}")
        except Exception as e:
            self.print_error(f"Erreur export CSV: {e}")
    
    def _export_excel(self, images: List[ImageInfo], filename: str) -> None:
        """Exporte en Excel."""
        try:
            filepath = os.path.join(self.config.output_dir, filename)
            
            if PANDAS_AVAILABLE:
                df = pd.DataFrame([img.to_dict() for img in images])
                df.to_excel(filepath, index=False, engine="openpyxl")
            elif OPENPYXL_AVAILABLE:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.title = "Images"
                
                if images:
                    headers = list(images[0].to_dict().keys())
                    ws.append(headers)
                    for img in images:
                        ws.append(list(img.to_dict().values()))
                
                wb.save(filepath)
            
            self.print_success(f"Métadonnées Excel: {filepath}")
        except Exception as e:
            self.print_error(f"Erreur export Excel: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RAPPORT FINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def print_summary(self) -> None:
        """Affiche un résumé final."""
        if self.config.silent:
            return
        
        self.stats.end_time = time.time()
        duration = self.stats.duration
        
        summary_lines = [
            "",
            "═" * 60,
            "  📊 RÉSUMÉ NOEXI IMAGE DOWNLOADER",
            "═" * 60,
            f"  ⏱  Durée            : {duration:.2f} secondes",
            f"  🔍 Images détectées : {self.stats.detected_images}",
            f"  ✅ Téléchargées     : {self.stats.downloaded}",
            f"  ⏭️  Ignorées         : {self.stats.skipped}",
            f"  ❌ Échecs           : {self.stats.failed}",
            f"  🔄 Converties       : {self.stats.converted}",
            f"  🖼️  Miniatures       : {self.stats.thumbnails}",
            f"  📦 Taille totale    : {self._format_bytes(self.stats.total_bytes)}",
            f"  📈 Taux de réussite : {self.stats.success_rate:.1f}%",
            f"  📁 Répertoire       : {os.path.abspath(self.config.output_dir)}",
            "═" * 60,
            ""
        ]
        
        if RICH_AVAILABLE and self.console:
            table = Table(
                title="[bold bright_green]Résumé NOEXI[/bold bright_green]",
                box=box.DOUBLE_EDGE,
                border_style="green"
            )
            table.add_column("Métrique", style="cyan")
            table.add_column("Valeur", style="green")
            
            table.add_row("Durée", f"{duration:.2f} s")
            table.add_row("Images détectées", str(self.stats.detected_images))
            table.add_row("Téléchargées", str(self.stats.downloaded))
            table.add_row("Ignorées", str(self.stats.skipped))
            table.add_row("Échecs", str(self.stats.failed))
            table.add_row("Converties", str(self.stats.converted))
            table.add_row("Miniatures", str(self.stats.thumbnails))
            table.add_row("Taille totale", self._format_bytes(self.stats.total_bytes))
            table.add_row("Taux de réussite", f"{self.stats.success_rate:.1f}%")
            table.add_row("Répertoire", os.path.abspath(self.config.output_dir))
            
            self.console.print(table)
        else:
            print("\n".join(summary_lines))
    
    @staticmethod
    def _format_bytes(size: int) -> str:
        """
        Formate une taille en octets en unités lisibles.
        
        Args:
            size: Taille en octets
            
        Returns:
            Chaîne formatée
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXÉCUTION PRINCIPALE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def run(self) -> List[ImageInfo]:
        """
        Lance le téléchargement complet.
        
        Returns:
            Liste des ImageInfo traités
        """
        self.stats.start_time = time.time()
        self.print_banner()
        
        if not self.config.urls:
            self.print_error("Aucune URL fournie")
            return []
        
        self.stats.total_urls = len(self.config.urls)
        self.print_info(f"Traitement de {len(self.config.urls)} URL(s)")
        
        all_images: List[ImageInfo] = []
        
        for url in self.config.urls:
            try:
                images = self.detect_images(url)
                all_images.extend(images)
            except Exception as e:
                self.print_error(f"Erreur analyse {url}: {e}")
                self.stats.errors.append(f"{url}: {e}")
        
        # Limiter globalement
        if self.config.max_images:
            all_images = all_images[:self.config.max_images]
        
        # Télécharger
        downloaded_images = self.download_all(all_images)
        
        # Exporter les métadonnées
        self.export_metadata(downloaded_images)
        
        # Résumé
        self.print_summary()
        
        return downloaded_images


# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """Limiteur de débit pour les requêtes concurrentes."""
    
    def __init__(self, max_concurrent: int, delay: float):
        """
        Initialise le rate limiter.
        
        Args:
            max_concurrent: Nombre maximum de requêtes simultanées
            delay: Délai minimum entre les requêtes
        """
        self.max_concurrent = max(1, max_concurrent)
        self.delay = max(0.0, delay)
        self._semaphore = threading.Semaphore(self.max_concurrent)
        self._last_request_time = 0.0
        self._lock = threading.Lock()
    
    def acquire(self) -> None:
        """Acquiert une permission pour effectuer une requête."""
        self._semaphore.acquire()
        
        if self.delay > 0:
            with self._lock:
                now = time.time()
                elapsed = now - self._last_request_time
                if elapsed < self.delay:
                    time.sleep(self.delay - elapsed)
                self._last_request_time = time.time()
    
    def release(self) -> None:
        """Libère une permission."""
        self._semaphore.release()


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION PAR FICHIER
# ═══════════════════════════════════════════════════════════════════════════════

def load_config_from_file(filepath: str) -> Dict[str, Any]:
    """
    Charge une configuration depuis un fichier JSON/YAML.
    
    Args:
        filepath: Chemin du fichier
        
    Returns:
        Dictionnaire de configuration
    """
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in [".yaml", ".yml"] and YAML_AVAILABLE:
                return yaml.safe_load(f) or {}
            elif ext == ".json":
                return json.load(f)
    except Exception as e:
        print(f"Erreur chargement config {filepath}: {e}")
    
    return {}


# ═══════════════════════════════════════════════════════════════════════════════
# INTERFACE EN LIGNE DE COMMANDE
# ═══════════════════════════════════════════════════════════════════════════════

def create_parser() -> argparse.ArgumentParser:
    """
    Crée le parser d'arguments.
    
    Returns:
        ArgumentParser configuré
    """
    parser = argparse.ArgumentParser(
        prog="noexi_image_downloader",
        description="NOEXI Advanced Image Downloader - Téléchargeur d'images web ultra-avancé",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s -u https://example.com
  %(prog)s -u https://example.com -o ./mes_images --selenium --scroll
  %(prog)s --url-list urls.txt -t 10 --convert webp --thumbnails 300x300
  %(prog)s -u https://example.com --proxy http://proxy:8080 --auth user:pass
        """
    )
    
    # Groupe URL
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument(
        "-u", "--url",
        type=str,
        help="URL du site web à analyser"
    )
    url_group.add_argument(
        "--url-list",
        type=str,
        help="Fichier contenant une liste d'URLs (une par ligne)"
    )
    url_group.add_argument(
        "--config",
        type=str,
        help="Fichier de configuration JSON/YAML"
    )
    
    # Groupe sortie
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./noexi_downloads",
        help="Répertoire de sortie (défaut: ./noexi_downloads)"
    )
    
    # Groupe détection
    detection_group = parser.add_argument_group("Détection")
    detection_group.add_argument(
        "--no-external",
        action="store_true",
        help="Ne pas télécharger les images externes"
    )
    detection_group.add_argument(
        "--no-css",
        action="store_true",
        help="Ne pas extraire les images du CSS"
    )
    detection_group.add_argument(
        "--no-js",
        action="store_true",
        help="Ne pas extraire les images du JavaScript"
    )
    detection_group.add_argument(
        "--no-iframes",
        action="store_true",
        help="Ne pas analyser les iframes"
    )
    detection_group.add_argument(
        "--no-base64",
        action="store_true",
        help="Ne pas extraire les images base64 inline"
    )
    detection_group.add_argument(
        "--custom-regex",
        type=str,
        help="Regex personnalisée pour détecter des URLs d'images"
    )
    detection_group.add_argument(
        "--max-images",
        type=int,
        help="Nombre maximum d'images à télécharger"
    )
    
    # Groupe Selenium
    selenium_group = parser.add_argument_group("Selenium (contenu dynamique)")
    selenium_group.add_argument(
        "--selenium",
        action="store_true",
        help="Utiliser Selenium pour le rendu JavaScript"
    )
    selenium_group.add_argument(
        "--scroll",
        action="store_true",
        help="Activer le défilement automatique avec Selenium"
    )
    selenium_group.add_argument(
        "--scroll-times",
        type=int,
        default=3,
        help="Nombre de défilements (défaut: 3)"
    )
    selenium_group.add_argument(
        "--scroll-delay",
        type=float,
        default=1.5,
        help="Délai entre les défilements en secondes (défaut: 1.5)"
    )
    
    # Groupe filtrage
    filter_group = parser.add_argument_group("Filtrage")
    filter_group.add_argument(
        "--extensions",
        type=str,
        help="Extensions d'images à garder (ex: jpg,png,webp)"
    )
    filter_group.add_argument(
        "--min-size",
        type=int,
        default=0,
        help="Taille minimale en octets"
    )
    filter_group.add_argument(
        "--max-size",
        type=int,
        help="Taille maximale en octets"
    )
    filter_group.add_argument(
        "--min-width",
        type=int,
        help="Largeur minimale en pixels"
    )
    filter_group.add_argument(
        "--min-height",
        type=int,
        help="Hauteur minimale en pixels"
    )
    filter_group.add_argument(
        "--blacklist-domains",
        type=str,
        help="Domaines à ignorer, séparés par des virgules"
    )
    filter_group.add_argument(
        "--whitelist-domains",
        type=str,
        help="Domaines autorisés, séparés par des virgules"
    )
    
    # Groupe téléchargement
    dl_group = parser.add_argument_group("Téléchargement")
    dl_group.add_argument(
        "-t", "--threads",
        type=int,
        default=5,
        help="Nombre de threads de téléchargement (défaut: 5)"
    )
    dl_group.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout des requêtes en secondes (défaut: 30)"
    )
    dl_group.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Nombre de tentatives en cas d'échec (défaut: 3)"
    )
    dl_group.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Délai entre les requêtes en secondes"
    )
    dl_group.add_argument(
        "--no-resume",
        action="store_true",
        help="Ne pas reprendre les téléchargements existants"
    )
    dl_group.add_argument(
        "--overwrite",
        action="store_true",
        help="Écraser les fichiers existants"
    )
    
    # Groupe réseau
    net_group = parser.add_argument_group("Réseau")
    net_group.add_argument(
        "--user-agent",
        type=str,
        help="User-Agent personnalisé"
    )
    net_group.add_argument(
        "--rotate-ua",
        action="store_true",
        help="Roter les User-Agents à chaque requête"
    )
    net_group.add_argument(
        "--headers",
        type=str,
        help="Headers JSON personnalisés"
    )
    net_group.add_argument(
        "--cookies",
        type=str,
        help="Cookies JSON personnalisés"
    )
    net_group.add_argument(
        "--auth",
        type=str,
        help="Authentification Basic user:password"
    )
    net_group.add_argument(
        "--proxy",
        type=str,
        help="Proxy HTTP/SOCKS (ex: http://proxy:8080)"
    )
    net_group.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Désactiver la vérification SSL"
    )
    net_group.add_argument(
        "--respect-robots",
        action="store_true",
        help="Respecter le robots.txt"
    )
    
    # Groupe traitement
    process_group = parser.add_argument_group("Traitement")
    process_group.add_argument(
        "--convert",
        type=str,
        choices=["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"],
        help="Convertir les images dans ce format"
    )
    process_group.add_argument(
        "--thumbnails",
        type=str,
        nargs="?",
        const="200x200",
        help="Générer des miniatures (taille: LxH, défaut: 200x200)"
    )
    
    # Groupe organisation
    org_group = parser.add_argument_group("Organisation")
    org_group.add_argument(
        "--no-organize-domain",
        action="store_true",
        help="Ne pas organiser par domaine"
    )
    org_group.add_argument(
        "--organize-date",
        action="store_true",
        help="Organiser par date"
    )
    org_group.add_argument(
        "--filename-template",
        type=str,
        default="{index:04d}_{name}_{width}x{height}{ext}",
        help="Template du nom de fichier"
    )
    
    # Groupe export
    export_group = parser.add_argument_group("Export")
    export_group.add_argument(
        "--export-json",
        action="store_true",
        help="Exporter les métadonnées en JSON"
    )
    export_group.add_argument(
        "--export-csv",
        action="store_true",
        help="Exporter les métadonnées en CSV"
    )
    export_group.add_argument(
        "--export-excel",
        action="store_true",
        help="Exporter les métadonnées en Excel"
    )
    export_group.add_argument(
        "--no-export-metadata",
        action="store_true",
        help="Ne pas exporter les métadonnées"
    )
    
    # Groupe avancé
    advanced_group = parser.add_argument_group("Avancé")
    advanced_group.add_argument(
        "--save-source",
        action="store_true",
        help="Sauvegarder le source HTML des pages"
    )
    advanced_group.add_argument(
        "--source-dir",
        type=str,
        default="./noexi_page_sources",
        help="Répertoire pour les sources HTML"
    )
    
    # Groupe logs
    log_group = parser.add_argument_group("Logs")
    log_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mode verbeux"
    )
    log_group.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Mode silencieux"
    )
    log_group.add_argument(
        "--log-file",
        type=str,
        help="Fichier de log"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    return parser


def parse_args_to_config(args: argparse.Namespace) -> DownloaderConfig:
    """
    Convertit les arguments CLI en DownloaderConfig.
    
    Args:
        args: Arguments parsés
        
    Returns:
        DownloaderConfig
    """
    config = DownloaderConfig()
    
    # URLs
    if args.url:
        config.urls = [args.url]
    elif args.url_list:
        with open(args.url_list, "r", encoding="utf-8") as f:
            config.urls = [line.strip() for line in f if line.strip()]
    elif args.config:
        file_config = load_config_from_file(args.config)
        config = DownloaderConfig(**file_config)
        return config
    
    # Sortie
    config.output_dir = args.output
    
    # Détection
    config.include_external = not args.no_external
    config.extract_css = not args.no_css
    config.extract_js = not args.no_js
    config.extract_iframes = not args.no_iframes
    config.extract_base64 = not args.no_base64
    config.custom_regex = args.custom_regex
    config.max_images = args.max_images
    
    # Selenium
    config.use_selenium = args.selenium
    config.scroll_pages = args.scroll
    config.scroll_times = args.scroll_times
    config.scroll_delay = args.scroll_delay
    
    # Filtrage
    if args.extensions:
        config.extensions = ["." + ext.strip().lstrip(".") for ext in args.extensions.split(",")]
    config.min_size = args.min_size
    config.max_size = args.max_size
    config.min_width = args.min_width
    config.min_height = args.min_height
    if args.blacklist_domains:
        config.blacklist_domains = [d.strip() for d in args.blacklist_domains.split(",")]
    if args.whitelist_domains:
        config.whitelist_domains = [d.strip() for d in args.whitelist_domains.split(",")]
    
    # Téléchargement
    config.threads = args.threads
    config.timeout = args.timeout
    config.retries = args.retries
    config.delay = args.delay
    config.resume = not args.no_resume
    config.no_overwrite = not args.overwrite
    
    # Réseau
    config.user_agent = args.user_agent
    config.rotate_ua = args.rotate_ua
    if args.headers:
        config.headers = json.loads(args.headers)
    if args.cookies:
        config.cookies = json.loads(args.cookies)
    if args.auth:
        config.auth = tuple(args.auth.split(":", 1))
    config.proxy = args.proxy
    config.verify_ssl = not args.no_verify_ssl
    config.respect_robots = args.respect_robots
    
    # Traitement
    config.convert_format = args.convert
    if args.thumbnails:
        parts = args.thumbnails.split("x")
        if len(parts) == 2:
            config.thumbnail_size = (int(parts[0]), int(parts[1]))
    
    # Organisation
    config.organize_by_domain = not args.no_organize_domain
    config.organize_by_date = args.organize_date
    config.filename_template = args.filename_template
    
    # Export
    config.export_json = args.export_json
    config.export_csv = args.export_csv
    config.export_excel = args.export_excel
    config.export_metadata = not args.no_export_metadata
    
    # Avancé
    config.save_page_source = args.save_source
    config.page_source_dir = args.source_dir
    
    # Logs
    config.verbose = args.verbose
    config.silent = args.quiet
    config.log_file = args.log_file
    
    return config


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    """
    Point d'entrée principal.
    
    Returns:
        Code de sortie
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        config = parse_args_to_config(args)
        downloader = NoexiImageDownloader(config)
        downloader.run()
        return 0
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        return 130
    except Exception as e:
        print(f"Erreur fatale: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
