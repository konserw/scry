import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


class Card:
    def __init__(self, name, price):
        self.price = price
        self.name = name \
            .replace("Karta Magic ", "") \
            .replace("Karta ", "") \
            .replace(" foil", "") \
            .replace(" Foil", "") \
            .replace(" promo", "") \
            .replace(" Promo", "")

    def get_summary(self):
        params = {
            "exact": self.name,
        }
        response = requests.get("https://api.scryfall.com/cards/named", params=params)
        if response.ok:
            j = json.loads(response.content)
            try:
                return [self.name, self.price, j["prices"]["usd"], j["scryfall_uri"]]
            except:
                pass
        return [self.name, self.price]

    def get_image(self):
        name = self.name.replace('"', "").replace("'", "")
        image_path = Path.cwd() / "roki" / f"{name}.png"
        if image_path.exists():
            return
        params = {
            "exact": self.name,
            "format": "image",
            "version": "png",
        }
        response = requests.get("https://api.scryfall.com/cards/named", params=params)
        if response.ok:
            image_path.write_bytes(response.content)
        else:
            print(f"karty {self.name} nie znaleziono")


def get_page(number):
    page = requests.get(
        f"https://allegrolokalnie.pl/uzytkownik/Roki_94/magic-the-gathering/single-323399?page={number}")
    soup = BeautifulSoup(page.content, 'html.parser')
    #    selection = soup.select('h3.mlc-itembox__title')
    #    return [Card(t.text) for t in selection]
    cards = []
    items = soup.select("div.mlc-itembox__offer-container")
    for item in items:
        name = item.select_one("h3").text
        price = item.select_one("span.ml-offer-price__dollars").text
        card = Card(name, price)
        cards.append(card)
    return cards


def main():
    headers = ("Name", "cena rokiego PLN", "Scryfal USD", "scryfall link")
    cards = []
    summs = []
    collection = ""
    for i in range(12):
        print(f"page {i + 1}... ", end="")
        cards += get_page(i + 1)
        print("done")
    for card in cards:
        print(card.name)
        card.get_image()
        summs.append(card.get_summary())
        collection += f"{card.name}\n"

    print(tabulate(summs, headers))
    summary = Path(__file__).parent / "roki" / "summary.html"
    summary.write_text(tabulate(summs, headers, tablefmt="html"))
    roki = Path(__file__).parent / "roki.csv"
    roki.write_text(collection)
    print("Finished!")


if __name__ == '__main__':
    main()
