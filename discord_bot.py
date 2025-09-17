import discord
from discord.ext import commands
import random
import re


class DiscordBot:
    def __init__(self, token: str):
        self.token = token

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.slash_command_responses = {}

        # Регистрируем обработчики и команды
        self.setup_events()
        self.setup_commands()

    def setup_events(self):
        @self.bot.event
        async def on_ready():
            print(f"[Discord] Бот запущен как {self.bot.user}")
            for guild in self.bot.guilds:
                print(f"🛡️ Сервер: {guild.name}")
                for channel in guild.text_channels:
                    print(f"  📺 Канал: {channel.name} (ID: {channel.id})")

        @self.bot.event
        async def on_connect():
            try:
                synced = await self.bot.tree.sync()
                print(f"Slash-команды синхронизированы: {len(synced)} шт.")
            except Exception as e:
                print(f"Ошибка при sync: {e}")

    def setup_commands(self):
        # === SLASH команды ===
        @self.bot.tree.command(name="dice", description="Кинуть кубик с заданным числом граней")
        async def dice(interaction: discord.Interaction, sides: str = "6"):
            match = re.search(r'(\d+)', sides)
            arg = int(match.group(1)) if match else 6

            if arg < 2:
                await interaction.response.send_message(
                    "❌ Кубик должен иметь минимум 2 грани!", ephemeral=False
                )
                return

            number = random.randint(1, arg)
            await interaction.response.send_message(f"🎲 Выпало: {number} (из {arg})")
            message = await interaction.original_response()
            self.track_slash_response(interaction.channel.id, message)

        @self.bot.tree.command(name="choose", description="Выбор из нескольких вариантов.")
        async def choose(interaction: discord.Interaction, choices: str):
            options = choices.split()
            number = random.randint(0, len(options) - 1)
            await interaction.response.send_message(
                f"✅ Побеждает {options[number]}! ({choices})"
            )
            message = await interaction.original_response()
            self.track_slash_response(interaction.channel.id, message)

        # === PREFIX команды ===
        @self.bot.command(name="purge")
        async def purge(ctx, n: int = 5):
            deleted = await ctx.channel.purge(
                limit=n, check=lambda message: message.author == self.bot.user
            )
            await ctx.send(f"🗑️ Удалено {len(deleted)} сообщений от бота.", delete_after=5)

        @self.bot.command(name="purge_slash")
        async def clear_slash_replies(ctx, count: int = 1):
            channel_id = ctx.channel.id

            if channel_id not in self.slash_command_responses or not self.slash_command_responses[channel_id]:
                await ctx.send("❌ Нет ответов на слеш-команды в этом канале.", delete_after=5)
                await ctx.message.delete(delay=5)
                return

            deleted = 0
            for msg in self.slash_command_responses[channel_id][-count:]:
                try:
                    await msg.delete()
                    deleted += 1
                except discord.NotFound:
                    continue
                except discord.Forbidden:
                    await ctx.send("⚠️ Нет прав удалять сообщения!", delete_after=5)
                    await ctx.message.delete(delay=5)
                    return

            self.slash_command_responses[channel_id] = self.slash_command_responses[channel_id][:-deleted]
            await ctx.send(f"✅ Удалено {deleted} ответов на слеш-команды.", delete_after=5)
            await ctx.message.delete(delay=5)

    def track_slash_response(self, channel_id: int, message: discord.Message):
        """Запоминает сообщения-ответы на slash-команды"""
        if channel_id not in self.slash_command_responses:
            self.slash_command_responses[channel_id] = []
        self.slash_command_responses[channel_id].append(message)

    def run(self):
        self.bot.run(self.token)
