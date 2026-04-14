"""サイト設定"""

from pathlib import Path

# パス設定
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EVENTS_DIR = DATA_DIR / "events"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
ASSETS_DIR = PROJECT_ROOT / "assets"
OUTPUT_DIR = PROJECT_ROOT / "output"

# サイト設定
SITE_NAME = "My Community"
SITE_TITLE = "My Community Portal"
SITE_DESCRIPTION = "エンジニア達のLTイベント - 発表資料アーカイブ"
SITE_URL = "https://unsolublesugar.github.io/engineer-community-portal"  # デプロイ後に設定（例: "https://username.github.io/engineer-community-portal"）
SITE_OG_IMAGE = ""  # OG画像のURL（例: "https://username.github.io/engineer-community-portal/images/og-image.png"）
