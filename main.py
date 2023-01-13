from google.cloud import firestore
import firebase_admin
from firebase_admin import firestore
import requests
from bs4 import BeautifulSoup
from datetime import datetime

firebase_admin.initialize_app()
db = firestore.Client(project='fregov-app')

url_city = 'https://www.city.fukuoka.lg.jp'
url_top = 'https://www.city.fukuoka.lg.jp/business/keiyaku-kobo/teiankyogi.html'
res = requests.get(url_top)
content_type_encoding = res.encoding if res.encoding != 'ISO-8859-1' else None
soup = BeautifulSoup(res.content, 'html.parser', from_encoding=content_type_encoding)

tag_update = 'body > div.tpl1 > div > div.tpl1-1-2 > div > div > div > div.tpl1-1-2 > div > div > div.content.clearfix > div.menu-content.clearfix > div.right-content > div:nth-of-type(1) > div.disappear > div > div > ul > li > span > span'
tag_title = 'body > div.tpl1 > div > div.tpl1-1-2 > div > div > div > div.tpl1-1-2 > div > div > div.content.clearfix > div.menu-content.clearfix > div.right-content > div:nth-of-type(1) > div.disappear > div > div > ul > li > a > span > span'
tag_url = 'body > div.tpl1 > div > div.tpl1-1-2 > div > div > div > div.tpl1-1-2 > div > div > div.content.clearfix > div.menu-content.clearfix > div.right-content > div:nth-of-type(1) > div.disappear > div > div > ul > li > a'

elems_update = soup.select(tag_update)
elems_title = soup.select(tag_title)
elems_url = soup.select(tag_url)

def save_firestore():
	for elem_update, elem_title, elem_url in zip(elems_update, elems_title, elems_url):
		update = datetime.strptime(elem_update.contents[0], '%Y年%m月%d日').date()
		update = datetime.strftime(update, '%Y/%m/%d')
		data = {
			'cityName': '福岡県福岡市',
			'issueTitle': elem_title.contents[0],
			'updateTime': update,
			'detailUrl': url_city + elem_url.get('href')
		}

		db.collection('issues').add(data)

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.get().to_dict()}')
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

def main(event, content):
	delete_collection(db.collection('issues'), 10)
	save_firestore()