# DB Schenker MCP Tracker

This project is an **MCP (Model Context Protocol) server** that tracks DB Schenker shipments by intercepting internal tracking data from the public DB Schenker website.  
It uses **Playwright** to run a headless browser and capture detailed shipment information that is not available through traditional scraping or simple HTTP requests.

The tool can be:
- Run as an MCP server for use with **Claude Desktop**
- Tested locally via a terminal script


# Instructions on how to set up and test the tool
First you need to have Python 3.10 or higher installed.
You must use the Python MCP SDK 1.2.0 or higher.

### Install uv 
macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

Windows
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

### Clone repo
git clone https://github.com/Josefgus/schenker-tracker
cd schenker-tracker
uv sync

### Install the headless browser
uv run playwright install chromium

### To start MCP server
uv run python schenker_server.py

### To test in terminal
uv run python shenker_terminal.py

### To test with Claude for Desktop
install latest version of claude desktop https://claude.com/download
Run claude

open App configuration at ~/Library/Application Support/Claude/claude_desktop_config.json (for macOS/linux)

or 
AppData\Claude\claude_desktop_config.json (for Windows)

add our mcp server like so:
```
{
  "mcpServers": {
    "schenker_tracker": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\ABSOLUTE\\PATH\\TO\\PARENT\\FOLDER\\SCHENKER-TRACKER",
        "run",
        "schenker_server.py"
      ]
    }
  }
}
```


You may need to put the full path to the uv executable in the command field. You can get this by running which uv on macOS/Linux or where uv on Windows.

Restart Claude and the mcp server should be detected, then you clould ask for tracking updates for a package.

### How to test the tool 
To test the tool in the terminal, run the script schenker_terminal.py
Enter a reference number and wait for the response to be printed in the terminal. (e.g., '1806203236'). 
Printed in the terminal is all relevent information given the reference number.

# How did I approach extracting data from schenker?
### Initial Exploration of the project. 
I started by manually checking the public DB Schenker tracking portal to see what data was visible and how it was fetched. I used browser developer tools to analyze network traffic and the structure of the site to find where the information came from. I soon realized that a standard GET or POST request would not work because the website is a modern application that relies on client-side JavaScript to show data. The site also uses cookies and security checks like CAPTCHAs to stop automated scraping. To solve the JavaScript and security problems I decided to use a headless browser with Playwright. This allows the script to run a full browser without a GUI and execute all JavaScript like a real user. It also handles cookies and sessions automatically. I asked an AI for help to brainstorm ways to catch background network requests which led to the final solution. 

I wanted to track every individual package but I was stuck. The swedish website i was using did not include this data. After some googling i hapend to land on the US website and I saw that the US version of the tracking app provides much more information. I analyzed the background traffic of the US site and found a specific JSON response that contained the detailed data I needed. I updated the code to use the international tracking URL and intercept the raw JSON data instead of scraping text from the screen. This makes the data very accurate. The tool now provides the full shipment history and specific status updates for every single package in the shipment.