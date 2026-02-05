import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_key_here")
SECRET_API_KEY = os.getenv("SECRET_API_KEY", "my_secret_hackathon_key_789")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./honeypot.db")

# GUVI API Settings
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

# Print for debugging (remove later)
print(f"Config loaded: DATABASE_URL = {DATABASE_URL}")