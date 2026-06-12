import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
HF_TOKEN  = os.getenv("HF_TOKEN", "")

UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"

COATINGS: dict[str, tuple[str, str]] = {
    "gloss":     ("🔆 Глянец",    "glossy finish, mirror-like shine, wet look paint"),
    "matte":     ("🛡 Матовое",   "matte finish, flat no-gloss paint, satin matte"),
    "pearl":     ("✨ Перламутр", "pearlescent finish, iridescent shimmer, pearl effect"),
    "chrome":    ("🪙 Хром",      "chrome mirror finish, highly polished reflective chrome"),
    "carbon":    ("🕸 Карбон",    "carbon fiber wrap texture, dark weave pattern"),
    "chameleon": ("🌈 Хамелеон",  "color-shifting chameleon paint, iridescent color change effect"),
    "silk":      ("🤵 Шёлк",      "satin silk finish, semi-gloss smooth paint"),
    "frost":     ("🧊 Морозный",  "frosted ice effect paint, crystalline frost finish"),
}

COLORS: dict[str, tuple[str, str]] = {
    "white":   ("⚪ Белый",       "pure white"),
    "black":   ("⚫ Чёрный",      "jet black"),
    "red":     ("🔴 Красный",     "vibrant red"),
    "blue":    ("🔵 Синий",       "deep royal blue"),
    "green":   ("🟢 Зелёный",     "forest green"),
    "yellow":  ("🟡 Жёлтый",      "bright yellow"),
    "purple":  ("🟣 Фиолетовый",  "deep purple"),
    "gray":    ("🩶 Серый",       "metallic silver gray"),
    "brown":   ("🟤 Коричневый",  "chocolate brown"),
    "orange":  ("🟠 Оранжевый",   "burnt orange"),
    "khaki":   ("🌿 Хаки",        "military olive khaki"),
    "gold":    ("🪙 Золотой",     "metallic gold"),
    "teal":    ("🩵 Бирюзовый",   "turquoise teal"),
    "pink":    ("🌸 Розовый",     "hot pink"),
}