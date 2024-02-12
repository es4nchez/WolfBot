import discord
from discord.ext import commands, tasks
from datetime import datetime
from api.intra import IntraAPIClient
from config.config import DISCORD_EVAL_CHANNEL

payload = {
    "filter[campus]":47,
    "sort": "updated_at",
    "page":1,
    "range[updated_at]": "2024-01-29T15:00:16.000Z,2024-01-30T20:28:16.000Z",
}

class EvalBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_evals(self):
        ic = IntraAPIClient(progress_bar=False)
        results = ic.pages_threaded("teams", params=payload)
        return results

    @tasks.loop(seconds=20.0)
    async def eval_info_update(self, message):
        grades = self.get_evals()
        message_content = ""

        for user, data in grades.items():
            exam_name, grade, status, date_completed = data[0], data[1], data[2], data[3]

            if grade == 100:
                formatted_date = datetime.strptime(date_completed, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Hh%M:%S') if date_completed is not None else ""
                message_content += f"**{user}**  -  {exam_name[5:]} - {grade} :white_check_mark: - {formatted_date}\n"
            elif status == "finished" and grade != 100:
                formatted_date = datetime.strptime(date_completed, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Hh%M:%S') if date_completed is not None else ""
                message_content += f"**{user}**  -  {exam_name[5:]} - {grade} :x: -  {formatted_date}\n"
            else:
                message_content += f"**{user}**  -  {exam_name[5:]} - {grade}\n"

        formatted_date = datetime.now().strftime("%A %d %B %Y, %Hh%M:%S")
        message_content += f"\nLast update: {formatted_date}"

        await message.edit(content=message_content)

    @commands.Cog.listener()
    async def on_ready(self):
        exam_channel = self.bot.get_channel(DISCORD_EVAL_CHANNEL)
        await exam_channel.purge()
        initial_message = await exam_channel.send("Initializing... ")
        self.eval_info_update.start(initial_message)


def setup(bot):
    bot.add_cog(EvalBot(bot))
