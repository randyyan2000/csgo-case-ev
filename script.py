from bs4 import BeautifulSoup
import requests

case_id = 303 # Prisma 2 Case
base_url = "https://csgostash.com/case/"
ignore_knives = True

quality_probabilities = {
    "yellow":       0.0026,
    "covert":       0.0064,
    "classified":   0.032,
    "restricted":   0.1598,
    "mil-spec":     0.7992,
}

wear_probabilities = {
    "factory new":      0.07,
    "minimal wear":     0.08,
    "field-tested":     0.23,
    "well-worn":        0.07,
    "battle-scarred":   0.55
}

if ignore_knives:
    for quality in quality_probabilities:
        if quality != "yellow":
            quality_probabilities[quality] /= 0.9974


r = requests.get(base_url + str(case_id))
if r.status_code != 200:
    raise Exception("request failed")

# print(r.text)
soup = BeautifulSoup(r.text, "html.parser")

query = {
    "tag": "div",
    "attrs": {
        "class": "col-lg-4 col-md-6 col-widen text-center"
    },
}

items = soup.find_all(query["tag"], attrs=query["attrs"])
print(len(items))

prices_per_quality = {
    "yellow":       [],
    "covert":       [],
    "classified":   [],
    "restricted":   [],
    "mil-spec":     []
}

for item in items:
    # find quality
    quality_tag = item.find("a", class_="nounderline")
    if quality_tag is None:
        # knife item
        if ignore_knives:
            continue
    quality = quality_tag["title"].split()[1].lower()
    quality_prob = quality_probabilities[quality]

    # find link to prices
    link_tag = item.find("div", class_="details-link")
    link = link_tag.find("a")["href"]
    print(quality, link)

    #use link to get prices
    r = requests.get(link)
    if r.status_code != 200:
        raise Exception(f"request failed: {link}")

    item_soup = BeautifulSoup(r.text, "html.parser")
    price_tags = item_soup.find("div", id="prices").find_all("div", class_="btn-group-sm btn-group-justified")
    print(len(price_tags))
    ev = 0
    for price_tag in price_tags:
        price = price_tag.find("span", class_="pull-right")
        if price is None:
            continue
        price = float(price.string[1:])
        wears = price_tag.find_all("span", class_="pull-left")
        print([wear.string for wear in wears], price)
        is_stattrak = len(wears) > 1
        wear = wears[-1].string.lower()
        if is_stattrak:
            ev += 0.1 * price * wear_probabilities[wear]
        else:
            ev += 0.9 * price * wear_probabilities[wear]
    prices_per_quality[quality].append(ev)


ev = 0
print(prices_per_quality)
for quality in prices_per_quality:
    prices = prices_per_quality[quality]
    if len(prices) <= 0:
        continue
    avg = sum(prices) / len(prices)
    ev += avg * quality_probabilities[quality]

print(ev)
        

    

    

