import logging
import os
import uuid

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import COLORS, COATINGS, UPLOADS_DIR
from keyboards import kb_after_result, kb_colors, kb_coatings
from states import CarState

logger = logging.getLogger(__name__)

router = Router()


# ─── Commands ────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я помогу визуализировать новый цвет твоей машины.\n\n"
        "📸 Отправь фото автомобиля — и я покажу как он будет выглядеть "
        "в любом цвете и покрытии.",
    )
    await state.set_state(CarState.waiting_photo)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🤖 <b>Как пользоваться ботом:</b>\n\n"
        "1. Отправь фото машины\n"
        "2. Выбери цвет\n"
        "3. Выбери тип покрытия\n"
        "4. Получи результат!\n\n"
        "⚡ Генерация занимает ~30–60 секунд\n"
        "📸 Лучший результат — фото сбоку на чистом фоне\n\n"
        "/start — начать заново\n"
        "/cancel — отменить",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено. Отправь новое фото когда будешь готов.")
    await state.set_state(CarState.waiting_photo)


# ─── Photo ───────────────────────────────────────────────────────────────────

@router.message(CarState.waiting_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    filename  = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(UPLOADS_DIR, filename)

    file = await message.bot.get_file(photo.file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    await state.update_data(image_path=file_path)
    logger.info(f"Фото сохранено: {file_path}")

    await message.answer("✅ Фото получено!\n\n🎨 Выбери цвет:", reply_markup=kb_colors())
    await state.set_state(CarState.waiting_color)


@router.message(CarState.waiting_photo)
async def handle_no_photo(message: Message):
    await message.answer(
        "📸 Пожалуйста, отправь <b>фото</b> автомобиля.",
        parse_mode=ParseMode.HTML,
    )


# ─── Color ───────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("color:"))
async def handle_color(callback: CallbackQuery, state: FSMContext):
    color_key = callback.data.split(":")[1]
    if color_key not in COLORS:
        await callback.answer("Неизвестный цвет", show_alert=True)
        return

    color_label, color_value = COLORS[color_key]
    await state.update_data(color_label=color_label, color_value=color_value)

    await callback.message.edit_text(
        f"🎨 Цвет: <b>{color_label}</b>\n\n✨ Теперь выбери тип покрытия:",
        reply_markup=kb_coatings(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(CarState.waiting_coating)
    await callback.answer()


@router.callback_query(F.data == "back_to_colors")
async def handle_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🎨 Выбери цвет:", reply_markup=kb_colors())
    await state.set_state(CarState.waiting_color)
    await callback.answer()


# ─── Coating + Generation ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("coating:"))
async def handle_coating(callback: CallbackQuery, state: FSMContext):
    coating_key = callback.data.split(":")[1]
    if coating_key not in COATINGS:
        await callback.answer("Неизвестное покрытие", show_alert=True)
        return

    coating_label, coating_value = COATINGS[coating_key]
    data = await state.get_data()

    color_label = data.get("color_label", "")
    color_value = data.get("color_value", "")
    image_path  = data.get("image_path", "")

    await state.set_state(CarState.generating)
    await callback.message.edit_text(
        f"⚙️ Генерирую...\n\n"
        f"🎨 Цвет: <b>{color_label}</b>\n"
        f"✨ Покрытие: <b>{coating_label}</b>\n\n"
        f"⏳ Это займёт ~30–60 секунд, подожди...",
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()

    try:
        from ai import generate
        result_path = await generate(
            image_path=image_path,
            color=color_value,
            coating=coating_value,
        )

        await callback.message.answer_photo(
            photo=FSInputFile(result_path),
            caption=(
                f"✅ Готово!\n\n"
                f"🎨 Цвет: <b>{color_label}</b>\n"
                f"✨ Покрытие: <b>{coating_label}</b>"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=kb_after_result(),
        )
        await callback.message.edit_text("✅ Генерация завершена!")
        logger.info(f"Результат отправлен: {result_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации: {e}", exc_info=True)
        await callback.message.edit_text(
            "❌ Ошибка при генерации.\n\n"
            "Возможные причины:\n"
            "• Проблема с HF_TOKEN\n"
            "• Модель перегружена — попробуй через минуту\n\n"
            "Отправь фото снова для повторной попытки."
        )
        await state.set_state(CarState.waiting_photo)
        return

    await state.update_data(coating_label=coating_label, coating_value=coating_value)
    await state.set_state(CarState.waiting_photo)


# ─── After result ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "retry")
async def handle_retry(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("image_path") or not os.path.exists(data["image_path"]):
        await callback.answer("Фото не найдено, отправь новое", show_alert=True)
        await state.set_state(CarState.waiting_photo)
        return
    await callback.message.edit_text("🎨 Выбери новый цвет:", reply_markup=kb_colors())
    await state.set_state(CarState.waiting_color)
    await callback.answer()


@router.callback_query(F.data == "new_photo")
async def handle_new_photo(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("📸 Отправь новое фото автомобиля!")
    await state.set_state(CarState.waiting_photo)
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def handle_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отменено.\n\n📸 Отправь фото когда будешь готов.")
    await state.set_state(CarState.waiting_photo)
    await callback.answer()


# ─── Fallback ────────────────────────────────────────────────────────────────

@router.message()
async def handle_unknown(message: Message, state: FSMContext):
    current = await state.get_state()
    if current == CarState.generating.state:
        await message.answer("⏳ Подожди, идёт генерация...")
    else:
        await message.answer("📸 Отправь фото автомобиля чтобы начать.\nПомощь: /help")
        await state.set_state(CarState.waiting_photo)