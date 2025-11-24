# bot.py
import os, json, uuid, requests
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL","https://replace-later")
HW_FILE = "hwids.json"

if os.path.exists(HW_FILE):
    with open(HW_FILE,"r") as f: HW = json.load(f)
else:
    HW = {}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def save_hw():
    with open(HW_FILE,"w") as f: json.dump(HW,f)

@bot.event
async def on_ready():
    print("Bot ready", bot.user)
    try:
        await bot.tree.sync()
    except Exception as e:
        print("sync failed", e)

@bot.tree.command(name="gethwid", description="Get your HWID (DM)")
async def gethwid(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in HW:
        HW[user_id] = str(uuid.uuid4()); save_hw()
    await interaction.response.defer(ephemeral=True)
    await interaction.user.send(f"Your HWID (keep secret): `{HW[user_id]}`")
    await interaction.followup.send("HWID sent via DM.", ephemeral=True)

@bot.tree.command(name="set", description="Bind a key to your HWID for 24 hours")
@app_commands.describe(key="The key to bind")
async def set_cmd(interaction: discord.Interaction, key: str):
    user_id = str(interaction.user.id)
    hwid = HW.get(user_id)
    if not hwid:
        await interaction.response.send_message("Run /gethwid first.", ephemeral=True); return
    try:
        resp = requests.post(f"{API_URL}/bind_key", json={"key":key,"hwid":hwid})
        if resp.status_code == 200:
            await interaction.response.send_message("Key bound to your HWID for 24 hours.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Failed: {resp.text}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

bot.run(TOKEN)
