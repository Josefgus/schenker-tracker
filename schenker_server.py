import asyncio
import json
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("DB-Schenker-Tracker")

async def get_schenker_data(reference_number):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        captured_json = None

        async def handle_response(response):
            nonlocal captured_json
            # Look for the LandStt:* JSON response, which contains all the shipment data
            if f"LandStt:" in response.url:
                if response.status == 200:
                    data = await response.json()
                    if "sttNumber" in data:
                        captured_json = data
        
        # Attach the response handler
        page.on("response", handle_response)
        
        url = f"https://www.dbschenker.com/app/tracking-public/?language_region=en-US_US&refNumber={reference_number}"
        
        # Navigate to the tracking page for the given reference number
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            return captured_json
        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()

# Format the raw JSON data into a structured output
def format_output(raw_json):
    # Handle error case, e.g., if no data found
    if not raw_json:
        return {"error": "Could not find LandStt-file. Check reference number."}
    if "error" in raw_json:
        return raw_json
        
    loc = raw_json.get("location", {})
    goods = raw_json.get("goods", {})
    
    shipper = loc.get("shipperPlace", {})
    consignee = loc.get("consigneePlace", {})

    return {
        "summary": {
            "sttNumber": raw_json.get("sttNumber"),
            "product": raw_json.get("product"),
            "pieces": goods.get("pieces"),
            "volume": f"{goods.get('volume', {}).get('value')} {goods.get('volume', {}).get('unit')}",
            "dimensions": goods.get("dimensions") or None,
            "total_weight": f"{goods.get('weight', {}).get('value')} {goods.get('weight', {}).get('unit')}",
            "estimated_delivery": raw_json.get("deliveryDate", {}).get("estimated")
        },
        "route": {
            "from": f"{shipper.get('postCode')}, {shipper.get('city')}, {shipper.get('country')}",
            "to": f"{consignee.get('postCode')}, {consignee.get('city')}, {consignee.get('country')}"
        },
        "shipment_history": [
            {
                "date": e.get("date"),
                "status": e.get("comment") or e.get("code"),
                "location": e.get("location", {}).get("name") if isinstance(e.get("location"), dict) else e.get("location")
            } for e in raw_json.get("events", [])
        ],
        "individual_packages": [
            {
                "package_id": pkg.get("id"),
                "events": [
                    {
                        "date": pe.get("date"),
                        "status_code": pe.get("code"),
                        "location": pe.get("location")
                    } for pe in pkg.get("events", [])
                ]
            } for pkg in raw_json.get("packages", [])
        ]
    }

# MCP tool definition
@mcp.tool()
async def track_schenker(reference_number: str) -> str:
    """
        Tracks a DB Schenker shipment and returns detailed package events and history.
        
        Args:
            reference_number: The shipment reference number (e.g., '1806203236').
    """
    raw_data = await get_schenker_data(reference_number)
    formatted = format_output(raw_data)
    return json.dumps(formatted, indent=2, ensure_ascii=False)

if __name__ == "__main__":

    mcp.run()