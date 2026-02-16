import asyncio
import discord
from discord.ext import commands
from database.base import init_db
from config import settings

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class AchieveBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("--- Database initialization ---")
        await init_db()
        print("--- Database ready ---")

        # await self.load_extension("cogs.goals")

        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


async def main():
    token = settings.DISCORD_TOKEN.get_secret_value()

    bot = AchieveBot()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
