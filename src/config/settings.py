"""
Configuration module: loads environment variables for the ATS microservice.
All sensitive credentials are read from environment variables (never hardcoded).
"""
import os
from dotenv import load_dotenv

# Load variables from a .env file when running locally
load_dotenv()

# Recruitee API credentials
RECRUITEE_API_KEY: str = os.getenv("RECRUITEE_API_KEY", "")
RECRUITEE_BASE_URL: str = os.getenv("RECRUITEE_BASE_URL", "https://api.recruitee.com/c")

# Validate that required config is present
if not RECRUITEE_API_KEY:
    raise EnvironmentError(
        "RECRUITEE_API_KEY is not set. Please add it to your .env file or environment."
    )

if not RECRUITEE_BASE_URL:
    raise EnvironmentError(
        "RECRUITEE_BASE_URL is not set. Please add it to your .env file or environment."
    )
