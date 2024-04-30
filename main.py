import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathos.multiprocessing import ProcessPool


class Collection:
    def __init__(self, collection_id, name):
        self.collection_id = collection_id
        self.name = name
        self._search_url = f"https://mtgcollectionbuilder.com/collections/{collection_id}/search"
        self.found = []

    def search_card(self, card):
        strings = []
        page = requests.post(self._search_url, data={"cardNameSearch": card})
        soup = BeautifulSoup(page.content, 'html.parser')
        # return soup.select('tr.success')
        for r in soup.select('tr.success'):
            tds = r.select("td")
            name = tds[0].text.strip()
            img_url = r.td.a["data-img"]
            row = f'<tr><td><a class="thumbnail" href="{tds[0].a["href"]}" target="_blank" rel="noopener noreferrer">{name}<span><img src="{img_url}" /></span></a></td>{tds[1]}{tds[2]}{tds[3]}{tds[4]}</tr>'
            strings.append(row)
        return strings

    def search_card_list(self, search_list):
        print(f"Searching in {self.name}:", end="")
        #        self.found += self.search_card(search_list[0])
        #        return
        pool = ProcessPool(nodes=8)
        results = pool.amap(self.search_card, search_list)
        while not results.ready():
            time.sleep(1)
            print(".", end='')

        for r in results.get():
            self.found += r
        print(" Done!")

    def get_html(self):
        ret = f"""
<h1><a href="https://mtgcollectionbuilder.com/collections/{self.collection_id}">{self.name} collection</a></h1>
<table class="styled-table">
    <thead>
    <tr>
        <th class="header">Name</th>
        <th class="header">Qt.</th>
        <th class="header">Foil Qt.</th>
        <th class="header">Set</th>
        <th class="header">Low $</th>
    </tr>
    </thead>
    <tbody>
    {'\n'.join(self.found)}
    </tbody>
</table>
        """
        return ret


def process_file(path):
    out = set()
    regex = re.compile(r"(?:\d+ )?([^(]*)(?:\(.*\))?(?: .*)?")
    lines = path.read_text().splitlines()
    for line in lines:
        if not line or line[0] == "#":
            continue
        match = regex.match(line)
        if match:
            out.add(match.group(1).strip())
    return out


def main():
    search_list = set()
    for path in Path.cwd().glob("*.txt"):
        print(f"reading from {path}")
        search_list.update(process_file(path))

    #    search_list = ["Island", "Plains"]
    collections = []
    friends_path = Path.cwd() / "friends.csv"
    friends_list = friends_path.read_text().splitlines()
    reader = csv.reader(friends_list[1:], delimiter=',')
    for row in reader:
        collections.append(Collection(row[1], row[0]))

    for collection in collections:
        collection.search_card_list(search_list)
    print("\n\nSaving report to report.html")
    html_report = """
<html>
<head>
<link rel="stylesheet" href="thumbs.css">
<link rel="stylesheet" href="table.css">
</head>
<body>
"""
    for collection in collections:
        html_report += collection.get_html()
    html_report += "\n</body></html>"
    Path("./report.html").write_text(html_report)


if __name__ == '__main__':
    main()
