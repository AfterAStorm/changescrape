
from .base import Scraper
from requests import Session
from bs4 import BeautifulSoup

class Gruv(Scraper):
    name = 'gruv'
    
    def __init__(self, category: str):
        super().__init__()
        self.category = category
        self.base_url = 'https://www.gruv.com'
        self.url = f'{self.base_url}/category/{category}'
        self.session = Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        self.session.headers['Referer'] = f'https://www.gruv.com/category/4k_ultra_hd_bluray_movies_pre_order' # fair enough, it's a form
    
    def scrape(self):
        # get
        #page = self.session.get(self.url)
        page = self.session.post(self.url, data={'ddl-per-page': 'ALL', 'ddl-sortby': 'RD'}, allow_redirects=True)
        #print(page.content)
        #print(page.status_code)
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, 'html.parser')
        cards = soup.select('.card:not(.p-3)') # random invisible element?
        
        found = []
        for card in cards:
            body_tag = card.select_one('.card-body')
            if not body_tag:
                print('Invalid card, missing body', card)
                continue
            title_tag = body_tag.select_one('a')
            price_tag = card.select_one('.price')
            image_tag = card.select_one('img')
            
            if not price_tag:
                print('Invalid card, missing price', card)
                continue
            if not title_tag:
                print('Invalid card, missing title', card)
                continue
            if not image_tag:
                print('Invalid card, missing image', card)
                continue
            price = float(price_tag.text.strip('$ \n'))
            title = title_tag.text.strip()
            url = self.base_url + title_tag.attrs.get('href', '/') # /product/...
            img = 'https:' + image_tag.attrs.get('src', '').removeprefix('https:')
            found.append({
                'price': price,
                'title': title,
                'url': url,
                'image_url': (img.split('?')[0]) # remove ?width=250, high quality
            })
        
        return found