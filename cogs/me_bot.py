import discord
from discord.ext import commands
import requests
import api_token
import logging
from config.config import DISCORD_ME_CHANNEL

LOG = logging.basicConfig(level=logging.INFO)

async def get_personal_info(login):
    """
    Get the data from the 42 api
    """
    access_token, error = api_token.get_access_token(login)
    if error:
        return error
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        profil = requests.get("https://api.intra.42.fr/v2/me", headers=headers).json()
    if len(str(profil)) == 2:
        return None
    return profil


class InfosButton(discord.ui.View):
    """
    View for the button My infos
    """
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="My infos", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        logging.info(f"{interaction.user.name} : button me")
        user = interaction.user
        infos = await get_personal_info(user.name)
        if not infos:
            await interaction.response.send_message(content="Login not found, please link your intra in <#1202272862245752922>", ephemeral=True)
            return
        embed = discord.Embed(
            title=f"Info for {infos['usual_full_name']}",
            description=f"""
                        Login: {infos['login']}
                        Grade: {infos['cursus_users'][1]['grade']}
                        Level: {infos['cursus_users'][1]['level']}
                        Wallets: {infos['wallet']}
                        Correction points: {infos['correction_point']}
                        """,
            color=0x00ff00)
        embed.set_thumbnail(url=infos['image']['versions']['small'])
        await interaction.response.send_message(embed=embed, ephemeral=True)



class MeBot(commands.Cog):
    """
    Cog for a command to get personnal info
    """
    def __init__(self, bot):
        self.bot = bot
        self.members = {}

    @commands.Cog.listener()
    async def on_ready(self):
        me_channel = self.bot.get_channel(int(DISCORD_ME_CHANNEL))
        await me_channel.purge()
        await me_channel.send("", view=InfosButton())

def setup(bot):
    bot.add_cog(MeBot(bot))

