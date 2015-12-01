#!/usr/bin/python3

from urllib.request import urlretrieve
from urllib.error import HTTPError
from lxml import etree
from time import strftime, sleep
import codecs
import re
import pystache

url_olymp = "https://olympiads.ru/zaoch/2015-16/current_standings.shtml"

persons = [
    {"name": "Третьяков Глеб", "grade": 11, "group": "B", "id": 69448},
    {"name": "Андрей Рахмановский", "grade": 11, "group": "B", "id": 69512},
    {"name": "Николенко Даниил", "grade": 9, "group": "A", "id": 12400},
    {"name": "Ушерович Мария", "grade": 11, "group": "B", "id": 66252},
    {"name": "Греков Илья", "grade": 9, "group": "B", "id": 68240},
    {"name": "Бурлаков Александр", "grade": 11, "group": "—", "id": 70720},
    {"name": "Солонков Денис", "grade": 11, "group": "A", "id": 9196},
    {"name": "Ройтман Сергей", "grade": 10, "group": "D2", "id": 69798},
    {"name": "Шеховцов Александр", "grade": 7, "group": "C", "id": 61559},
    {"name": "Марков Вениамин", "grade": 10, "group": "B", "id": 70415},
    {"name": "Шатов Олег", "grade": 8, "group": "C", "id": 70265},
    {"name": "Кончагин Андрей", "grade": 11, "group": "A", "id": 5792},
    {"name": "Ивановский Сергей", "grade": 11, "group": "B", "id": 70633},
    {"name": "Новиков Иван", "grade": 11, "group": "—", "id": 70715},
    {"name": "Кондратенко Александра", "grade": 10, "group": "C", "id": 69501},
    {"name": "Ветлин Владислав", "grade": 10, "group": "D2", "id": 70914},
    {"name": "Кожакин Кирилл", "grade": 10, "group": "—", "id": 67282},
    {"name": "Титов Дмитрий", "grade": 11, "group": "—", "id": 70289},
]

def update_person(person, data):
    if "place" in person.keys():
        return
    person["place"] = data[0].text
    person["solved"] = int(data[-2].text)
    person["points"] = int(data[-1].text)
    person["submits"] = 0
    person["tasks"] = []
    for task in data[3: -2]:
        string = etree.tostring(task).decode("utf-8")
        match = re.match("^<td class=\"st_prob\">(<b>)?([0-9]*)(?:</b>)? \(([0-9]*)\)</td>$", string)
        if match is not None:
            groups = list(match.groups())
            person["submits"] += int(groups[2])
            person["tasks"].append({"full" if groups[0] is not None else "partial": True,
                                    "points": int(groups[1]),
                                    "submits": int(groups[2])})
        else:
            person["tasks"].append({"not_submitted": True})


# Fetching data from the server
pages = 1
while True:
    try:
        urlretrieve(url_olymp.format(str(pages) if pages > 1 else ""), "{:02}".format(pages))
    except HTTPError:
        pages -= 1
        break
    #print(pages)
    sleep(1)
    break
    # pages += 1

if pages < 1:
    exit(1)

# Splitting data into lines
lines = []
for page in range(1, pages + 1):
    data = codecs.open("{:02}".format(page), "r", "koi8-r").read()
    lines += etree.HTML(data).xpath("/html/body/table[2]/tr/td[2]/table[2]/tr[position()>1]")

# Updating persons list
for line in lines:
    if not len(line.xpath("td[2]/a")):
        continue
    value = re.findall("&user_id=([0-9]*)&", line[1][0].get("href"))
    if len(value) != 1:
        continue
    value = int(value[0])
    person = list(filter(lambda x: x["id"] == value, persons))
    if len(person) != 1:
        continue
    person = person[0]
    update_person(person, line)

# Additional information
persons.sort(key=lambda person: (-person["points"], -person["solved"], person["submits"]))
for local_place, person in enumerate(persons):
    person["local_place"] = local_place + 1

# Rendering
html = pystache.render(open("template.html").read(), {
    'update_time': strftime("%H:%M:%S %d.%m.%Y"),
    'persons': persons
})
out_file = open("results.html", "w")
print(html, file=out_file)
out_file.close()
