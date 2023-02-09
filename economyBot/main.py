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
data = loadData(DATA_FILE)

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

@bot.tree.command(name="account_info")
async def account_info(interaction:discord.Interaction, user:discord.User=None):
    if user == None:
        user = interaction.user
    try:
        breads = data[interaction.guild.id][interaction.user.id]
    except:
        if interaction.guild.id not in data:
            data[interaction.guild.id] = {}
        data[interaction.guild.id][interaction.user.id] = 0
        breads = 0
        saveData(DATA_FILE, data)
    await interaction.response.send_message(f"{user.name} has {breads} breads.")

bot.run(TOKEN)