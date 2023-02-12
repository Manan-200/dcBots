import discord
from discord.ext import commands
import json
import random

DATA_FILE = "data.json"

def loadData(filePath:str):
    try:
        with open(filePath, "r") as file:
            return(json.load(file))
    except:
        return {}

def saveData(filePath:str, data:dict):
    with open(filePath, "w") as file:
        json.dump(data, file)

def loadBreads(guildID:discord.Interaction.guild_id, memberID:discord.Member.id, data:dict):
    if str(guildID) not in data:
        data[str(guildID)] = {}
        data[str(guildID)][str(memberID)] = 0
        saveData(DATA_FILE, data)
        return 0
    if str(memberID) not in data[str(guildID)]:
        data[str(guildID)][str(memberID)] = 0
        saveData(DATA_FILE, data)
        return 0
    return data[str(guildID)][str(memberID)]

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

@bot.tree.command(name="ping", description="Check breadManager's connection")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message(f"Pong! You are in {interaction.guild.name} server.")

@bot.tree.command(name="account_info", description="Get account information of a member or yourself")
async def account_info(interaction:discord.Interaction, member:discord.Member=None):
    if member == None:
        member = interaction.user
    data = loadData(DATA_FILE)
    breads = loadBreads(interaction.guild_id, member.id, data)
    await interaction.response.send_message(f"{member.name} has {breads} breads.")

@bot.tree.command(name="guess_number", description="Guess the correct number(0/1) to win/lose breads!")
async def guess_number(interaction:discord.Interaction, guess:int):
    data = loadData(DATA_FILE)
    breads = loadBreads(interaction.guild_id, interaction.user.id, data)
    num = random.choice([0, 1])
    if num == guess:
        breads += 5
        await interaction.response.send_message("Correct! You won 5 breads. :D")
    else:
        breads -= 5
        await interaction.response.send_message("Wrong, You lost 5 breads. D:")
    data[str(interaction.guild.id)][str(interaction.user.id)] = breads
    saveData(DATA_FILE, data)

bot.run(TOKEN)