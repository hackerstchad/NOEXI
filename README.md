# 🚀 NOEXI Advanced Image Downloader

<p align="center">
  <span style="color: #00ff00; font-size: 48px; font-weight: bold;">NOEXI</span>
</p>

<p align="center">
  <strong style="color: #00ff00;">Téléchargeur d'images web ultra-avancé</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-8.0.0-brightgreen?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-brightgreen?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/licence-MIT-brightgreen?style=for-the-badge" alt="Licence">
</p>

---

## 📋 Description

**NOEXI Advanced Image Downloader** est un script Python ultra-avancé permettant de télécharger automatiquement toutes les images présentes sur un site web, qu'elles soient :

- 🖼️ En HTML standard (`<img>`, `<picture>`, `<source>`)
- 🎨 En arrière-plan CSS (`background-image`)
- ⚡ Dans des scripts JavaScript (`data-src`, lazy-loading, JSON)
- 🔲 Dans des iframes et frames
- 📄 Dans des feuilles de style externes (`.css`)
- 📜 Dans des fichiers JavaScript externes (`.js`)
- 🎠 Dans des carrousels, galeries, modals
- 🤖 Générées dynamiquement par JavaScript (via Selenium)
- 🔐 Derrière une authentification ou un proxy

---

## ✨ Fonctionnalités principales

| Fonctionnalité | Description |
|----------------|-------------|
| ✅ **Multi-sources** | Images internes, externes, CSS, JS, iframes, base64 |
| ✅ **Lazy-loading** | Détection `data-src`, `data-srcset`, `srcset` |
| ✅ **Filtrage avancé** | Extension, taille, dimensions, type MIME |
| ✅ **Barre de progression** | Temps réel avec `tqdm` et `rich` |
| ✅ **Multi-threading** | Téléchargement parallèle rapide |
| ✅ **Reprise** | Reprise après interruption (resume) |
| ✅ **Conversion** | Convertir en webp, png, jpg, etc. |
| ✅ **Miniatures** | Génération de thumbnails |
| ✅ **Hash** | Vérification MD5 / SHA256 |
| ✅ **Proxy / Auth** | Support SOCKS/HTTP et authentification |
| ✅ **Selenium** | Mode headless pour sites dynamiques |
| ✅ **Export** | CSV, JSON, Excel des métadonnées |
| ✅ **Logs** | Journalisation complète |
| ✅ **robots.txt** | Respect optionnel |
| ✅ **Rate limiting** | Limitation du débit |
| ✅ **User-Agent** | Rotation automatique |

---

## 🛠️ Installation

### 1. Cloner / télécharger le projet

```bash
git clone https://github.com/votre-repo/noexi-image-downloader.git
cd noexi-image-downloader
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer ChromeDriver (si utilisation de Selenium)

Le script utilise `webdriver-manager` pour gérer automatiquement ChromeDriver.
Assurez-vous d'avoir Google Chrome installé.

---

## 🚀 Utilisation rapide

### Télécharger les images d'une URL simple

```bash
python noexi_image_downloader.py -u "https://example.com"
```

### Spécifier un répertoire de sortie

```bash
python noexi_image_downloader.py -u "https://example.com" -o ./mes_images
```

### Utiliser Selenium pour les sites dynamiques

```bash
python noexi_image_downloader.py -u "https://example.com" --selenium --scroll
```

### Convertir toutes les images en WebP + miniatures

```bash
python noexi_image_downloader.py -u "https://example.com" \
  --convert webp --thumbnails 300x300
```

### Utiliser un proxy et une authentification

```bash
python noexi_image_downloader.py -u "https://example.com" \
  --proxy "http://user:pass@proxy:8080" --auth "user:password"
```

### Télécharger depuis une liste d'URLs

```bash
python noexi_image_downloader.py --url-list urls.txt -t 10
```

---

## 📚 Options disponibles

### Groupe URL

| Option | Description |
|--------|-------------|
| `-u, --url` | URL du site web à analyser |
| `--url-list` | Fichier contenant une liste d'URLs |
| `--config` | Fichier de configuration JSON/YAML |

### Groupe détection

| Option | Description |
|--------|-------------|
| `--no-external` | Ne pas télécharger les images externes |
| `--no-css` | Ne pas extraire les images du CSS |
| `--no-js` | Ne pas extraire les images du JavaScript |
| `--no-iframes` | Ne pas analyser les iframes |
| `--no-base64` | Ne pas extraire les images base64 inline |
| `--custom-regex` | Regex personnalisée pour détecter des URLs |
| `--max-images` | Nombre maximum d'images à télécharger |

### Groupe Selenium

| Option | Description |
|--------|-------------|
| `--selenium` | Utiliser Selenium pour le rendu JS |
| `--scroll` | Activer le défilement automatique |
| `--scroll-times` | Nombre de défilements (défaut: 3) |
| `--scroll-delay` | Délai entre défilements (défaut: 1.5s) |

### Groupe filtrage

| Option | Description |
|--------|-------------|
| `--extensions` | Extensions à garder (ex: jpg,png,webp) |
| `--min-size` | Taille minimale en octets |
| `--max-size` | Taille maximale en octets |
| `--min-width` | Largeur minimale en pixels |
| `--min-height` | Hauteur minimale en pixels |
| `--blacklist-domains` | Domaines à ignorer |
| `--whitelist-domains` | Domaines autorisés |

### Groupe téléchargement

| Option | Description |
|--------|-------------|
| `-t, --threads` | Nombre de threads (défaut: 5) |
| `--timeout` | Timeout des requêtes (défaut: 30s) |
| `--retries` | Nombre de tentatives (défaut: 3) |
| `--delay` | Délai entre requêtes |
| `--no-resume` | Ne pas reprendre les téléchargements |
| `--overwrite` | Écraser les fichiers existants |

### Groupe réseau

| Option | Description |
|--------|-------------|
| `--user-agent` | User-Agent personnalisé |
| `--rotate-ua` | Roter les User-Agents |
| `--headers` | Headers JSON personnalisés |
| `--cookies` | Cookies JSON personnalisés |
| `--auth` | Authentification Basic user:password |
| `--proxy` | Proxy HTTP/SOCKS |
| `--no-verify-ssl` | Désactiver la vérification SSL |
| `--respect-robots` | Respecter le robots.txt |

### Groupe traitement

| Option | Description |
|--------|-------------|
| `--convert` | Convertir les images (jpg/png/webp/gif/bmp/tiff) |
| `--thumbnails` | Générer des miniatures (ex: 300x300) |

### Groupe export

| Option | Description |
|--------|-------------|
| `--export-json` | Exporter en JSON |
| `--export-csv` | Exporter en CSV |
| `--export-excel` | Exporter en Excel |
| `--no-export-metadata` | Ne pas exporter les métadonnées |

### Groupe logs

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Mode verbeux |
| `-q, --quiet` | Mode silencieux |
| `--log-file` | Fichier de log |

---

## 📁 Structure des fichiers

```
noexi-image-downloader/
├── noexi_image_downloader.py   # Script principal (2000+ lignes)
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
└── noexi_downloads/            # Répertoire de sortie par défaut
    ├── example.com/
    │   ├── 0001_image_1920x1080.jpg
    │   ├── 0002_logo_512x512.png
    │   └── thumbs/
    └── noexi_metadata_*.json
```

---

## 🧪 Exemples avancés

### Télécharger uniquement les images > 100 Ko et > 500px de large

```bash
python noexi_image_downloader.py -u "https://example.com" \
  --min-size 102400 --min-width 500 --extensions jpg,png,webp
```

### Télécharger avec authentification et sauvegarde du source

```bash
python noexi_image_downloader.py -u "https://example.com" \
  --auth "admin:secret" --save-source --verbose
```

### Export complet des métadonnées

```bash
python noexi_image_downloader.py -u "https://example.com" \
  --export-json --export-csv --export-excel
```

### Utilisation avec un fichier de configuration

Créer `config.json` :

```json
{
  "urls": ["https://example.com"],
  "output_dir": "./mes_images",
  "threads": 10,
  "convert_format": "webp",
  "thumbnail_size": [300, 300],
  "export_json": true,
  "export_csv": true
}
```

Puis exécuter :

```bash
python noexi_image_downloader.py --config config.json
```

---

## ⚙️ Configuration via JSON/YAML

Le script accepte un fichier de configuration complet. Tous les champs de `DownloaderConfig` sont supportés.

Exemple `config.yaml` :

```yaml
urls:
  - https://example.com
  - https://another-site.com
output_dir: ./downloads
threads: 8
use_selenium: true
scroll_pages: true
convert_format: webp
thumbnail_size: [300, 300]
export_json: true
export_csv: true
organize_by_domain: true
respect_robots: true
```

---

## 🔒 Respect légal et éthique

Ce script est destiné à un usage légal et éthique. Avant de télécharger des images :

1. Vérifiez les conditions d'utilisation du site cible.
2. Respectez le `robots.txt` si l'option `--respect-robots` est activée.
3. Ne téléchargez pas de contenu protégé par des droits d'auteur sans autorisation.
4. Utilisez des délais raisonnables (`--delay`) pour ne pas surcharger les serveurs.

---

## 🐛 Dépannage

### `ModuleNotFoundError: No module named 'requests'`

```bash
pip install -r requirements.txt
```

### Selenium ne trouve pas ChromeDriver

Installez `webdriver-manager` et Google Chrome :

```bash
pip install webdriver-manager selenium
```

Assurez-vous que Chrome est dans le PATH.

### Erreur SSL

```bash
python noexi_image_downloader.py -u "https://example.com" --no-verify-ssl
```

### Peu d'images détectées

Essayez le mode Selenium pour les sites à contenu dynamique :

```bash
python noexi_image_downloader.py -u "https://example.com" --selenium --scroll
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

## 📜 Licence

Ce projet est sous licence MIT.

---

<p align="center">
  <strong style="color: #00ff00;">NOEXI</strong> — Téléchargez le web en vert. 💚
</p>
