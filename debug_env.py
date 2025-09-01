import os
from dotenv import load_dotenv

# First, try to load the .env file
print("Attempting to load .env file...")
load_dotenv()

# Check if environment variables are loaded correctly
print("\nEnvironment Variables from .env:")
env_vars = [
    "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", 
    "EMAIL_FROM", "EMAIL_TO"
]

for var in env_vars:
    value = os.getenv(var, "")
    # Hide password in output
    if var == "SMTP_PASS" and value:
        display_value = "*" * len(value)
    else:
        display_value = value
    print(f"{var}: '{display_value}'")

# Check if .env file exists and read its raw content
env_path = ".env"
if os.path.exists(env_path):
    print("\n.env file exists. Reading raw content:")
    try:
        with open(env_path, "r") as f:
            content = f.read()
            print("------- .env file content -------")
            # Print each line, hiding password
            for line in content.splitlines():
                if line.startswith("SMTP_PASS="):
                    parts = line.split("=", 1)
                    if len(parts) > 1:
                        line = f"{parts[0]}={'*' * len(parts[1])}"
                print(line)
            print("----------------------------------")
    except Exception as e:
        print(f"Error reading .env file: {e}")
else:
    print("\n.env file does not exist!")