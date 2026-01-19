I followd the official MCP websites guide on how to set up an MCP server. But if you have downloaded this repo you do not need to folow all the steps.

1. Python 3.10 or higher installed.
You must use the Python MCP SDK 1.2.0 or higher.

2. Install uv 
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

git clone https://github.com/your-repo/tracker.git
cd tracker

# This installs Python, creates the .venv, and installs libraries
uv sync