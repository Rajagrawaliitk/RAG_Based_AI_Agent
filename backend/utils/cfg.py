import os, yaml
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        with open("configs/settings.yaml", "r") as f:
            self.settings = yaml.safe_load(f)

        self.amazon_assoc_tag = os.getenv("AMAZON_ASSOC_TAG", "")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

cfg = Config()
