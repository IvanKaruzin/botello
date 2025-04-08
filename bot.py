import asyncio
import nest_asyncio
from telegram import Update
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import re


nest_asyncio.apply()

# === Токены и настройки ===
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
TELEGRAM_TOPIC_ID = int(os.getenv("TELEGRAM_TOPIC_ID"))

# === Telegram ===
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()
telegram_bot = Bot(token=TELEGRAM_TOKEN)


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
    #await update.message.reply_text("Привет из Telegram!")
    chat = update.effective_chat
    await update.message.reply_text(f"Chat ID: {chat.id}")


telegram_app.add_handler(CommandHandler("start", tg_start))
telegram_app.add_handler(CommandHandler("voice", voice_command))

# === Discord ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

discord_bot = commands.Bot(command_prefix="!", intents=intents)


@discord_bot.event
async def on_message(message):
    # Игнорировать свои сообщения
    if message.author == discord_bot.user:
        return

    await discord_bot.process_commands(message)

    # Получаем имя и текст
    author_name = message.author.display_name
    content_text = f"*{author_name}* в Discord:\n{message.content or '📷'}"

    # Если есть вложения (attachments)
    if message.attachments:
        for attachment in message.attachments:
            # Проверим, является ли файл изображением
            if attachment.content_type and attachment.content_type.startswith(
                    "image/"):
                # Скачиваем и отправляем изображение с подписью
                await telegram_bot.send_photo(
                    chat_id=TELEGRAM_CHAT_ID,
                    photo=attachment.url,
                    caption=content_text,
                    parse_mode="Markdown",
                    message_thread_id=TELEGRAM_TOPIC_ID)
                return  # Отправили — выходим
            else:
                # Другой тип файла — отправим как ссылку
                await telegram_bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=f"{content_text}\n\n📎 Вложение: {attachment.url}",
                    parse_mode="Markdown",
                    message_thread_id=TELEGRAM_TOPIC_ID)
                return

    # Если просто текстовое сообщение
    if message.content:
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                                        text=content_text,
                                        parse_mode="Markdown",
                                        message_thread_id=TELEGRAM_TOPIC_ID)


@discord_bot.event
async def on_ready():
    print(f"[Discord] Бот запущен как {discord_bot.user}")
    for guild in discord_bot.guilds:
        print(f"🛡️ Сервер: {guild.name}")
        for channel in guild.text_channels:
            print(f"  📺 Канал: {channel.name} (ID: {channel.id})")


@discord_bot.event
async def on_connect():
    try:
        synced = await discord_bot.tree.sync()
        print(f"Slash-команды синхронизированы: {len(synced)} шт.")
    except Exception as e:
        print(f"Ошибка при sync: {e}")


@discord_bot.tree.command(name="dice",
                          description="Кинуть кубик с заданным числом граней")
async def dice(interaction: discord.Interaction, sides: str = "6"):
    # Парсим число граней
    match = re.search(r'(\d+)', sides)
    arg = int(match.group(1)) if match else 6

    # Проверка на минимальное количество граней
    if arg < 2:
        await interaction.response.send_message(
            "ИДИОТ! 🎲 Кубик должен иметь минимум 2 грани!", ephemeral=False)
        return

    # Бросок кубика
    number = random.randint(1, arg)
    await interaction.response.send_message(f"🎲 Выпало: {number} (из {arg})",
                                            ephemeral=False)


@discord_bot.command(name="dice")
async def dice_text(ctx, arg: str = "6"):
    import re

    # Парсим число: либо просто число, либо что-то вроде dice100
    match = re.search(r'(\d+)', arg)
    sides = int(match.group(1)) if match else 6

    if sides < 2:
        await ctx.send("ИДИОТ! 🎲 Кубик должен иметь минимум 2 грани!")
        return

    number = random.randint(1, sides)
    await ctx.send(f"🎲 Выпало: {number} (из {sides})")


@discord_bot.command(name="choose")
async def dice_text(ctx, *args):
    number = random.randint(0, len(args) - 1)
    await ctx.send(f"Побеждает {args[number]}!")


@discord_bot.tree.command(name="choose")
async def dice_text(interaction: discord.Interaction, choices: str):
    number = random.randint(0, len(choices.split()) - 1)
    await interaction.response.send_message(
        f"Побеждает {choices.split()[number]}! ({choices})")


@discord_bot.command(name="purge")
async def purge(ctx, n: int = 5):
    # Получаем список последних n сообщений в текущем канале
    deleted = await ctx.channel.purge(
        limit=n, check=lambda message: message.author == discord_bot.user)

    # Информируем пользователя, сколько сообщений было удалено
    await ctx.send(f"Удалено {len(deleted)} сообщений от бота.",
                   delete_after=5)


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
