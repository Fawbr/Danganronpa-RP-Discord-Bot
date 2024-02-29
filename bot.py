import discord
from discord.ext import commands
intents = discord.Intents.all()
intents.members = True
import os
import asyncio

client = commands.Bot(command_prefix = '>', owner_id=140177108348567552, help_command=None, intents=intents)
client.remove_command("help")

@client.command()
async def help(ctx):
    embedList = []
    keepGoing = True
    def check(reaction, user):
        return str(reaction.emoji in ['⬅️','➡️']) and user.bot == False and ctx.author.id == user.id

    helpString1 = """
    Welcome to AIM Instant Messenger! NATM's very own DM bot, designed by Spooky MrMcgee#7317!

    You'll be able to get a good idea of the commands at your disposal with this quick help guide!
    Remember, the prefix for all of these commands are '>'! You can use the arrows in the reactions to move between different help pages!

    ``help`` - The help command for the bot! Gives you this message, not sure why you needed that one.

    ``ping`` - Pong!"""

    helpString2 = """
    List of commands for the bots DM interface!
    Remember, the prefix for all of these commands are '>'! You can use the arrows in the reactions to move between different help pages!

    ``setup_user [name] [admin name] [user discord ID]`` - (ADMIN) Allows you to set someone up for giving and receiving DM'S as a character. If this is your first time using the command, the bot will also ask you to setup a DM receipts channel where all DM's can be seen.

    ``dm [character name] [message]`` - Allows someone to DM another character as the character that the user is listed as.

    ``adm [character name] [message]`` - Allows someone to anonymously DM another player! This won't show the name of character to the player, but the admins can see who the user is in their dedicated receipts channel!
    """
    helpEmbed1 = discord.Embed(
    title = "Opening Page and Misc Commands",
    colour = 0x00ffff,
    description = helpString1)
    helpEmbed2 = discord.Embed(
    title = "DM System Commands",
    colour = 0x00ffff,
    description = helpString2)
    embedList.append(helpEmbed1)
    embedList.append(helpEmbed2)
    closeEmbed = discord.Embed(
    title = "This embed has closed.",
    colour = 0x000000,
    description = "This embed has closed due to user time out, this message will be deleted shortly.")

    message = await ctx.send(embed=helpEmbed1)
    x = 0
    while keepGoing == True:
        await message.add_reaction(emoji="⬅️")
        await asyncio.sleep(1.0)
        await message.add_reaction(emoji="➡️")
        try:
            reaction, user = await client.wait_for('reaction_add', check=check, timeout=90)
        except asyncio.TimeoutError:
            await message.edit(embed=closeEmbed)
            keepGoing = False
        else:
            if str(reaction.emoji) == "➡️":
                try:
                    x=x+1
                    print(str(x) + "no index error")
                    await message.edit(embed=embedList[x])
                except IndexError:
                    x=0
                    print(str(x) + "index error")
                    await message.edit(embed=embedList[x])
            if str(reaction.emoji) == "⬅️":
                try:
                    x=x-1
                    print(str(x) + "no index error")
                    await message.edit(embed=embedList[x])
                except IndexError:
                    x=x+(len(embedList)-1)
                    print(str(x) + "index error")
                    await message.edit(embed=embedList[x])
    return

@client.command()
async def ping(ctx):
    await ctx.send("Pong!")
    return

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    await load()
    await client.start('')

asyncio.run(main())
