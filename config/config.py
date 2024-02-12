import yaml

with open('config/secrets.yml', 'r') as f:
    config = yaml.load(f, Loader=yaml.BaseLoader)

CLIENT = config['intra42']['CLIENT']
SECRET = config['intra42']['SECRET']
CALLBACK_URL = config['intra42']['CALLBACK_URL']
URI = config['intra42']['URI']
ENDPOINT = config['intra42']['ENDPOINT']

BACKEND_URL = config['backend']['BACKEND_URL']
BACKEND_PORT = config['backend']['BACKEND_PORT']

DISCORD_BOT_TOKEN = config['bot']['DISCORD_BOT_TOKEN']
DISCORD_SERVER_ID = config['bot']['DISCORD_SERVER_ID']
DISCORD_EVAL_CHANNEL = config['bot']['DISCORD_EVAL_CHANNEL']
DISCORD_EXAM_CHANNEL = config['bot']['DISCORD_EXAM_CHANNEL']
DISCORD_LINKINTRA_CHANNEL = config['bot']['DISCORD_LINKINTRA_CHANNEL']
DISCORD_SLOTS_CHANNEL = config['bot']['DISCORD_SLOTS_CHANNEL']
DISCORD_ME_CHANNEL = config['bot']['DISCORD_ME_CHANNEL']