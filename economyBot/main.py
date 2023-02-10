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

def loadBreads(interaction:discord.Interaction, member:discord.Member, data:dict):
    if interaction.guild.id not in data:
        data[interaction.guild.id] = {}
    if member.id not in data[interaction.guild.id]:
        data[interaction.guild.id][member.id] = 0
        saveData(DATA_FILE, data)
        return 0
    return data[interaction.guild.id][member.id]

def saveBreads(breads:int, data:dict, interaction:discord.Interaction):
    data[interaction.guild.id][interaction.user.id] = breads
    saveData(DATA_FILE, data)

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

@bot.tree.command(name="ping", description="Check breadManager's connection")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message(f"Pong! You are in {interaction.guild.name} server.")

@bot.tree.command(name="account_info", description="Get account information of a member or yourself")
async def account_info(interaction:discord.Interaction, member:discord.Member=None):
    if member == None:
        member = interaction.user
    breads = loadBreads(interaction, member, data)
    await interaction.response.send_message(f"{member.name} has {breads} breads.")

@bot.tree.command(name="guess_number", description="Guess the correct number(0/1) to win/lose breads!")
async def guess_number(interaction:discord.Interaction, guess:int):
    breads = loadBreads(interaction, interaction.user, data)
    num = random.choice([0, 1])
    if num == guess:
        breads += 5
        await interaction.response.send_message("Correct! You won 5 breads. :D")
    else:
        breads -= 5
        await interaction.response.send_message("Wrong, You lost 5 breads. D:")
    saveBreads(breads, data, interaction)

bot.run(TOKEN)