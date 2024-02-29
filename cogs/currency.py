import discord
import asyncio
import json
from discord.ext import commands
import os

class Currency(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.currency_list = []
        self.checkData = self.getData("currency_info.txt")
        if self.checkData:
            self.currency_list = self.getData("currency_info.txt")

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
        self.sendData(self.currency_list, 'currency_info.txt')
        if not self.currency_list:
            self.currency_list = []


    @commands.Cog.listener()
    async def on_ready(self):
        memberPresent = False
        guild = self.client.guilds
        async for member in guild[0].fetch_members():
            for x in range(len(self.currency_list)):
                if member.id == self.currency_list[x][0]:
                    memberPresent = True
            if memberPresent == False:
                memberDetails = [member.id, 0]
                self.currency_list.append(memberDetails)

        self.sendData(self.currency_list, 'currency_info.txt')
        if not self.currency_list:
            self.currency_list = []


    @commands.Cog.listener()
    async def on_member_join(self, member):
        memberPresent = False
        memberDetails = [member.id, 0]
        guild = member.guild
        async for member in guild.fetch_members():
            for x in range(len(self.currency_list)):
                if member.id == self.currency_list[x][0]:
                    memberPresent = True
            if memberPresent == False:
                memberDetails = [member.id, 0]
                self.currency_list.append(memberDetails)

        self.sendData(self.currency_list, 'currency_info.txt')
        if not self.currency_list:
            self.currency_list = []


    @commands.command(aliases= ["add", "add_money", "give", "give_money"])
    @commands.has_permissions(administrator = True)
    async def add_currency(self, ctx, *args):
        if args:
            userID = args[0]
            userID = userID.replace('>','')
            userID = userID.replace('<','')
            userID = userID.replace('@','')
            userID = userID.replace('!','')
            moneyAdd = int(args[1])
            for x in range(len(self.currency_list)):
                if int(userID) == self.currency_list[x][0]:
                    money = self.currency_list[x][1]
                    money = money + moneyAdd
                    self.currency_list[x][1] = money
            await ctx.send("Added {} coins to <@{}>!".format(args[1], userID))


    @commands.command(aliases = ["remove_money", "remove", "take", "take_money"])
    @commands.has_permissions(administrator = True)
    async def remove_currency(self, ctx, *args):
        if args:
            userID = args[0]
            userID = userID.replace('>','')
            userID = userID.replace('<','')
            userID = userID.replace('@','')
            userID = userID.replace('!','')
            moneyAdd = int(args[1])
            for x in range(len(self.currency_list)):
                if int(userID) == self.currency_list[x][0]:
                    money = self.currency_list[x][1]
                    if money < moneyAdd:
                        money = 0
                    else:
                        money = money - moneyAdd
                    self.currency_list[x][1] = money
            await ctx.send("Removed {} coins from <@{}>!".format(args[1], userID))

    @commands.command(aliases = ["balance"])
    async def bal(self, ctx):
        for x in range(len(self.currency_list)):
            if self.currency_list[x][0] == ctx.author.id:
                moneyAmount = discord.Embed(
                title = "{}".format(ctx.author.display_name),
                description = "Your current balance is **{}**!".format(self.currency_list[x][1]),
                colour = int("0xA04FDB",16)
                )
                await ctx.send(embed=moneyAmount)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def leaderboard(self, ctx):
        self.currency_list.sort(key=lambda x: x[1], reverse = True)

        leadString = """
        1. <@{}> with **{}**!
        2. <@{}> with **{}**!
        3. <@{}> with **{}**!
        4. <@{}> with **{}**!
        5. <@{}> with **{}**!
        6. <@{}> with **{}**!
        7. <@{}> with **{}**!
        8. <@{}> with **{}**!
        9. <@{}> with **{}**!
        10. <@{}> with **{}**!
        """.format(self.currency_list[0][0], self.currency_list[0][1], self.currency_list[1][0], self.currency_list[1][1], self.currency_list[2][0], self.currency_list[2][1], self.currency_list[3][0], self.currency_list[3][1], self.currency_list[4][0], self.currency_list[4][1], self.currency_list[5][0], self.currency_list[5][1], self.currency_list[6][0], self.currency_list[6][1], self.currency_list[7][0], self.currency_list[7][1], self.currency_list[8][0], self.currency_list[8][1], self.currency_list[9][0], self.currency_list[9][1])

        leadEmbed = discord.Embed(
        title = "These are our current top earners for this server!",
        description = "{}".format(leadString),
        colour = int("0xA04FDB",16)
        )
        await ctx.send(embed=leadEmbed)

async def setup(client):
    await client.add_cog(Currency(client))
