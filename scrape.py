# ressource : https://www.youtube.com/watch?v=ng2o98k983k&t=2377s&ab_channel=CoreySchafer

import requests
from bs4 import BeautifulSoup

source = requests.get('https://coreyms.com/').text

soup = BeautifulSoup(source,'lxml')

for article in soup.find_all('article'):

	header = article.find('h2').text
	print(header)

	content = article.find('div',class_='entry-content').p.text
	print(content)

	try:
		vid_link = article.find('iframe')['src']
		vid_id = vid_link.split('/')[4]
		vid_id = vid_id.split('?')[0]
		ytb_link = f"https//youtube.com/watch?v={vid_id}"
	except :
		ytb_link = None

	print(ytb_link)

	print()