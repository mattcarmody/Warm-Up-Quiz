import bs4
import requests
import sqlite3

URL = "https://docs.python.org/3/library/calendar.html"
LIB_NAME = "calendar"

res = requests.get(URL)
try:
    res.raise_for_status()
except:
    print("Couldn't reach the destination.")

soup = bs4.BeautifulSoup(res.text, "lxml")

add_data = []

results = soup.find_all('dl')
for result in results:
    module = LIB_NAME
    title = result.find('dt').text
    title = title.rstrip("¶")
    expl = result.find('dd').text
    note = ""
    changes = result.find_all("div", {"class": ["versionchanged", "versionadded", "deprecated"]})
    for change in changes:
        note += change.text
    
    if note != "":
        expl = expl.replace(note, "")
    
    title = title.replace("\n", " ")
    title = title.strip()
    expl = expl.replace("\n", " ")
    expl = expl.strip()
    note = note.replace("\n", " ")
    note = note.strip()
    
    add_data.append((module, title, expl, note))

conn = sqlite3.connect("warmUp.db")
cur = conn.cursor()
cur.executemany("INSERT INTO python(area, concept, explanation, note) VALUES(?,?,?,?);", add_data)
conn.commit()
