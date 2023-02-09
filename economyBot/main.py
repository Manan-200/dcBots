import discord
from discord.ext import commands
import json
import random

DATA_FILE = "data.json"

def loadData(dataFile:str):
    try:
        with open(dataFile, "r") as file:
            return(json.load(file))
    except:
        return {}

def saveData(dataFile:str, data:dict):
    with open(dataFile, "w") as file:
        json.dump(data, file)

TOKEN = loadData("token.json")["token"]

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="ping")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message(f"Pong! You are in {interaction.guild.name} server.")

bot.run(TOKEN)