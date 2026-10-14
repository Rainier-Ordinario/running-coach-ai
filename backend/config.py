import os

from dotenv import load_dotenv

load_dotenv()

# `or` (not a getenv default) so a blank CLAUDE_MODEL= line in .env still
# falls back instead of sending an empty model name to the API.
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL") or "claude-opus-4-7"
