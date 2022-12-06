import requests


def get_book_info(query, isbn=True):
    if isbn:
        r = requests.get(f'https://openlibrary.org/api/books?bibkeys=ISBN:{query}&format=json&jscmd=data')
        j = r.json()[f"ISBN:{query}"]
    else:
        r = requests.get(f'https://openlibrary.org/api/books?bibkeys=OLID:{query}&format=json&jscmd=data')
        j = r.json()[f"OLID:{query}"]
    print(r.status_code)

    title = j['title']
    try:
        # See if there is a defined by statement for multiple authors
        by_statement = j['by_statement']
    except KeyError:
        # Otherwise get first authors name
        by_statement = j['authors'][0]['name']
    # https://covers.openlibrary.org/b/id/135182-S.jpg -> 135182-S.jpg -> 135182
    cover_id = j['cover']['medium'].split('/')[-1].split('-')[0]
    print(cover_id)

    return {"title": title, "author": by_statement, "cover_id": cover_id}