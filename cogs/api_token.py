import sqlite3
import os
import requests
from config import config

def get_access_token(login):
    """
    Get the token for a user nor update it if expired
    """
    db_connection = sqlite3.connect('databases/users.db')
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT * FROM users WHERE discord_id = ?", (login,))
    user = db_cursor.fetchone()
    if user:
        access_token = user[3]
        refresh_token = user[4]
    else:
        return None, "No profile linked"

    headers = {"Authorization": f"Bearer {access_token}"}
    slots = requests.get("https://api.intra.42.fr/v2/me", headers=headers)
    if 'error' in slots and slots['error'] == 'invalid_token':
        refresh_payload = {
            'grant_type': 'refresh_token',
            'client_id': config.CLIENT,
            'client_secret': config.SECRET,
            'refresh_token': refresh_token
        }
        refresh_response = requests.post("https://api.intra.42.fr/oauth/token", data=refresh_payload)
        refresh_json_response = refresh_response.json()
        access_token = refresh_json_response.get('access_token')

        try:
            conn = sqlite3.connect('databases/users.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET access_token=? WHERE login=?", (access_token, login))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print("SQLite error:", e)

    return access_token, None