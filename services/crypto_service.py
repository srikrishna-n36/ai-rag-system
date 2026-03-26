import httpx
import logging

logging.basicConfig(level=logging.INFO)

async def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,gbp"
    logging.info("Fetching crypto data...")

    try:
        async with httpx.AsyncClient() as client:
            logging.info("Fetching crypto data...")
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            return response.json()

    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return {"error": str(e)}