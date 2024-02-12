import discord
from discord.ext import commands
import logging
from cogs.webserver import *
import os
import sys
from config.config import *

def setup_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix="/", intents=intents)
    
    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger()
    
    sys.path.append(os.path.abspath('cogs'))

    @bot.event
    async def on_ready():
        LOG.info("Wolf ready, let's gather some data!")
        webserver = Webserver(bot)
        await webserver.setup()

    bot.load_extension("exam_bot")
    bot.load_extension("slots")
    bot.load_extension("me_bot")
    bot.load_extension("link_intra")
    bot.load_extension("search_login")
    bot.add_cog(Webserver(bot))

    return bot

def main():
    bot = setup_bot()
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()
