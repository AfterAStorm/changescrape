
from .base import Notifier
from requests import Session
from datetime import datetime, timezone

class DiscordWebhookNotifier(Notifier):
    name = 'discord_webhook'
    
    def __init__(self, url: str, username: str='ChangeScrape Notifier', content='<@everyone>'):
        super().__init__()
        self.url = url
        self.username = username
        self.content = content # for pings and such
        self.session = Session()
    
    def notify(self, contents: list[dict]):
        embeds = []
        for i in range(min(len(contents), 10)): # there should never be more than 10... so... whatever
            content = contents[i]
            embeds.append({
                    'title': content.get('title'),
                    #'type': 'rich',
                    'color': 5957270,
                    'url': content.get('url'),
                    'image': {
                        'url': content.get('image_url')
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'fields': [
                        {
                            'name': 'Price',
                            'value': '$' + str(content.get('price', 'n/a'))
                        }
                    ]
                })
        
        res = self.session.post(self.url, json={
            'username': self.username,
            'content': self.content,
            'embeds': embeds
        })
        res.raise_for_status()