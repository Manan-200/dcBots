from discord.ext import commands, tasks
from github import Github
import json
import discord

def loadData(filePath:str):
    try:
        with open(filePath, 'r') as file:
            return(json.load(file))
    except:
        return {}
def saveData(filePath:str, data:dict):
    with open(filePath, 'w') as file:
        json.dump(data, file)

DATA_FILE = "data.json"

tokenData = loadData("tokens.json")
gitToken = tokenData["git"]
botToken = tokenData["bot"]

g = Github(gitToken)
repo = g.get_repo("Manan-200/dcBots")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

oldCommit = repo.get_commits()[0]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        printCommit.start()
    except Exception as e:
        print(e)

@tasks.loop(minutes=1)
async def printCommit():
    global oldCommit
    for guild in bot.guilds:
        channel = discord.utils.get(guild.channels, name="git")
        if channel:
            newCommit = repo.get_commits()[0]
            if oldCommit != newCommit:
                oldCommit = newCommit
                await channel.send(f"New commit by {newCommit.commit.author.name} on {repo.name}: '{newCommit.commit.message}'")

@bot.tree.command(name="track_file", description="Add a file to tracking list")
async def track_file(interaction:discord.Interaction, file:str):
    data = loadData(DATA_FILE)
    if len(data) == 0:
        data = {"files": []}
    data["files"].append(file)
    saveData(DATA_FILE, data)
    await interaction.response.send_message(f"Added {file} to tracking list.")

@bot.tree.command(name="untrack_file", description="Remove a file from tracking list")
async def untrack_file(interaction:discord.Interaction, file:str):
    data = loadData(DATA_FILE)
    try:
        data["files"].remove(file)
        saveData(DATA_FILE, data)
        await interaction.response.send_message(f"Removed {file} from tracking list")
    except:
        await interaction.response.send_message(f"{file} is not in the tracking list")

bot.run(botToken)