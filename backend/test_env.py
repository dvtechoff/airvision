import os
from dotenv import load_dotenv

print("=== ENV VARIABLE TEST ===")

print("Before loading .env:")
print(f"OPENAQ_API_KEY: {os.getenv('OPENAQ_API_KEY', 'NOT FOUND')}")

# Load .env file
load_dotenv()

print("\nAfter loading .env:")
openaq_key = os.getenv('OPENAQ_API_KEY', 'NOT FOUND')
print(f"OPENAQ_API_KEY: {openaq_key}")

# Check if .env file exists
import pathlib
env_path = pathlib.Path('.env')
print(f"\n.env file exists: {env_path.exists()}")

if env_path.exists():
    content = env_path.read_text()
    print(f"\n.env file content (first 200 chars):")
    print(content[:200])
    
    # Look for OPENAQ specifically
    lines = content.split('\n')
    for line in lines:
        if 'OPENAQ_API_KEY' in line:
            print(f"\nFound OPENAQ line: {line}")