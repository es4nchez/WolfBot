import discord
from discord.ext import commands
from api.intra import IntraAPIClient
import sqlite3
import json
import logging

LOG = logging.basicConfig(level=logging.INFO)


class SearchLogin(commands.Cog):
    """
    Add a commande to search a login in the intra42
    """
    def __init__(self, bot):
        self.bot = bot
        self.ic = IntraAPIClient(progress_bar=False)

    @commands.slash_command(name="search", description="Search a 42 user by login")
    async def search(self, ctx, login: str):
        """
        Command: Search a 42 user by login
        """
        logging.info(f"{ctx.author} : command search {login}")
        payload = {"filter[login]": f"{login}",}
        try:
            user = self.ic.pages_threaded("users", params=payload)[0]
        except:
            await ctx.response.send_message(content="User not found, maybe the login is wrong, or 42 API is down", ephemeral=True)
            return
        if user['location'] == None:
            loc = "Not logged"
        else:
            loc = user['location']
        embed = discord.Embed(
            title=f"Info for {user['usual_full_name']}",
            description=f"""
                        :bust_in_silhouette: Login: {user['login']}
                        :briefcase: Kind: {user['kind']}
                        :person_swimming: Pool: {user['pool_month']} {user['pool_year']}
                        :bookmark: Correction points: {user['correction_point']}
                        :moneybag: Wallets: {user['wallet']}
                        :computer: Location: {loc}
                        """,
            color=0x00ff00)
        embed.set_thumbnail(url=user['image']['versions']['small'])
        await ctx.response.send_message(embed=embed, ephemeral=True)
       

def setup(bot):
    bot.add_cog(SearchLogin(bot))