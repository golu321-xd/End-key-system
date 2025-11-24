import discord
from discord.ext import commands
import requests, os, uuid

TOKEN = os.environ.get("BOT_TOKEN")
API = os.environ.get("BASE_URL")
SECRET = os.environ.get("API_SECRET")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.command()
async def key(ctx):
    hwid = str(uuid.uuid4())
    key = str(uuid.uuid4())

    data = {"key": key, "hwid": hwid}
    requests.post(f"{API}/setkey", json=data, headers={"Authorization": SECRET})

    await ctx.author.send(f"Your Key: `{key}`\nYour HWID: `{hwid}`\nValid 24 Hours")
    await ctx.reply("Check your DM!")

@bot.command()
async def set(ctx, key, new_hwid):
    data = {"key": key, "hwid": new_hwid}
    requests.post(f"{API}/setkey", json=data, headers={"Authorization": SECRET})
    await ctx.reply("HWID Updated!")

bot.run(TOKEN)
