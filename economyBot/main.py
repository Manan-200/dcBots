from discord.ext import commands
from dotenv import dotenv_values
from keep_alive import keep_alive
import discord
import json
import random

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
        data[str(guildID)][str(memberID)] = {}
        data[str(guildID)][str(memberID)]["breads"] = initialBreads
        saveData(DATA_FILE, data)
        return initialBreads
    if str(memberID) not in data[str(guildID)]:
        data[str(guildID)][str(memberID)] = {}
        data[str(guildID)][str(memberID)]["breads"] = initialBreads
        saveData(DATA_FILE, data)
        return initialBreads
    return data[str(guildID)][str(memberID)]["breads"]

def saveBreads(guildID:discord.Interaction.guild_id, memberID:discord.Member.id, data:dict, breads:int):
    data[str(guildID)][str(memberID)]["breads"] = breads
    saveData(DATA_FILE, data)

TOKEN = dotenv_values(".env")["TOKEN"]

DATA_FILE = "data.json"
initialBreads = 100

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

@bot.tree.command(name="help")
async def help(interaction:discord.Interaction):
    url = "https://github.com/Manan-200/dcBots/blob/master/economyBot/README.md"
    await interaction.response.send_message(f"Visit {url} for more information.")

@bot.tree.command(name="balance", description="Get account information of a member or yourself")
async def balance(interaction:discord.Interaction, member:discord.Member=None):
    if member != None and member.bot:
        await interaction.response.send_message(f"{member.name} is a bot.")
        return
    if member == None:
        member = interaction.user
    data = loadData(DATA_FILE)
    breads = loadBreads(interaction.guild_id, member.id, data)
    await interaction.response.send_message(f"{member.name} has {breads} breads.")

@bot.tree.command(name="gamble", description="Gamble breads!")
async def gamble(interaction:discord.Interaction, gamble_breads:int):
    data = loadData(DATA_FILE)
    breads = loadBreads(interaction.guild_id, interaction.user.id, data)
    if gamble_breads > breads:
        await interaction.response.send_message(f"You can't gamble more than what you have!")
    else:
        wonBreads = random.randrange(gamble_breads * (-1), gamble_breads + 1)
        breads += wonBreads
        if wonBreads >= 0:
            await interaction.response.send_message(f"You won {wonBreads} breads! :D")
        else:
            await interaction.response.send_message(f"You lost {wonBreads * -1} breads. D:")
    saveBreads(interaction.guild.id, interaction.user.id, data, breads)

@bot.tree.command(name="rob", description="Rob a member!")
async def rob(interaction:discord.Interaction, member:discord.Member):
    if member.bot:
        await interaction.response.send_message(f"You can't rob a bot.")
        return

    if member.id == interaction.user.id:
        await interaction.response.send_message("You can't rob yourself.")
        return

    data = loadData(DATA_FILE)
    robberBreads = loadBreads(interaction.guild.id, interaction.user.id, data)
    memberBreads = loadBreads(interaction.guild.id, member.id, data)

    breadPercent = random.randrange(-10, 11)
    if breadPercent >= 0:
        stolenBreads =  int(memberBreads*breadPercent/100)
        await interaction.response.send_message(f"{interaction.user.name} robbed {stolenBreads} breads from {member.name}")
    elif breadPercent < 0:
        stolenBreads =  int(robberBreads*breadPercent/100)
        await interaction.response.send_message(f"{member.name} reverse robbed {-(stolenBreads)}breads from {interaction.user.name}")

    robberBreads += stolenBreads
    memberBreads -= stolenBreads

    saveBreads(interaction.guild.id, interaction.user.id, data, robberBreads)
    saveBreads(interaction.guild.id, member.id, data, memberBreads)

@bot.tree.command(name="leaderboard", description="See who has the most breads!")
async def leaderboard(interaction:discord.Interaction):
    data = loadData(DATA_FILE)
    try:
        guildDict = data[str(interaction.guild.id)]
    except:
        await interaction.repsponse.send_message("Everyone has the same breads.")
        return

    values = list(guildDict.values())
    
    keys = list(guildDict.keys())
    for i in range(len(values) - 1):
        for j in range(i, len(values)):
            if values[j] > values[i]:
                values[i], values[j] = values[j], values[i]
                keys[i], keys[j] = keys[j], keys[i]
    guildDict = {}
    for i in range(len(keys)):
        guildDict[f"{bot.get_user(int(keys[i])).name}"] = values[i]
    await interaction.response.send_message(f"{guildDict}")

keep_alive()
bot.run(TOKEN)