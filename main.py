
print('ChangeScrape')
print()

from toml import load
# from inspect import signature # TODO: more type checking?
import sqlite3
from time import time, sleep

# load config
with open('config.toml', 'r') as f:
    config = load(f)
    
# load persistence
db = sqlite3.connect('persist.db')
db.execute('CREATE TABLE IF NOT EXISTS found(source, url, image_url, title, price)')
db.commit()

# load notifiers
from scrapers import Scraper, scrapers
from notifiers import Notifier, notifiers

# define instance
class Instance:
    scraper: Scraper
    notifier: Notifier
    
    interval: int # seconds
    interval_verbose: str
    last_scrape: float = 0

def find_with_name(classes: list, name: str):
    for clazz in classes:
        if clazz.name == name:
            return clazz

def compare_found(source: str, found: list[dict]) -> list[dict]:
    new = []
    for thing in found: # we always assumes it returns the right thing, :fingerscrossed: 
        args = [source, thing['url'], thing['image_url'], thing['title'], thing['price']]
        # check if it exists
        cursor = db.cursor()
        cursor.execute('SELECT * FROM found WHERE source=? AND url=? AND image_url=? AND title=? AND price=?', args)
        existing: list = cursor.fetchone()
        
        if existing == None:
            #print('Found new item!', thing['title'])
            new.append(thing)
            cursor.execute('INSERT INTO found (source, url, image_url, title, price) VALUES (?, ?, ?, ?, ?)', args)
            db.commit()
        else:
            pass#print('Already exists', thing['title'])
        
        cursor.close()
    return new

def handle_input_error(context_name: str, err: TypeError):
    arg: str = err.args[0]
    
    if arg.find('required position argument') >= 0:
        print(f'{context_name} is missing required argument {arg.split("\'")[1]}')
    elif arg.find('an unexpected keyword argument') >= 0:
        print(f'{context_name} got non-existent argument {arg.split("\'")[1]}')
    else:
        print(f'Unrecognized error for {context_name}:')
        raise err

SUFFIX_MAP = {
    's': 1,
    'm': 60, # seconds to minutes
    'h': 60 * 60, # seconds to hours
    'd': 60 * 60 * 24, # seconds to days
}

def parse_interval(value: str) -> int:
    suffix = value[-1]
    num_str = value[0:len(value) - 1] # so, seconds
    
    try:
        num = float(num_str)
    except:
        print('Invalid interval', value)
        return 60 * 30 # 30m default
    
    if suffix not in SUFFIX_MAP:
        print('Invalid interval suffix', suffix, 'valid:', ', '.join(SUFFIX_MAP.keys()))
    mapped = SUFFIX_MAP[suffix]
    return int(num * mapped) # seconds to X

# parse instances
creating_instances: list[dict] = config.get('instance', list)
instances: list[Instance] = []
for instance in creating_instances:
    # get
    scraper: dict = instance.get('scraper', dict)
    notifier: dict = instance.get('notifier', dict)
    interval: str | None = instance.get('interval', None)
    
    # names
    scraper_name: str = scraper.get('scraper', '')
    notifier_name: str = notifier.get('notifier', '')
    
    # classes
    scraper_class = find_with_name(scrapers, scraper_name)
    notifier_class = find_with_name(notifiers, notifier_name)
    
    if scraper_class == None:
        print('Invalid scraper name', scraper_name)
        continue
    if notifier_class == None:
        print('Invalid notifier name', notifier_name)
        continue
    if interval == None:
        print('Invalid interval')
        continue
    
    # remove class names
    del scraper['scraper']
    del notifier['notifier']
    
    # create
    instance = Instance()
    try:
        instance.scraper = scraper_class(**scraper)
    except TypeError as e:
        handle_input_error(scraper_name, e)
        continue
        
    try:
        instance.notifier = notifier_class(**notifier)
    except TypeError as e:
        handle_input_error(notifier_name, e)
        continue
    
    instance.interval_verbose = interval
    instance.interval = parse_interval(interval)
    
    instances.append(instance)

# "RUN"
print(len(instances), 'instances running:')
for instance in instances:
    print(f'from {instance.scraper.name} to {instance.notifier.name} every {instance.interval_verbose}')
print()

while True:
    min_wait_time = 9999999999999999999
    for instance in instances:
        now = time()
        last = instance.last_scrape
        if now - last > instance.interval:
            instance.last_scrape = now
            try:
                scraped = instance.scraper.scrape()
                difference = compare_found(instance.scraper.name, scraped)
                if len(difference) > 0:
                    print(f'Found differences from {instance.scraper.name} to {instance.notifier.name}')
                    instance.notifier.notify(difference)
            except Exception as e:
                print(f'An error occured while fetching from {instance.scraper.name} to {instance.notifier.name}:')
                print(e)
                instance.last_scrape = now - instance.interval + 30 # try again in 30 seconds
        min_wait_time = min(min_wait_time, instance.interval - (now - instance.last_scrape))
    
    # print('Waiting', min_wait_time)
    sleep(min_wait_time)