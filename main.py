#—————————————————————————Plugins————————————————————————————
import os

from pymongo import MongoClient
from discord.ext import commands
from config import settings
#—————————————————————————————————————————————————————————————


#———————————————————DB, Start—————————————————————————————————
cluster = MongoClient("тут данные от БД")

client = commands.Bot(command_prefix = settings['PREFIX'])
client.remove_command('help')

servers = [1291493323017551882, 626146788591534090]
#—————————————————————————————————————————————————————————————



# #—————————————————————————————————————————————————————————————
@client.event 
async def on_ready():
    print("Main file has been loaded \n-----")
# #—————————————————————————————————————————————————————————————



#-загрузка Cogs-#—————————————————————————————————————————————————————————————
cogfiles = [
    f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs/") if filename.endswith(".py")
]

for cogfile in cogfiles:
    try:
        client.load_extension(cogfile)
    except Exception as error:
        print(error)
# #—————————————————————————————————————————————————————————————


#запуск
client.run(settings['TOKEN'])