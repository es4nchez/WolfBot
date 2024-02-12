import discord
from discord.ext import commands
from api.intra import IntraAPIClient
import sqlite3
from config.config import DISCORD_LINKINTRA_CHANNEL, BACKEND_PORT, BACKEND_URL



async def intra_linking():
    ic = IntraAPIClient(progress_bar=False)

    conn = sqlite3.connect('databases/users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tokens
                      (key TEXT PRIMARY KEY, value TEXT)''')
    cursor.execute("INSERT OR REPLACE INTO tokens (key, value) VALUES (?, ?)", ("login", "token"))
    conn.commit()
    cursor.execute("SELECT value FROM tokens WHERE key=?", ("test",))
    forty_two_access_token = cursor.fetchone()
    conn.close()
    
    return True



class InfosButton(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Link 42 Intra", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        user = interaction.user
        await interaction.response.send_message(f'{BACKEND_URL}:{BACKEND_PORT}/link-intra?discord_id={user}', ephemeral=True)
        

class LinkIntraBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        link_intra_channel = self.bot.get_channel(int(DISCORD_LINKINTRA_CHANNEL))
        await link_intra_channel.purge()
        message = await link_intra_channel.send("", view=InfosButton(link_intra_channel))

def setup(bot):
    bot.add_cog(LinkIntraBot(bot))

def setup(bot):
    bot.add_cog(LinkIntraBot(bot))

