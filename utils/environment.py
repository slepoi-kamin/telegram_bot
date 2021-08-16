from dotenv import load_dotenv
import os


def load_env(dotenv_path):
    if os.path.exists(dotenv_path):
        return load_dotenv(dotenv_path)
