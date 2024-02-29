import discord
import asyncio
import json
from discord.ext import commands
import os

class DM_System(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dm_list = []
        self.checkData = self.getData("dm_info.txt")
        if self.checkData:
            self.dm_list = self.getData("dm_info.txt")


    def getData(self, file):
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, file)
        filename = filename.replace("cogs\\","")
        with open(filename) as json_file:
            data = None
            try:
                data = json.load(json_file)
            except:
                pass
            if data:
                return data

    def sendData(self, dataSend, file):
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, file)
        filename = filename.replace("cogs\\","")
        with open(filename, 'w') as outfile:
            json.dump(dataSend, outfile)


    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.sendData(self.dm_list, 'dm_info.txt')
        if not self.dm_list:
            self.dm_list = []

    @commands.has_permissions(administrator = True)
    @commands.command()
    async def setup_user(self, ctx, *args):
        userDetails = []
        alreadyAdded = False
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        def check_channel(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.channel_mentions
        if not self.dm_list:
            await ctx.send("Hello! Before we start, this bot will need a channel that only the moderators/admins can access! This channel will be used to relay all DM receipts, that will contain the content of the message, the recipient and the person sending. Whenever you are ready, please send the the name of a channel (like so: #welcome).")
            chanLoop = True
            while chanLoop == True:
                channelPlacement = await self.client.wait_for("message", check=check_channel)
                x = self.client.get_channel(channelPlacement.channel_mentions[0].id)
                await ctx.send("So you'd like your receipt channel to be {}, correct? Please confirm with either a 'Y' or 'N' to confirm or deny.".format(x.mention))
                confMessage = await self.client.wait_for("message", check=check)
                if confMessage.content.lower() == "y":
                    await ctx.send("Alright! {} has been set to your receipt channel! All DM's should flow into there when they're sent!\nIf you want to change it in future, you can just use the >chance_receipt command!".format(x.mention))
                    chanLoop = False
                    self.dm_list.append(x.id)
                elif confMessage.content.lower() == "n":
                    await ctx.send("Retrying channel process, please mention the channel you'd like to use for your receipts.")
                else:
                    await ctx.send("Unknown response, please re-enter your choice for channel.")

        dmStr = " ".join(args)
        length = len(dmStr)
        cutValue = dmStr.find('<')
        cutValue2 = dmStr.find('>')
        name = dmStr[0:(cutValue-1)]
        userId = dmStr[(cutValue+2):cutValue2]
        chanId = dmStr[(cutValue2+4):(length-1)]

        userDetails.append(name)
        userDetails.append(int(userId))
        userDetails.append(int(chanId))
        await ctx.send("Alright! That wraps up the user setup! They should now be able to send and receive DM's.")

        for x in range(len(self.dm_list)):
            try:
                if user.mentions[0].id == self.dm_list[x][1]:
                        extraChar = []
                        extraChar.append(name.content)
                        extraChar.append(channel.id)
                        self.dm_list[x].append(extraChar)
                        alreadyAdded = True
            except:
                pass
        if alreadyAdded == False:
            self.dm_list.append(userDetails)
        
    @commands.command()
    async def dm(self, ctx, arg1, *, args):
        nameConfirmed = False
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        if args:
            characterCount = 0
            possibleNick = []
            keepGoing = False
            nameConf = False
            for a in range(len(self.dm_list)):
                try:
                    if ctx.author.id == self.dm_list[a][1]:
                        characterCount += 1
                        possibleNick.append(self.dm_list[a][0])
                except:
                    pass

            for x in range(len(self.dm_list)):
                message = []
                try:
                    if ctx.author.id == self.dm_list[x][1]:
                        if characterCount > 1:
                            listName = ' '.join(possibleNick)
                            await ctx.send("Who would you like to send a message as? Your possible options are: {}".format(listName))
                            while keepGoing == False:
                                DMChoose = await self.client.wait_for("message", check=check)
                                for y in range(len(possibleNick)):
                                    if DMChoose.content.lower() == possibleNick[y].lower():
                                        nickname = possibleNick[y]
                                        keepGoing = True
                                nameConfirmed = True

                        if nameConfirmed == False:
                            nickname = self.dm_list[x][0]
                        for y in range(len(self.dm_list)):
                            try:
                                if arg1.lower() == self.dm_list[y][0].lower():
                                        channel = self.dm_list[y][2]
                                        recipNick = self.dm_list[y][0]
                                        chan = self.client.get_channel(channel)
                                        guild = chan.guild
                                        messageEmbed = discord.Embed(
                                        title = "{} has sent {} a message!".format(nickname, recipNick),
                                        description = "{}".format(args),
                                        color = 0xA04FDB)
                                        messageEmbed.set_footer(text="Communications are monitored 24/7! A reminder that every message can and will be read by the hosts.")


                                        receiptEmbed = discord.Embed(
                                        title = "{} has sent {} a DM!".format(nickname, recipNick),
                                        description = "{}".format(args))
                                        receiptEmbed.set_footer(text="This has been a message sent by {}".format(ctx.author.name))
                                        await chan.send(embed=messageEmbed)
                                        await chan.send("<@{}>".format(self.dm_list[y][1]))
                                        receiptChan = self.client.get_channel(self.dm_list[0])
                                        await receiptChan.send(embed=receiptEmbed)
                                        await ctx.send("Message sent successfully!")
                                        return
                            except:
                                pass
                except:
                    pass
        else:
            await ctx.send("You haven't sent a full message! Please be sure to specify the name and the message you'd like to send!")

    @commands.command()
    async def adm(self, ctx, arg1, *, args):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        if args:
            secondUser = False
            keepGoing = False
            nameConf = False
            for x in range(len(self.dm_list)):
                message = []
                try:
                    if ctx.author.id == self.dm_list[x][1]:
                        for y in range(len(self.dm_list)):
                            try:
                                if arg1.lower() == self.dm_list[y][0].lower():
                                    nameConf = True
                                    secondUser = False
                                try:
                                    if arg1.lower() == self.dm_list[y][3][0].lower():
                                        nameConf = True
                                        secondUser = True
                                except:
                                    pass

                                if nameConf == True:
                                    if secondUser == True:
                                        try:
                                            if self.dm_list[y][3]:
                                                channel = self.dm_list[y][3][1]
                                                recipNick = self.dm_list[y][3][0]
                                        except:
                                            pass
                                    if secondUser == False:
                                        channel = self.dm_list[y][2]
                                        recipNick = self.dm_list[y][0]
                                    chan = self.client.get_channel(channel)
                                    guild = chan.guild
                                    messageEmbed = discord.Embed(
                                    title = "You have received an anonymous message!",
                                    description = "{}".format(args),
                                    color = 0xA04FDB)
                                    messageEmbed.set_footer(text="Communications are monitored 24/7! A reminder that every message can and will be read by the hosts.")


                                    receiptEmbed = discord.Embed(
                                    title = "{} has sent {} a DM!".format(ctx.author.name, recipNick),
                                    description = "{}".format(args))
                                    receiptEmbed.set_footer(text="This has been a message sent by {}".format(ctx.author.name))
                                    await chan.send(embed=messageEmbed)
                                    await chan.send("<@{}>".format(self.dm_list[y][1]))
                                    receiptChan = self.client.get_channel(self.dm_list[0])
                                    await receiptChan.send(embed=receiptEmbed)
                                    await ctx.send("Message sent successfully!")
                                    return
                            except TypeError:
                                pass
                except TypeError:
                    pass

    @commands.command()
    async def nicknames(self, ctx):
        nicknames = []
        nickString = ""
        for x in range(len(self.dm_list)):
            try:
                nicknames.append(self.dm_list[x][0])
                if self.dm_list[x][3]:
                    nicknames.append(self.dm_list[x][3][0])
            except:
                pass

        for y in range(len(nicknames)):
            nickString = nickString + nicknames[y] + '\n'
        nicknameEmbed = discord.Embed(
        title = "Here are all the available nicknames for DM'ing!",
        description = '**{}**'.format(nickString),
        color = 0xA04FDB)
        await ctx.send(embed=nicknameEmbed)

async def setup(client):
    await client.add_cog(DM_System(client))
