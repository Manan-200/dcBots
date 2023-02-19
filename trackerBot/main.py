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
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

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
            data = loadData(DATA_FILE)
            for repo_name in data:
                repo = g.get_repo(f'{data[repo_name]["author"]}/{repo_name}')
                oldNodeID = data[repo_name]["nodeID"]
                newNodeID = repo.get_commits()[0].sha
                if newNodeID != oldNodeID:
                    await channel.send(f"New commit by {repo.get_commits()[0].commit.author.name} on {repo.name}: '{repo.get_commits()[0].commit.message}'")
                    data[repo_name]["nodeID"] = newNodeID
                    saveData(DATA_FILE, data)

@bot.tree.command(name="track_file", description="Add a file to tracking list")
async def track_file(interaction:discord.Interaction, author:str, repo_name:str):
    data = loadData(DATA_FILE)
    repo = g.get_repo(f"{author}/{repo_name}")
    data[repo_name] = {"nodeID":f"{repo.get_commits()[0].sha}", "author":f"{author}"}
    saveData(DATA_FILE, data)
    await interaction.response.send_message(f"Added {repo_name} to tracking list.")

@bot.tree.command(name="untrack_file", description="Remove a file from tracking list")
async def untrack_file(interaction:discord.Interaction, repo_name:str):
    data = loadData(DATA_FILE)
    if repo_name in data:
        del data[repo_name]
        saveData(DATA_FILE, data)
        await interaction.response.send_message(f"Removed {repo_name} from tracking list")
    else:
        await interaction.response.send_message(f"{repo_name} is not in the tracking list")

bot.run(botToken)