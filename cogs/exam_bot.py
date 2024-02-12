from discord.ext import commands, tasks
from datetime import datetime, timedelta
from api.intra import IntraAPIClient
import sqlite3
import os
from config.config import DISCORD_EXAM_CHANNEL

payload_date = {
    "filter[future]": "true",
}

projects_dict = {}

class ExamBot(commands.Cog):
    """
    Cog for a retrieve the next exam, and update the grades in real time
    """
    def __init__(self, bot):
        self.bot = bot
        self.start_date = None
        self.end_date = None
        db_file = 'databases/exams.db'
        if not os.path.exists(db_file):
            self.create_database()
        
        self.db_connection = sqlite3.connect(db_file)
        self.db_cursor = self.db_connection.cursor()

    def create_database(self):
        with sqlite3.connect('databases/exams.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS exams
                              (id INTEGER PRIMARY KEY, exam_name TEXT, begin_at TEXT, end_at TEXT)''')
            conn.commit()

    def get_date(self):
        """
        Get the dates for the upcoming exams
        """
        ic = IntraAPIClient(progress_bar=False)
        results = ic.pages_threaded("campus/47/exams", params=payload_date)
        for exam in results:
            exam_id, start_str, end_str = exam['id'], exam['begin_at'], exam['end_at']
            start = datetime.fromisoformat(start_str[:-1]) - timedelta(minutes=1)
            self.real_start = (datetime.fromisoformat(start_str[:-1]) + timedelta(hours=1)).strftime('%s')
            end = datetime.fromisoformat(end_str[:-1]) + timedelta(days=1)
        
            self.db_cursor.execute("SELECT COUNT(*) FROM exams WHERE exam_name = ? AND begin_at = ? AND end_at = ?", (exam_id, start, end))
            count = self.db_cursor.fetchone()[0]
        
            if count == 0:
                self.db_cursor.execute("INSERT INTO exams (exam_name, begin_at, end_at) VALUES (?, ?, ?)", (exam_id, start, end))
                self.db_connection.commit()
        return

    def get_exams_grades(self):
        """
        Get the grades in real time
        """
        ic = IntraAPIClient(progress_bar=False)
        results = {}
        start_date_iso = self.start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_date_iso = self.end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        payload_grades = {
            "filter[campus]": 47,
            "sort": "updated_at",
            "range[updated_at]": f"{start_date_iso},{end_date_iso}",}
        for res in ic.pages_threaded("teams", params=payload_grades):
            project_id = res['project_id']
            if project_id not in projects_dict:
                projects_dict[project_id] = ic.pages_threaded(f"projects/{project_id}")["name"]
            if "Exam" in projects_dict[project_id]:
                user_login = res["users"][0]["login"]
                results[user_login] = [projects_dict[project_id], res["final_mark"], res["status"], res["updated_at"]]
        sorted_results = sorted(results.items(), key=lambda x: (int(x[1][0].split(" ")[-1]), x[1][1] if x[1][1] is not None else 0, x[0]))
        return dict(sorted_results)


    def check_date(self):
        """
        Set start_date and end_date to the next exam dates
        """
        conn = sqlite3.connect('databases/exams.db')
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute("SELECT * FROM exams WHERE begin_at >= ? ORDER BY begin_at ASC", (now,))
        exams = cursor.fetchall()
        cursor.close()
        conn.close()

        if exams:
            self.start_date = datetime.strptime(exams[0][2], '%Y-%m-%d %H:%M:%S')
            self.end_date = datetime.strptime(exams[0][3], '%Y-%m-%d %H:%M:%S')
        return


    @tasks.loop(seconds=3600.0)
    async def exam_date_update(self):
        """
        Loop to update the exam's dates
        """
        self.get_date()

    @tasks.loop(seconds=20.0)
    async def exam_info_update(self, message):
        """
        Main loop for update the grades
        """
        self.check_date()
        if self.start_date > datetime.now() < self.end_date:
            real_start = (self.start_date + timedelta(hours=1, minutes=1)).strftime('%s')
            await message.edit(content=f"Next exam : <t:{real_start}:F>, <t:{real_start}:R>")
            return
        grades = self.get_exams_grades()
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
        """
        Start the cog, clean the channel and get the first dates
        """
        exam_channel = self.bot.get_channel(int(DISCORD_EXAM_CHANNEL))
        await exam_channel.purge()
        initial_message = await exam_channel.send("Initializing... ")
        self.get_date()
        self.exam_info_update.start(initial_message)

def setup(bot):
    bot.add_cog(ExamBot(bot))

