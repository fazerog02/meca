import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_client import BaseClient

# load .env
load_dotenv(verbose=True)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# get env val
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

FIREBASE_CRED_FILE_NAME = os.environ.get("FIREBASE_CRED_FILE_NAME")

MECA_CATEGORY_NAME = os.environ.get("MECA_CATEGORY_NAME")
WORKING_ROOM_VC_NAME = os.environ.get("WORKING_ROOM_VC_NAME")
LOG_TC_NAME = os.environ.get("LOG_TC_NAME")

# init firestore
cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), FIREBASE_CRED_FILE_NAME))
firebase_admin.initialize_app(cred)
db: BaseClient = firestore.client()
