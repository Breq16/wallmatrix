import os
import requests
import time

from PIL import Image, ImageDraw

from wallmatrix.fonts import font, small_font
from wallmatrix.sources import Source


api_key = os.environ["COINMARKETCAP_KEY"]
base_url = "https://pro-api.coinmarketcap.com/v1/"


coin = "ETH"


class Crypto(Source):
    def __init__(self):
        super().__init__()

        self.get_raw_coin_data()
        self.last_cache_update = time.time()

    def get_raw_coin_data(self):
        url = base_url + "cryptocurrency/quotes/latest"

        response = requests.get(url, params={
            "symbol": coin,
            "convert": "USD",
            "CMC_PRO_API_KEY": api_key
        })

        data = response.json()

        coin_data = data["data"][coin]

        price_data = coin_data["quote"]["USD"]

        self.cache = price_data
        self.last_cache_update = time.time()

    def get_cached_coin_data(self):
        if time.time() - self.last_cache_update > 300:
            self.get_raw_coin_data()

        return self.cache

    def draw_arrow(self, draw, x, y, color, inverted=False):
        if not inverted:
            draw.rectangle((x+2, y, x+2, y+4), fill=color)
            draw.rectangle((x+1, y+1, x+3, y+1), fill=color)
            draw.point((x, y+2), fill=color)
            draw.point((x+4, y+2), fill=color)
        else:
            draw.rectangle((x+2, y, x+2, y+4), fill=color)
            draw.rectangle((x+1, y+3, x+3, y+3), fill=color)
            draw.point((x, y+2), fill=color)
            draw.point((x+4, y+2), fill=color)


    def get_image(self):
        canvas = Image.new("RGB", (32, 16))

        draw = ImageDraw.Draw(canvas)

        price_data = self.get_cached_coin_data()

        # Draw the main price
        price = int(round(price_data["price"]))
        draw.text(
            (1, 1), f"${price}", font=font, fill=(255, 255, 255))

        # Draw the coin name
        draw.text((1, 10), coin, font=small_font, fill=(127, 127, 127))

        # Draw the coin price change
        price_change = int(round(price_data["percent_change_24h"]))

        if price_change > 0:
            color = (0, 255, 0)
        elif price_change == 0:
            color = (127, 127, 127)
        elif price_change < 0:
            color = (255, 0, 0)

        self.draw_arrow(draw, 14, 10, color, inverted=(price_change < 0))
        draw.text(
            (20, 10), f"{abs(price_change)}%", font=small_font, fill=color)

        return canvas

__matrix_source__ = Crypto