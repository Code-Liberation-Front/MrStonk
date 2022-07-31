#cogs.General runs all of the message commands for general purpose
import nextcord
from nextcord.ext import commands
import config

extension = config.extension

class General(commands.Cog):

    def __init__(self, client):
        print("General initialized Successfully")

def setup(client):
    client.add_cog(General(client))