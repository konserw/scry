from pathlib import Path

import requests
from bs4 import BeautifulSoup


class Collection:
    def __init__(self, collection_id, name):
        self.collection_id = collection_id
        self.name = name
        self._search_url = f"https://mtgcollectionbuilder.com/collections/{collection_id}/search"

    def search_card(self, card):
        page = requests.post(self._search_url, data={"cardNameSearch": card})
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup.select('tr.success')

    def search_card_list(self, search_list):
        found = []
        print(f"Searching in {self.name}:")
        for card in search_list:
            # print(f"Searching for card: {card}")
            rows = self.search_card(card)
            # print(f"Found {len(rows)} rows")
            if rows:
                print("!", end="")
                for row in rows:
                    found.append(str(row))
            else:
                print(".", end="")
        print(f"\nFinished! {len(found)} hits")
        return f"""
         <h1><a href="https://mtgcollectionbuilder.com/collections/{self.collection_id}">{self.name} collection</a></h1>
        <table>
    <thead>
    <tr>
        <th class="header headerSortDown">Name</th>
        <th class="header headerSortUp">Qt.</th>
        <th class="header headerSortUp">Foil Qt.</th>
        <th class="header">Set</th>
        <th class="header">Low</th>
        <th class="header">Avg</th>
        <th class="header">High</th>
        <th class="header">Foil</th>
    </tr>
    </thead>
    <tbody>
    {'\n'.join(found)}
    </tbody>
    </table>
        """


def main():
    search_list = []
    for path in Path("__file__").parent.glob("*.txt"):
        search_list += path.read_text().splitlines()

    roki = Collection("48069", "Roki")
    wiesiu = Collection("49774", "Wiesiu")

    print("\n\nSaving report to report.html")
    html_report = f"""
    <html><body>
   {roki.search_card_list(search_list)}
   {wiesiu.search_card_list(search_list)}
    </body></html>"""
    Path("./report.html").write_text(html_report)


if __name__ == '__main__':
    main()
