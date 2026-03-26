import pandas as pd

def process_crypto_data(data):
    usd_price = data["bitcoin"]["usd"]
    gbp_price = data["bitcoin"]["gbp"]

    df = pd.DataFrame({
        "Currency": ["USD", "GBP"],
        "Price": [usd_price, gbp_price]
    })

    return df.to_dict()