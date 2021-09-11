# Pyaxie bot

<img src="https://github.com/vmercadi/pyaxie-bot/blob/master/img/Pyaxie.png" alt="logo" width="200"/>

## Description

A python discord bot to help you manage your **Axie Infinity** scholarships.  
This is based on my other Axie project : [Pyaxie](https://github.com/vmercadi/pyaxie) which is a python lib to interact with Axie world.

If you don't have the API URL for Axies informations, some of the functionalities will not work.  
You will have to find this by yourself and then add it in secret.yaml as it is forbidden to make it public in Axie ToS.

If you encounter a problem or have a question, you can join the discord server : https://discord.gg/gqaSv2PZbF

## [Follow this step-by-step guide to install and use the bot](https://github.com/vmercadi/pyaxie-bot/wiki)

As I'm adding a bit every day, you'll have to update the project as much as you can (infos in the discord).  
Here is a command to easily update : `mv secret.yaml asecret.yaml; git pull; mv asecret.yaml secret.yaml`
With this command, you'll not have to write the config in secret.yaml again

## BOT commands

**Commands for everybody :**

`$infos` = Send all the infos about your account  
`$infos 506011891353903121` = Send infos for the given discord ID  
`$qr` = Send your QR code  
`$mmr` = Send your current MMR  
`$rank` = Send your current rank  
`$axies` = Send the list of axies of your account  
`$axies 506011891353903121` = Send axies list of given discord ID  
`$profile` = Send link to the axie account of user  
`$profile 506011891353903121` = Send link to the axie account of the specified user  
`$self_payout` = Allow scholar to claim. Money is sent to their personal ronin and to you.
`$self_payout 0xScholar_Personal_Address` = Allow scholar to claim and payout to the personal address they give. (NOT FULLY TESTED YET)  

**Commands for manager :**

`$claim 506011891353903121` = Claim for the given discord ID   
`$all_claim` = Claim for all the scholars   
`$all_mmr` = Send scholar list sorted by MMR  
`$all_rank` = Send scholar list sorted by rank  
`$all_axies`= Send list of all the axies in the scholarship   
`$all_profiles`= Send list of all the scholars profiles  
`$payout` = Split SLP and send the available SLP to manager and scholars  
`$payout me` = Send all scholarship SLP directly to manager account with no split  
`$transfer 0xfrom_address 0xto_addres amount` = Transfer SLP  

## Donation

Thanks to [ZracheSs](https://github.com/ZracheSs-xyZ) for his Payout and QR script code.
And thanks to Andy for his help with debug !

**My ronin address :**  ronin:f561bb92d33e4feaae617a182264a4c7d7272948  
**My ethereum address :** 0x60900b1740E9e164137Db9b982d9681A2E74446c  

**ZracheSs ronin address :** ronin:a04d88fbd1cf579a83741ad6cd51748a4e2e2b6a  
**ZracheSs ethereum address :** 0x3C133521589daFa7213E5c98C74464a9577bEE01  

## Examples

![](https://github.com/vmercadi/pyaxie-bot/blob/master/img/qr.PNG)  
![](https://github.com/vmercadi/pyaxie-bot/blob/master/img/infos.PNG)  
![](https://github.com/vmercadi/pyaxie-bot/blob/master/img/transfer.PNG)  
![](https://github.com/vmercadi/pyaxie-bot/blob/master/img/all_axies.PNG)  
![](https://github.com/vmercadi/pyaxie-bot/blob/master/img/all_rank.PNG)  
![](https://github.com/vmercadi/pyaxie-bot/blob/master/img/all_mmr.PNG)  


