import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from config import UPLOADS_DIR, OUTPUTS_DIR
from handlers import router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
HF_TOKEN  = os.getenv("HF_TOKEN", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    me = await bot.get_me()
    logger.info(f"✅ Бот запущен: @{me.username}")
    logger.info(f"🤗 HF_TOKEN: {'✅ настроен' if HF_TOKEN else '❌ не установлен'}")


async def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен в .env")
        sys.exit(1)
    if not HF_TOKEN:
        logger.error("❌ HF_TOKEN не установлен в .env")
        sys.exit(1)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.startup.register(on_startup)

    logger.info("Запускаю бота...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())