from discord.ext import commands, tasks
from github import Github
import json
import discord

with open("token.json", "r") as file:
    data = json.load(file)
    gitToken = data["git"]
    botToken = data["bot"]

g = Github(gitToken)
repo = g.get_repo("Manan-200/dcBots")
n = 0
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

oldCommit = repo.get_commits()[0]

@tasks.loop(minutes=1)
async def printCommit():
    global oldCommit
    for guild in bot.guilds:
        channel = discord.utils.get(guild.channels, name="git")
        if channel:
            newCommit = repo.get_commits()[0]
            if oldCommit != newCommit:
                oldCommit = newCommit
                await channel.send(f"New commit by {newCommit.commit.author.name} on {newCommit.repo.name}: '{newCommit.commit.message}'")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        printCommit.start()
    except Exception as e:
        print(e)

bot.run(botToken)