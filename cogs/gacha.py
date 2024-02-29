import discord
import asyncio
import math
import json
import random
from discord.ext import commands
import os
import re

class Gacha(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.gacha_list = []
        self.inventory = []
        self.checkData = self.getData("gacha_info.txt")
        self.checkInvData = self.getData("inventory_info.txt")
        if self.checkData:
            self.gacha_list = self.getData("gacha_info.txt")
        if self.checkInvData:
            self.inventory = self.getData("inventory_info.txt")
    
    class InteractionButtons(discord.ui.View):
        def __init__(self, user: discord.User):
            super().__init__()
            self.value = None
            self.counter = 0
            self.embedList = []
            self.user = user

        @discord.ui.button(label="Previous Page", style=discord.ButtonStyle.primary, disabled=True)
        async def previousPage(self, interaction: discord.Interaction, button : discord.ui.Button):
            self.counter -= 1
            await interaction.response.edit_message(embed=self.embedHandler(self.embedList, self.counter), view=self)

        @discord.ui.button(label="Next Page", style=discord.ButtonStyle.primary)
        async def nextPage(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.counter += 1
            await interaction.response.edit_message(embed=self.embedHandler(self.embedList, self.counter), view=self)

        def updateEmbedList(self, listEmbed):
            self.embedList = listEmbed

        def updatePreviousButton(self, counter):
            if counter != 0:
                self.previousPage.disabled = False
            else:
                self.previousPage.disabled = True

        def updateNextButton(self, updateBool):
            if updateBool == False:
                self.nextPage.disabled = False
            else:
                self.nextPage.disabled = True

        async def interaction_check(self, interaction: discord.Interaction):
            if interaction.user != self.user:
                await interaction.response.send_message("You cannot interact with this button!", ephemeral=True)
            else:
                return True
    
        def embedHandler(self, embedList, embedIndex):
            self.updatePreviousButton(self.counter)
            if (len(embedList) <= ((embedIndex+1) * 5)):
                self.updateNextButton(True)
            else:
                self.updateNextButton(False)
            inventoryEmbed = discord.Embed(
            title = "Gacha Inventory",
            description = "Here's a list of all your items!",
            color = 0xA04FDB)


            for a in range(5):
                embedInd = (a + (5 * embedIndex))
                if (embedInd >= len(embedList)):
                    break
                titleStr = "{} - {}".format(embedList[embedInd][0], embedList[embedInd][1][0])
                itemDesc = str(embedList[embedInd][1][1])
                if len(itemDesc) >= 303:
                    itemDesc = itemDesc[:300] + "..."
                inventoryEmbed.add_field(name=titleStr, value=itemDesc, inline=False)
                footerStr = "Page {}/{}".format(str(embedIndex+1), str(math.ceil(len(embedList) / 5)))
                inventoryEmbed.set_footer(text=footerStr)
            return inventoryEmbed
        
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
        self.sendData(self.gacha_list, 'gacha_info.txt')
        self.sendData(self.inventory, "inventory_info.txt")
        if not self.gacha_list:
            self.gacha_list = []
        if not self.inventory:
            self.inventory = []

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def add_gacha(self, ctx, *args):
        gachaStr = " ".join(args)
        gachaStrList = []
        length = len(gachaStr)
        argsAmount = gachaStr.count("|")+1
        for x in range(argsAmount):
            if x < (argsAmount-1):
                stringToAdd = gachaStr[0:(gachaStr.find('|'))]
                gachaStr = gachaStr[(gachaStr.find('|')+2):len(gachaStr)]
            else:
                stringToAdd = gachaStr
            gachaStrList.append(stringToAdd)

        if (len(gachaStrList) == 3):
            gachaStrList[2] = int(gachaStrList[2])
        self.gacha_list.append(gachaStrList)

        gachaEmbed = discord.Embed(
        title = "{}".format(gachaStrList[0]),
        description = "{}".format(gachaStrList[1]),
        color = 0xA04FDB)
        if len(gachaStrList) == 3:
            await ctx.send("Added **{}**with a quantity of **{}**".format(gachaStrList[0], gachaStrList[2]))
        else:
            await ctx.send("Added **{}**".format(gachaStrList[0]))
        await ctx.send(embed=gachaEmbed)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def remove_gacha(self, ctx, *args):
        removeStr = " ".join(args)
        removeStr = removeStr + " "
        numberOfItems = len(self.gacha_list)
        for x in range(numberOfItems):
            if self.gacha_list[x][0] == removeStr:
                del self.gacha_list[x]

    @commands.command()
    async def roll(self, ctx):
        currency = self.client.get_cog("Currency")
        currencyInfo = currency.currency_list
        playerFound = False
        gachaChosen = False
        for x in range(len(currencyInfo)):
            if ctx.author.id == currencyInfo[x][0]:
                if currencyInfo[x][1] >= 100:
                    gachaRange = (len(self.gacha_list) - 1)

                    while (gachaChosen == False):
                        gachaChoice = random.randint(0, gachaRange)
                        if (len(self.gacha_list[gachaChoice]) == 3):
                            if (self.gacha_list[gachaChoice][2] > 0):
                                self.gacha_list[gachaChoice][2] -= 1
                                gachaChosen = True
                        else:
                            gachaChosen = True

                    gachaEmbed = discord.Embed(
                    title = "You rolled a {}!".format(self.gacha_list[gachaChoice][0]),
                    description = "Here's the information for your item",
                    color = 0xA04FDB)
                    gachaEmbed.add_field(name="{}".format(self.gacha_list[gachaChoice][0]), value="{}".format(self.gacha_list[gachaChoice][1], inline=False))
                    inventoryAdd = [self.gacha_list[gachaChoice][0], self.gacha_list[gachaChoice][1]]
                    if self.inventory:
                        for x in range(len(self.inventory)):
                            if ctx.author.id == self.inventory[x][0]:
                                playerFound = True
                                self.inventory[x].append(inventoryAdd)
                                break
                            else:
                                playerFound = False

                        if playerFound == False:
                            inventoryAdd = [ctx.author.id, [self.gacha_list[gachaChoice][0], self.gacha_list[gachaChoice][1]]]
                    else:
                        inventoryAdd = [ctx.author.id, [self.gacha_list[gachaChoice][0], self.gacha_list[gachaChoice][1]]]
                        self.inventory.append(inventoryAdd)

                    await ctx.send(embed=gachaEmbed)
                    currency.currency_list[x][1] -= 100

    @commands.command()
    async def inventory(self, ctx):       
        view = self.InteractionButtons(ctx.author)
        embedList = []
        view.updateEmbedList(embedList)
        recurringGacha = 0
        if self.inventory:
            for x in range(len(self.inventory)):
                if ctx.author.id == self.inventory[x][0]:
                    for y in range(len(self.inventory[x])):
                        if self.inventory[x][y] != self.inventory[x][0]:
                            recurringGacha = self.inventory[x].count(self.inventory[x][y])
                            addToEmbed = [recurringGacha, self.inventory[x][y]]
                            if embedList:
                                dontAdd = False
                                for z in range(len(embedList)):
                                    if addToEmbed == embedList[z]:
                                        dontAdd = True
                                if dontAdd == False:
                                    embedList.append(addToEmbed)
                            else:
                                embedList.append(addToEmbed)
                    view.updateEmbedList(embedList)
                    invEmbed = view.embedHandler(embedList, 0)
                    await ctx.send(embed=invEmbed, view=view)

    @commands.command()
    async def view_item(self, ctx, *args):
        gachaString = " ".join(args).lower()
        additionalCount = 0
        itemFound = False
        if self.inventory:
            for x in range(len(self.inventory)):
                if ctx.author.id == self.inventory[x][0]:
                    for y in range(len(self.inventory[x])):
                        if y != 0:
                            gachaComparison = self.inventory[x][y][0].lower()
                            if gachaString == gachaComparison[:-1]:
                                itemFound = True
                                additionalCount += 1
                                gachaEmbed = discord.Embed(
                                    title = "Item Information",
                                    description = "Here's the details of **{}**!".format(self.inventory[x][y][0]),
                                    color = 0xA04FDB
                                )
                                gachaName = str(self.inventory[x][y][0])
                                gachaDescription = str(self.inventory[x][y][1])
                    if itemFound == True:
                        gachaEmbed.add_field(name="{}".format(gachaName), value=gachaDescription, inline=False)
                        gachaEmbed.add_field(name="Quantity owned", value=str(additionalCount), inline=False)
                        await ctx.send(embed=gachaEmbed)
                    else:
                        await ctx.send("You either don't own this item or it doesn't exist! Make sure you're spelling the item name correctly.")
                    


async def setup(client):
    await client.add_cog(Gacha(client))
