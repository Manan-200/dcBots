from discord.ext import commands, tasks
from github import Github
import json
import discord
import requests

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
headers = {"Authorization": gitToken}

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
    #Selecting channel to send messages
    for guild in bot.guilds:
        channel = discord.utils.get(guild.channels, name="git")
        if channel:
            data = loadData(DATA_FILE)
            #Selecting each repository path from data
            for path in data:
                repo = g.get_repo(f"{path}")
                oldNodeID = data[path]["nodeID"]
                newNodeID = repo.get_commits()[0].sha
                
                #Comparing latest SHA with previous SHA
                if newNodeID == oldNodeID:
                    continue
                
                #Saving new commit SHA and sending message on discord
                fileUrl = f"https://github.com/{path}"
                await channel.send(f"New commit by '{repo.get_commits()[0].commit.author.name}' on {fileUrl} : '{repo.get_commits()[0].commit.message}'")
                data[path]["nodeID"] = newNodeID
                saveData(DATA_FILE, data)

@bot.tree.command(name="track_file", description="Add a repository to tracking list")
async def track_file(interaction:discord.Interaction, author:str, repo_name:str):
    
    path = f"{author}/{repo_name}"

    #Checking is entered repo path is valid
    url = f"https://api.github.com/repos/{path}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        await interaction.response.send_message(f"The repository does not exist")
        return
    
    data = loadData(DATA_FILE)

    fileUrl = f"https://github.com/{path}"

    #Checking if entered repo is already in data
    if path in data:
        await interaction.response.send_message(f"{fileUrl} is already tracking list")
        return

    #Saving the repo and latest commit SHA in data file
    repo = g.get_repo(path)
    data[path] = {"nodeID":f"{repo.get_commits()[0].sha}"}
    saveData(DATA_FILE, data)
    await interaction.response.send_message(f"Added {fileUrl} to tracking list")

@bot.tree.command(name="untrack_file", description="Remove a file from tracking list")
async def untrack_file(interaction:discord.Interaction, author:str, repo_name:str):

    data = loadData(DATA_FILE)
    path = f"{author}/{repo_name}"
    fileUrl = f"https://github.com/{path}"

    #Try to delete repo from data if it exists
    try:
        del data[path]
        saveData(DATA_FILE, data)
        await interaction.response.send_message(f"Removed {fileUrl} from tracking list")
    #If repo doesn't exist, send error message
    except:
        await interaction.response.send_message(f"The repository is not in the tracking list")

@bot.tree.command(name="tracking_list", description="Prints list of repositories being tracked")
async def tracking_list(interaction:discord.Interaction):

    data = loadData(DATA_FILE)

    #Printing list of URLs of all repos in data 
    msgArr = []
    for path in data:
        fileUrl = f"https://github.com/{path}"
        msgArr.append(f"{fileUrl}")
    await interaction.response.send_message(f"{msgArr}")

bot.run(botToken)