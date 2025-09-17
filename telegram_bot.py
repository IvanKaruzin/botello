import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes


class TelegramBot:
    def __init__(self, telegram_token, discord_bot):
        self.telegram_token = telegram_token
        self.discord_bot = discord_bot

        self.app = Application.builder().token(self.telegram_token).build()
        self.bot = Bot(token=self.telegram_token)

        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.tg_start))
        self.app.add_handler(CommandHandler("voice", self.voice_command))

    async def get_voice_members(self):
        report = ""
        for guild in self.discord_bot.guilds:
            for channel in guild.voice_channels:
                if channel.members:
                    report += f"🎧 *{channel.name}* ({guild.name}):\n"
                    for member in channel.members:
                        report += f"  - {member.display_name}\n"
        return report or "Никого нет в голосовых каналах."

    async def voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        report = await self.get_voice_members()
        await update.message.reply_text(report, parse_mode="Markdown")

    async def tg_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        await update.message.reply_text(f"Chat ID: {chat.id}")

    def run(self):
        self.app.run_polling()
