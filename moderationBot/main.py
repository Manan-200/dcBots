import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import json
import random

DATA_FILE = "data.json"

def reverse(msg:str):
    rev_msg = ""
    for char in msg:
        rev_msg += chr(ord("n") + ord("m") - ord(char))
    return(rev_msg)

def get_data(FILE):
    try:
        with open(FILE, "r") as file:
            data = json.load(file)
        return(data)
    except:
        return {}

def save_data(FILE, data):
    with open(FILE, "w") as file:
        json.dump(data, file)

TOKEN = get_data("token.json")["token"]
data_dict = get_data(DATA_FILE)
print(data_dict)
try:
    game1_data = data_dict["game_1"]
except:
    data_dict["game_1"] = {}
    game1_data = data_dict["game_1"]

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print (f"Synced {len(synced)} commands(s)")
    except Exception as e:
        print (e)

@bot.tree.command(name="hey")   
async def hello(interaction:discord.Interaction):  
    await interaction.response.send_message(f"hey mf")

@bot.tree.command(name="print_data")
async def print_msg(interaction:discord.Interaction):
    await interaction.response.send_message(f"{data_dict}")

@bot.tree.command(name="ping")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message("pong!")

@bot.tree.command(name="embed")
async def embed(interaction:discord.Interaction, member:discord.Member=None):
    if member == None:
        member = interaction.user
    
    name = member.display_name
    pfp = member.display_avatar

    embed = discord.Embed(title=f"{name} you suck", description=f"{name} sucks", colour=discord.Colour.random())
    embed.set_author (name=f'{name}')
    embed.set_thumbnail(url=f"{pfp}")
    embed.add_field(name=f"{name} is a disgrace!", value=f"{name} is fatherless!")
    embed.set_footer(text=f"{interaction.user} created this embed!")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="generate_num")
async def generate_num(interaction:discord.Interaction):
    await interaction.response.send_message("Random number has been generated between 1 and 50!")
    game1_data["state"] = True
    game1_data["num"] = random.randrange(1, 51)
    game1_data["lives"] = 5
    save_data(DATA_FILE, data_dict)

@bot.tree.command(name="guess")
async def guess(interaction:discord.Interaction, num:int):
    if game1_data["state"]:
        if game1_data["num"] == num:
            await interaction.response.send_message("You guessed the correct number, gg!")
            game1_data["state"] = False
        else:
            game1_data["lives"] -= 1
            if game1_data["lives"] > 0:
                if game1_data["num"] < num:
                    await interaction.response.send_message("Your guess is too big")
                elif game1_data["num"] > num:
                    await interaction.response.send_message("Your guess is too small")
            if game1_data["lives"] == 0:
                await interaction.response.send_message("You lost")
                game1_data["state"] = False
    else:
        await interaction.response.send_message("First use /generate_num")
    save_data(DATA_FILE, data_dict)

@bot.tree.command(name="reverse_cipher")
async def reverse_cipher(interaction:discord.Interaction, msg:str):
    await interaction.response.send_message(reverse(msg))

@bot.tree.command(name="role")
async def role(interaction: discord.Interaction, role: discord.Role):
    if role in interaction.user.roles:
        await interaction.user.remove_roles(role)
    else:
        await interaction.user.add_roles(role)
    await interaction.response.send_message(f"Work has been done")

@bot.tree.command(name="addrole")
@has_permissions(manage_roles=True)
async def addrole(interaction: discord.Interaction, role: discord.Role, member: discord.Member=None):
    member == member or interaction.user
    await member.add_roles(role)
    await interaction.response.send_message (f"{role} has been added to {member}")

@bot.tree.command(name="removerole")
@has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, role: discord.Role, member: discord.Member=None):
    member == member or interaction.user
    await member.remove_roles(role)
    await interaction.response.send_message (f"{role} has been removed from {member}!")

@bot.tree.command(name="ban")
async def ban(interaction:discord.Interaction, member: discord.Member, reason:str=None):
    await member.ban()
    try:
        await member.send(f"You have been banned in {interaction.guild} for {reason}")
    except:
        pass
    await interaction.response.send_message(f"{member} has been successfully banned.")

@bot.tree.command(name="kick")
async def kick(interaction:discord.Interaction, member: discord.Member, reason:str=None):
    await member.kick()
    try:
        await member.send(f"You have been kicked from {interaction.guild} for {reason}")
    except:
        pass
    await interaction.response.send_message(f"{member} has been successfully kicked.")

bot.run(TOKEN)
