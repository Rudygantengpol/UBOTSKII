import os
from dotenv import load_dotenv

load_dotenv(".env")

MAX_BOT = int(os.getenv("MAX_BOT", "9999"))

DEVS = list(map(int, os.getenv("DEVS", "8125506794").split()))

API_ID = int(os.getenv("API_ID", "36685296"))

API_HASH = os.getenv("API_HASH", "0ff2963ccec9b8a38dcbd54b08ef6b2e")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8006482819:AAE7VDR0P3kGKyRQAk9aMbF3Mz8B6KTZYlI")

OWNER_ID = int(os.getenv("OWNER_ID", "1092285211"))

BLACKLIST_CHAT = list(map(int, os.getenv("BLACKLIST_CHAT", "-1003701593699").split()))

RMBG_API = os.getenv("RMBG_API", "s6tucqWKCDGQPTfaV78xxTZs")

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://sihevil217_db_user:JNDzSIxGsCEye4MJ@cluster0.vk3ukzf.mongodb.net/?appName=Cluster0")

LOGS_MAKER_UBOT = int(os.getenv("LOGS_MAKER_UBOT", "-1003356598260"))