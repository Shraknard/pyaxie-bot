import discord
import yaml
import os
import sys
import time
import json
import requests

from datetime import datetime
from pyaxie import pyaxie
import pyaxie_utils
from datetime import timedelta
from pprint import pprint

now = datetime.now()
client = discord.Client()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")


def create_info_message(pyax):
    """
    Create a message for the SLP infos (bot command : $wen)
    :param pyax: a pyaxie object with scholar informations
    :return: The response with the infos
    """
    balance = pyax.get_claimed_slp()
    last_claim = pyax.get_last_claim()

    try:
        if datetime.utcnow() + timedelta(days=-14) < datetime.fromtimestamp(last_claim):
            wait = datetime.fromtimestamp(last_claim) - (datetime.utcnow() + timedelta(days=-14))
            mod = wait.seconds
            hour = str(int(mod // 3600))
            mod %= 3600
            m = str(int(mod // 60))
            mod %= 60
            s = str(int(mod))
            response = "❌ **NOT ABLE TO CLAIM** : **" + str(wait.days) + " day(s) " + hour + " hour(s) " + m + " min " + s + " sec\n**"
        else:
            response = "✅ **ABLE TO CLAIM**\n"

        perc = 1 if pyax.ronin_address == config['personal']['ronin_address'] else pyax.payout_percentage

        unclaimed = pyax.get_unclaimed_slp()
        total = int(balance + unclaimed)
        response += "\nBalance : **" + str(balance) + " SLP**" + \
                    "\nUnclaimed : **" + str(unclaimed) + " SLP**" + \
                    "\nAfter we split, you'll have : **" + str(int(total * perc)) + " SLP** or **" + str(int((total * pyax.get_price('slp') * perc))) + "$**" + \
                    "\nApproximate daily ratio : **" + str(pyax.get_daily_slp()) + " SLP**\n---"
    except ValueError as e:
        return "Error creating message : " + str(e)
    return response


def get_account_from_id(id):
    """
    Get a pyaxie object depending on config
    :param id: discord_id
    :return: Scholar account or Manager account or None
    """
    scholar = None
    id = int(id)
    if id == config['personal']['discord_id']:
        scholar = pyaxie(config['personal']['ronin_address'], config['personal']['private_key'])
    else:
        for sch in config['scholars']:
            if config['scholars'][sch]['discord_id'] == id:
                scholar = pyaxie(config['scholars'][sch]['ronin_address'], config['scholars'][sch]['private_key'])
                break
    return scholar


def get_account_from_ronin(ronin_address):
    """
    Get a pyaxie object depending on config
    :param id: ronin address
    :return: Scholar account or Manager account or None
    """
    scholar = None
    if ronin_address == config['personal']['ronin_address']:
        scholar = pyaxie(config['personal']['ronin_address'], config['personal']['private_key'])
    else:
        for sch in config['scholars']:
            if config['scholars'][sch]['ronin_address'] == ronin_address:
                scholar = pyaxie(config['scholars'][sch]['ronin_address'], config['scholars'][sch]['private_key'])
                break
    return scholar


def log(message="", end="\n"):
    f = open('pyaxie.log', "a")
    og = sys.stdout
    print(message, end=end, flush=True)
    sys.stdout = f
    print(message, end=end)
    sys.stdout = og
    f.flush()
    f.close()


@client.event
async def on_ready():
    print('\nWe are logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user or len(message.content) < 2 or message.content[0] != '$':
        return

    with open("secret.yaml", "r") as file:
        config = yaml.safe_load(file)

        scholar = get_account_from_id(message.author.id)
        if scholar is None:
            await message.channel.send("You are not part of the scholarship. Check with your manager to be added to the bot.")
            print("\nNon scholar tried to use the bot : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
            return

    ##############################
    # Send the list of commands  #
    ##############################
    if message.content == "$help":
        await message.channel.send("\n\n------------------------------------------------\n" +
                                    "\n**Commands for everybody :**\n" +
                                    "\n`$infos` = Send all the infos about your account  " +
                                    "\n`$qr` = Send your QR code  " +
                                    "\n`$mmr` = Send your current MMR  " +
                                    "\n`$rank` = Send your current rank" +
                                    "\n`$axies` = Send the list of axies of your account" +
                                    "\n`$axies 506011891353903121` = Send axies list of given discord ID" +
                                    "\n\n**Commands for manager :**\n" +
                                    "\n`$claim 506011891353903121` = Claim for the given discord ID (Manager only)  " +
                                    "\n`$all_claim` = Claim for all the scholars (Manager only)  " +
                                    "\n`$all_mmr` = Send scholar list sorted by MMR  " +
                                    "\n`$all_rank` = Send scholar list sorted by rank  " +
                                    "\n`$payout` = Send the available SLP to manager and scholars  " +
                                    "\n`$payout me` = Send all scholarship SLP directly to manager account with no split" +
                                    "\n`$transfer 0xfrom_address 0xto_address amount` = Transfer amount SLP from from_address to to_address")
        return

    ##############################
    # Send a QR code             #
    ##############################
    if message.content == "$qr":
        print("\nGet QR code for : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        try:
            qr_path = scholar.get_qr_code()
            await message.author.send("\n\n------------------------------------------------\n" +
                "\nHello " + message.author.name + " ! 😃 \nHere is your new QR Code to login : ")
            await message.author.send(file=discord.File(qr_path))
            os.remove(qr_path)
        except ValueError as e:
            await message.channel.send("Error getting QR code : " + str(e))
        return

    ##############################
    # Get MMR of author          #
    ##############################
    if message.content == "$mmr":
        if config['url_api'] == '':
            await message.channel.send("No api_url set in secret.yaml. You have to FIND and add it by yourself as it is private and I can't make it public.")
            return
        print("\nGet MMR for : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        try:
            await message.channel.send("\n\n------------------------------------------------\n" +
                "Hello " + message.author.name + " !\n"
                "Your MMR is : {} 🥇".format(scholar.get_rank_mmr()['mmr']))
        except ValueError as e:
            await message.channel.send("Error getting MMR : " + str(e))
        return

    ##############################
    # Get rank of author         #
    ##############################
    if message.content == "$rank":
        if config['url_api'] == '':
            await message.channel.send("No api_url set in secret.yaml. You have to FIND and add it by yourself as it is private and I can't make it public.")
            return
        print("\nGet rank for : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        try:
            await message.channel.send("\n\n------------------------------------------------\n" +
                "Hello " + message.author.name + " !\n"
                "Your rank is : {} 🎖️".format(scholar.get_rank_mmr()['rank']))
        except ValueError as e:
            await message.channel.send("Error getting rank : " + str(e))
        return

    ##################################
    # Get all infos about the author #
    ##################################
    if "$infos" in message.content:
        if config['url_api'] == '':
            await message.channel.send("No api_url set in secret.yaml. You have to FIND and add it by yourself as it is private and I can't make it public.")
            return
        if "$infos " in message.content:
            try:
                id = message.content.split(" ")[1]
                if id.isnumeric():
                    scholar = get_account_from_id(id)
                else:
                    await message.channel.send("Error in ID. Example: $infos 496061891353903121")
                    return
            except ValueError as e:
                await message.channel.send("Error : " + str(e))
                return e

        if scholar is None:
            await message.channel.send("Error: No scholar found with this ID")
            return

        rank_mmr = scholar.get_rank_mmr()
        print("\nGet infos for : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        try:
            imgline = scholar.get_axies_imageline()
            await message.channel.send("\n\n------------------------------------------------\n" +
                "Here are the infos for **" + scholar.name + "** account [**" + scholar.ronin_address + "**] :\n---\n" +
                "Claim status : {}\n".format(create_info_message(scholar).replace("\n", "", 1)) +
                "MMR : **{}** 🥇\n".format(rank_mmr['mmr']) +
                "Rank : **{}** 🎖️".format(rank_mmr['rank']), file=discord.File(imgline))
        except ValueError as e:
            await message.channel.send("Error getting infos : " + str(e))
        return

    ##############################
    # Get rank for all scholars  #
    ##############################
    if message.content == "$all_rank":
        if config['url_api'] == '':
            await message.channel.send("No api_url set in secret.yaml. You have to FIND and add it by yourself as it is private and I can't make it public.")
            return
        if message.author.id != config['personal']['discord_id']:
            await message.channel.send("This command is only available for manager")
            return
        print("\nGet all rank, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        await message.channel.send("\n\n------------------------------------------------\n" +
            "🎖️ Getting rank for all scholars, this can take some time...")
        try:
            l = list()
            msg = ""
            for account in config['scholars']:
                rank_mmr = scholar.get_rank_mmr(config['scholars'][account]['ronin_address'])
                rank_mmr['name'] = str(account)
                l.append(rank_mmr)

            ranks = sorted(l, key=lambda k: k['rank'])
            for r in ranks:
                msg += "\n**{}** | {}".format(r['rank'], r['name'])
        except ValueError as e:
            await message.channel.send("Error getting ranks : " + str(e))
            return
        await message.channel.send(msg)
        return

    ##############################
    # Get MMR for all scholars   #
    ##############################
    if message.content == "$all_mmr":
        if config['url_api'] == '':
            await message.channel.send("No api_url set in secret.yaml. You have to FIND and add it by yourself as it is private and I can't make it public.")
            return
        if message.author.id != config['personal']['discord_id']:
            await message.channel.send("This command is only available for manager")
            return
        print("\nGet all MMR, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        await message.channel.send("🥇 Getting MMR for all scholars, this can take some time...")
        try:
            l = list()
            msg = ""
            for account in config['scholars']:
                rank_mmr = scholar.get_rank_mmr(config['scholars'][account]['ronin_address'])
                rank_mmr['name'] = str(account)
                l.append(rank_mmr)

            mmrs = reversed(sorted(l, key=lambda k: k['mmr']))
            for m in mmrs:
                msg += "\n**{}** | {}".format(m['mmr'], m['name'])
        except ValueError as e:
            await message.channel.send("Error getting MMRs : " + str(e))
            return
        await message.channel.send(msg)
        return

    ##################################
    # Claim for the current scholars #
    ##################################
    if "$claim" in message.content:
        if config['url_api'] == '':
            await message.channel.send("No api_url set in secret.yaml. You have to FIND and add it by yourself as it is private and I can't make it public.")
            return
        print("\nClaim, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        try:
            if message.content == "$claim":
                await message.channel.send("You have to specify the discord ID of the scholar you want to claim for.\n" +
                                           "Example: `$claim 506011891353903121`")
                return

            to_id = message.content.split(' ')[1]
            scholar = get_account_from_id(to_id)
            if scholar is None:
                await message.channel.send("The Discord ID you specified is not in the scholarship.\n")
                return

            amount = scholar.get_unclaimed_slp()
            if amount > 0:
                await message.channel.send("{} SLP claimed for {} !\nTransaction hash of the claim : {} ".format(amount, scholar.name, str(scholar.claim_slp())))
            else:
                await message.channel.send("No SLP to claim for {} at this moment !\n".format(message.author.name))
        except ValueError as e:
            await message.channel.send("Error while claiming : " + str(e))
        return

    ##############################
    # Claim for all scholars     #
    ##############################
    if message.content == "$all_claim":
        print("\nAll claim, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        if message.author.id != config['personal']['discord_id']:
            await message.channel.send("This command is only available for manager")
            return

        await message.channel.send("\n------------------------------------------------\nClaiming for all scholars... This can take some time.\n")

        try:
            l = list()
            for account in config['scholars']:
                scholar = pyaxie(config['scholars'][account]['ronin_address'], config['scholars'][account]['private_key'])
                amount = scholar.get_unclaimed_slp()
                if datetime.utcnow() + timedelta(days=-14) < datetime.fromtimestamp(scholar.get_last_claim()) or amount < 0:
                    l.append("**No SLP to claim for {} at this moment** \n".format(scholar.name))
                else:
                    l.append("**{} SLP claimed for {} !** Transaction hash : {} \n".format(amount, scholar.name, str(scholar.claim_slp())))

            await message.channel.send("--------\n".join(l))
        except ValueError as e:
            await message.channel.send("Error getting QR code : " + str(e))
        return

    ##############################
    # Payout for all scholars    #
    ##############################
    if "payout" in message.content:
        print("\nPayout, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        await message.channel.send("\n------------------------------------------------\nPayout for all scholar ! This can take some time.\n")

        # Self payout for scholars
        if "$self_payout " in message.content:
            to_address = message.content.split(' ')[1].replace('ronin:', '0x')
            scholar = get_account_from_id(message.author.id)

            if scholar is None:
                await message.channel.send("Author is not part of the scholarship.")
                return
            if to_address == scholar.ronin_address:
                await message.channel.send("Your from_address and to_address are the same.")
                return

            unclaimed = scholar.get_unclaimed_slp()
            tx = scholar.payout().lower()
            if "error" in tx:
                await message.channel.send("Error while trying to payout : {}".format(tx))
                return
            else:
                await message.channel.send("Successfully sent **{} SLP** from : **{}** to **{}**".format(unclaimed, scholar.ronin_address, to_address))
                return

        # Payout for all scholars
        if message.content == "$payout":
            if message.author.id != config['personal']['discord_id']:
                await message.channel.send("This command is only available for manager")
                return
            try:
                for account in config['scholars']:
                    scholar = pyaxie(config['scholars'][account]['ronin_address'], config['scholars'][account]['private_key'])
                    unclaimed = scholar.get_unclaimed_slp()
                    claimed = scholar.get_claimed_slp()
                    time.sleep(5)

                    if datetime.utcnow() + timedelta(days=-14) < datetime.fromtimestamp(scholar.get_last_claim()) or unclaimed <= 0:
                        await message.channel.send("**No SLP to claim for {} at this moment** \n".format(scholar.name))
                    else:
                        await message.channel.send("**{} SLP claimed for {} !** Transaction hash : {} \n".format(unclaimed, scholar.name, str(scholar.claim_slp())))

                    if claimed <= 0:
                        await message.channel.send("**No SLP to send for {} account.**\n".format(scholar.name))
                    elif "me" in message.content:
                        tx = scholar.transfer_slp(config['personal']['ronin_address'], claimed)
                        await message.channel.send("**All the {} SLP are sent to you !** Transaction hash : {} \n".format(claimed, str(tx)))
                    else:
                        res = scholar.payout()
                        await message.channel.send("**{} SLP sent to you and {} SLP to {} !**".format(claimed * (1-scholar.payout_percentage), claimed * scholar.payout_percentage, scholar.name) +
                                                   "Transactions hash : {} \n".format(res))

                    await message.channel.send("\n-------------\n")

                await message.channel.send("\n\n --- END OF PAYOUT ---")
            except ValueError as e:
                await message.channel.send("Error while paying out : " + str(e))
        return

    ##############################################
    # Transfer SLP from an account to another    #
    ##############################################
    if "$transfer" in message.content and " " in message.content:
        print("\nTransfer, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        if message.author.id != config['personal']['discord_id']:
            await message.channel.send("This command is only available for manager")
            return

        cmd = message.content.split(' ')
        if ("0x" not in cmd[1] and not cmd[1].isnumeric()) or ("0x" not in cmd[2] and not cmd[2].isnumeric()) or not cmd[3].isnumeric():
            await message.channel.send("Error in the command. Should look like this : $transfer 0xfrom_address 0xto_address 100")
            return

        try:
            scholar = get_account_from_id(cmd[1]) if cmd[0] == "$transfer_id" else get_account_from_ronin(cmd[1])
            scholar2 = get_account_from_id(cmd[2]) if cmd[0] == "$transfer_id" else get_account_from_ronin(cmd[2])
            if scholar is None:
                await message.channel.send("The from address or discord ID that you specified is not in the scholarship.")
                return

            if scholar2 is None and cmd[0] != "$transfer_id":
                ronin_address = cmd[2]
            else:
                ronin_address = scholar2.ronin_address

            try:
                tx = scholar.transfer_slp(ronin_address, int(cmd[3]))
            except ValueError as e:
                return e
            await message.channel.send("Sent **{}** SLP\n**From : ** {}\n**To : ** {}\n**Transaction : ** {} \
                                       ".format(cmd[3], cmd[1], ronin_address, tx))
        except ValueError as e:
            await message.channel.send("Error while transfering SLP : " + str(e))
        return

    ##############################################
    # Get list of axie of the account            #
    ##############################################
    if "$axies" in message.content:
        print("\nAxie list, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        if message.content == "$axies":
            scholar = get_account_from_id(message.author.id)
        elif "$axies " in message.content:
            try:
                id = message.content.split(" ")[1]
                if id.isnumeric():
                    scholar = get_account_from_id(id)
                else:
                    await message.channel.send("Error in ID. Example: $axies 496061891353903121")
                    return
            except ValueError as e:
                await message.channel.send("Error : " + str(e))
                return e

        if scholar is None:
            await message.channel.send("Error: No scholar found with this ID")
            return

        try:
            axies = scholar.get_axie_list()
            await message.channel.send("\nHere is the axie list for " + scholar.name + " account :\n")
            for axie in axies:
                await message.channel.send(scholar.axie_link(int(axie['id'])))
                await message.channel.send(file=discord.File(scholar.download_axie_image(int(axie['id']))))
        except ValueError as e:
            await message.channel.send("Error while getting axies : " + str(e))
        return
    elif message.content == "$all_axies":
        print("\nListing of all axies in the scholarship, asked by : " + message.author.name + " : " + str(message.author.id) + " at " + now.strftime("%d/%m/%Y %H:%M:%S"))
        await message.channel.send("\n------------------------------------------------\nGetting list of all the axies in the scholarship ! This can take some time.\n")

        try:
            for account in config['scholars']:
                scholar = pyaxie(config['scholars'][account]['ronin_address'], config['scholars'][account]['private_key'])
                axies = scholar.get_axie_list()
                for axie in axies:
                    await message.channel.send("\n" + scholar.axie_link(int(axie['id'])) + "\n")
                    await message.channel.send(file=discord.File(scholar.download_axie_image(int(axie['id']))))
            await message.channel.send("\n----------- END OF AXIES LIST ----------")
        except ValueError as e:
            await message.channel.send("Error while getting axies : " + str(e))
        return

    #################################################
    # Get a graph for burned/minted SLPs            #
    #################################################
    if message.content == "$graph":
        try:
            path = scholar.get_mint_burn_graph()
            discord.File(path, filename=path)
            embed = discord.Embed(title="SLP data", description=" \n Usefull SLP data like prices and minted vs burned SLP.", color=0xf5f542)
            total = json.loads(requests.get("https://explorer.roninchain.com/api/token/0xa8754b9fa15fc18bb59458815510e40a12cd2014").content)

            embed.add_field(name="Total SLP supply", value=total, inline=False)
            embed.add_field(name="SLP/USD", value=scholar.get_price("usd"), inline=True)
            embed.add_field(name="SLP/EUR", value=scholar.get_price("eur"), inline=True)
            embed.add_field(name="SLP/PHP", value=scholar.get_price("php"), inline=True)
            embed.set_image(url="attachment://" + path)
            await message.channel.send(embed)
        except ValueError as e:
            await message.channel.send("Error while getting burned/minted SLP graph : " + str(e))
        return

    #################################################
    # Get profiles links                            #
    #################################################
    if "profile" in message.content:
        url = "https://marketplace.axieinfinity.com/profile/ronin:"
        if message.content == "$all_profiles":
            try:
                l = list()
                for account in config['scholars']:
                    address = config['scholars'][account]['ronin_address']
                    l.append(account + " : " + url + address.replace('0x', '') + "/axie")
                await message.channel.send("\n".join(l) + "\n-----------\n")
            except ValueError as e:
                await message.channel.send("Error while getting profile : " + str(e))
                return e
            return

        elif message.content == "$profile":
            await message.channel.send("Here is the link for your profile **" + message.author.name +
                                       "** : " + url + scholar.ronin_address.replace('0x', '') + "/axie")
            return

        elif " " in message.content:
            try:
                id = message.content.split(" ")[1]
                if id.isnumeric():
                    scholar = get_account_from_id(id)
                else:
                    await message.channel.send("Error in discord ID. Example: $profile 496061891353903121")
                    return
            except ValueError as e:
                await message.channel.send("Error : " + str(e))
                return e
            if scholar is None:
                await message.channel.send("Error: No scholar found with this ID")
                return
            await message.channel.send("Here is the link for " + scholar.name + " profile : " + url + scholar.ronin_address.replace('0x', 'ronin:') + "/axie")
        return

    #################################################
    # Rename an axie                                #
    #################################################
    if "$rename" in message.content:
        if message.author.id != config['personal']['discord_id']:
            await message.channel.send("This command is for managers only.")
            return
        if "$rename_axie " in message.content:
            try:
                id = message.content.split(" ")[1]
                if id.isdigit():
                    axie = scholar.get_axie_detail(id)
                    scholar = get_account_from_ronin(str(axie['owner']))
                else:
                    await message.channel.send("Error in axie ID. Example: $rename_axie 1391353 new_name")
                    return

                name = message.content.split(" ")[2]
            except ValueError as e:
                await message.channel.send("Error : " + str(e))
                return e
            if scholar is None:
                await message.channel.send("Error: No scholar found with this ID")
                return
            if scholar.rename_axie(id, name):
                await message.channel.send("Axie name of " + str(id) + " changed to : **" + name + "**")
                return
            else:
                await message.channel.send("Error renaming axie : **" + str(id) + "** to : **" + name + "**")
                return

        if "$rename_account " in message.content:
            await message.channel.send("This functionality is under construction")
            return
            """
            try:
                id = message.content.split(" ")[1]
                if id.isnumeric():
                    scholar = get_account_from_id(id)
                else:
                    await message.channel.send("Error in discord ID. Example: $rename_account 496061891353903121 new_name")
                    return
                name = message.content.split(" ")[2]
            except ValueError as e:
                await message.channel.send("Error : " + str(e))
                return e
            if scholar is None:
                await message.channel.send("Error: No scholar found with this ID")
                return
            #  A CREER : scholar.rename_account(name)
            old_name = scholar.get_profile_name()
            if 'error' in old_name.lower():
                await message.channel.send("Error while renaming account. Maybe try again later ?")
                return
            await message.channel.send("Successfully renamed the account of  from : **" + old_name + "** to : **" + name + "**")
            return
            """

# Loads secret.yaml datas
with open("secret.yaml", "r") as file:
    config = yaml.safe_load(file)

# Run the client (This runs first)
client.run(config['discord_token'])
