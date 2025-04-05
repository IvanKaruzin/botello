import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
import discord
from dotenv import load_dotenv
import os


nest_asyncio.apply()

# === Токены и настройки ===
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# === Telegram ===
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Эта функция получает список участников в голосовых каналах
async def get_voice_members():
    report = ""
    for guild in discord_bot.guilds:
        for channel in guild.voice_channels:
            if len(channel.members) > 0:
                report += f"🎧 *{channel.name}* ({guild.name}):\n"
                for member in channel.members:
                    report += f"  - {member.display_name}\n"
    return report or "Никого нет в голосовых каналах."

# Обработчик Telegram-команды /голос
async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report = await get_voice_members()
    await update.message.reply_text(report, parse_mode="Markdown")

# Telegram: команда /start
async def tg_start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет из Telegram!")

# Telegram: пересылка в Discord
async def tg_forward(update: Update, context: CallbackContext):
    text = update.message.text
    user = update.message.from_user.full_name

    # Отвечаем в Telegram
    await update.message.reply_text(f"Пересылаю в Discord: {text}")

    # Пересылаем в Discord
    if discord_bot.is_ready():
        channel = discord_bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(f"Сообщение из Telegram от **{user}**:\n{text}")

telegram_app.add_handler(CommandHandler("start", tg_start))
telegram_app.add_handler(CommandHandler("voice", voice_command))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tg_forward))

# === Discord ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True


discord_bot = discord.Client(intents=intents)

@discord_bot.event
async def on_ready():
    print(f"[Discord] Бот запущен как {discord_bot.user}")
    for guild in discord_bot.guilds:
        print(f"🛡️ Сервер: {guild.name}")
        for channel in guild.text_channels:
            print(f"  📺 Канал: {channel.name} (ID: {channel.id})")

# === Главная функция ===
async def main():
    print("Запуск Telegram и Discord ботов...")

    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()

    await discord_bot.start(DISCORD_TOKEN)

# === Запуск ===
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
