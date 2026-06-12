from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import COLORS, COATINGS


def kb_colors() -> InlineKeyboardMarkup:
    buttons, row = [], []
    for key, (label, _) in COLORS.items():
        row.append(InlineKeyboardButton(text=label, callback_data=f"color:{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_coatings() -> InlineKeyboardMarkup:
    buttons, row = [], []
    for key, (label, _) in COATINGS.items():
        row.append(InlineKeyboardButton(text=label, callback_data=f"coating:{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_colors")])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_after_result() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Другой цвет / покрытие", callback_data="retry")],
        [InlineKeyboardButton(text="📸 Новое фото",             callback_data="new_photo")],
    ])