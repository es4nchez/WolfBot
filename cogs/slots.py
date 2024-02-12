import discord
from discord.ext import commands
import logging
import requests
from itertools import groupby
from operator import itemgetter
import datetime
from datetime import timedelta
import asyncio
import api_token
from config.config import DISCORD_SLOTS_CHANNEL

LOG = logging.basicConfig(level=logging.INFO)

async def ephemeral_message(interaction, message):
    inter = await interaction.response.send_message(content=message, ephemeral=True)
    await asyncio.sleep(5)
    await inter.delete_original_response()


async def get_personal_slots(login):
    access_token, error = api_token.get_access_token(login)
    if error:
        return error
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {'filter[future]': 'true'}
        slots = requests.get("https://api.intra.42.fr/v2/me/slots", headers=headers, params=payload).json()
        if len(str(slots)) == 2:
            return None
        slots.sort(key=itemgetter('end_at'))
        grouped_slots = [list(group) for key, group in groupby(slots, key=itemgetter('end_at'))]
        merged_slots = []
        for group in grouped_slots:
            merged_slot = group[0].copy()
            for slot in group[1:]:
                merged_slot['end_at'] = slot['end_at']
            merged_slots.append(merged_slot)
        return slots

async def delete_slot(login, id):
    access_token, error = api_token.get_access_token(login)
    if error:
        return error
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        delete_response = requests.delete(f"https://api.intra.42.fr/v2/slots/{id}", headers=headers)


class RemoveButton(discord.ui.Button):
    def __init__(self, number, slot, slots_view):
        super().__init__(label=f"X {number}", style=discord.ButtonStyle.danger)
        self.number = number
        self.slot = slot
        self.slots_view = slots_view
     
    async def callback(self, interaction: discord.Interaction):
        try:
            await delete_slot(interaction.user.name, self.slot['id'])
        except Exception as e:
            print(f"Error deleting slot {self.slot['id']} : {e}")
            await ephemeral_message(interaction, f"Error deleting slot")
        else:
            await ephemeral_message(interaction, f"Slot {self.number} successfully deleted")
            await self.slots_view.update_view(interaction) 



class SlotsButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def update_view(self, interaction: discord.Interaction):
        self.clear_items()
        await self.button_callback(self, interaction)

    @discord.ui.button(label="Update my slots", style=discord.ButtonStyle.primary)
    async def button_callback(self, button, interaction):
        logging.info(f"{interaction.user.name} button update slots")
        self.clear_items()
        user = interaction.user
        slots = await get_personal_slots(user.name)
        if slots == "No profil linked":
            await ephemeral_message(interaction, f"Login not found, please link your intra in #link-intra")
            return
        if not slots:
            await ephemeral_message(interaction, f"No slots at the moment")
            return
        embed = discord.Embed(
        title=f"Slots:",
        description="",
        color=0x570000
    )

        slots.sort(key=lambda x: x['end_at'])

        merged_slots = []
        current_slot = slots[0]

        for next_slot in slots[1:]:
            if current_slot['end_at'] == next_slot['begin_at']:
                current_slot['end_at'] = next_slot['end_at']
            else:
                merged_slots.append(current_slot.copy())
                current_slot = next_slot

        merged_slots.append(current_slot)

        counter = 1
        for slot in merged_slots:
            start_time = datetime.datetime.fromisoformat(slot['begin_at']) + timedelta(hours=1)
            end_time = datetime.datetime.fromisoformat(slot['end_at']) + timedelta(hours=1)
            duration = end_time - start_time

            total_seconds = duration.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes = remainder // 60

            start_time_str = discord.utils.format_dt(datetime.datetime.utcfromtimestamp(start_time.timestamp()), 'F')
            duration_str = f"{int(hours)}:{int(minutes)}"
        
            description_line = f"**{counter}** {start_time_str} - Duration: {duration_str}\n"
            remove_button = RemoveButton(counter, slot, self)
            self.add_item(remove_button)
            counter += 1
            embed.description += description_line

        await interaction.response.send_message(embed=embed, view=self)



class SlotsBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        me_channel = self.bot.get_channel(int(DISCORD_SLOTS_CHANNEL))
        await me_channel.purge()
        message = await me_channel.send("", view=SlotsButton())

def setup(bot):
    bot.add_cog(SlotsBot(bot))