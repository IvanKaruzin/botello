import asyncio
import os
from dotenv import load_dotenv

from telegram_bot import TelegramBot
from discord_bot import DiscordBot

 
async def main():
    # Загружаем токены
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

    print("Запуск Telegram и Discord ботов...")

    # Создаём экземпляры ботов
    discord_bot = DiscordBot(DISCORD_TOKEN)
    telegram_bot = TelegramBot(TELEGRAM_TOKEN, discord_bot.bot)

    # Инициализируем Telegram
    await telegram_bot.app.initialize()
    await telegram_bot.app.start()

    # Запускаем оба бота параллельно
    await asyncio.gather(
        telegram_bot.app.updater.start_polling(),
        discord_bot.bot.start(DISCORD_TOKEN),
    )


if __name__ == "__main__":
    asyncio.run(main())
