from discord.ext import commands
from aiohttp import web
import os
import requests
from cryptography.fernet import Fernet
import logging
import sqlite3
from config import config

def add_user(username, user_data):
    try:
        conn = sqlite3.connect('databases/users.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (username TEXT PRIMARY KEY,
                           id INTEGER,
                           discord_id TEXT,
                           access_token TEXT,
                           refresh_token TEXT)''')

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.execute("UPDATE users SET id=?, discord_id=?, access_token=?, refresh_token=? WHERE username=?",
                           (user_data['id'], user_data['discord_id'], user_data['access_token'], user_data["refresh_token"], username))
        else:
            cursor.execute("INSERT INTO users (username, id, discord_id, access_token, refresh_token) VALUES (?, ?, ?, ?, ?)",
                           (username, user_data['id'], user_data['discord_id'], user_data['access_token'], user_data["refresh_token"]))

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("SQLite error:", e)


class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def encrypt_discord_id(self, discord_id):
        return self.cipher_suite.encrypt(discord_id.encode())

    def decrypt_discord_id(self, encrypted_id):
        try:
            discord_id = self.cipher_suite.decrypt(encrypted_id).decode()
            return discord_id
        except Exception as e:
            logging.error(f"Decryption Error: {e}")
            raise


    async def linking(self, request):
        discord_id = request.query.get('discord_id')
        encrypted_id = self.encrypt_discord_id(discord_id)
    
    
        redirect_response = web.Response(status=302)
        redirect_response.set_cookie('discord_id', encrypted_id.decode('utf-8'))
        redirect_response.headers['Location'] = config.CALLBACK_URL
        return redirect_response

    async def callback(self, request):
        code = request.query.get('code')
        encrypted_id = request.cookies.get('discord_id', None)
        if encrypted_id is None:
            raise web.HTTPBadRequest(text="Cookie not found. Unauthorized request.")
        discord_id = self.decrypt_discord_id(encrypted_id)

        payload = {
        'grant_type': 'authorization_code',
        'client_id': config.CLIENT,
        'client_secret': config.SECRET,
        'code': code,
        'redirect_uri': f'{config.BACKEND_URL}:{config.BACKEND_PORT}/callback'
        }
        response = requests.post("https://api.intra.42.fr/oauth/token", data=payload)
        json_response = response.json()
        access_token = json_response.get('access_token')
        refresh_token = json_response.get('refresh_token')
        headers = {"Authorization": f"Bearer {access_token}"}
        profil = requests.get("https://api.intra.42.fr/v2/me", headers=headers).json()
        id = profil.get('id')
        login = profil.get('login')
        login_data = {
        "id": id,
        "discord_id": discord_id,
        "access_token": access_token,
        "refresh_token": refresh_token}
        add_user(login, login_data)
        redirect_url = f'discord:///channels/{config.DISCORD_SERVER_ID}'
        return web.HTTPFound(redirect_url)
    

    async def setup(self):
        app = web.Application()
        app.router.add_get('/callback', self.callback)
        app.router.add_get('/link-intra', self.linking)
        runner = web.AppRunner(app)
        await runner.setup()
        web_server_port = int(os.environ.get('PORT', config.BACKEND_PORT))
        site = web.TCPSite(runner, host=f'0.0.0.0', port=web_server_port)
        await site.start()