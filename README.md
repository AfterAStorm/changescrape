# ChangeScrape #

A lil' tool designed to allow expandable mass scrape-age of whatever you so please!

## Features ##

* Split into 2 major scripts
  * **Notifiers** - Designates how new items are displayed
  * **Scrapers** - What is actually going be "scraped", generally websites that you'd like to "watch"
* Easy-ish configuration
* Expandable

## How to use ##

To use it, just run the `main.py` script to your liking, ex: ``python3 main.py``.

Creating new notifiers/scrapers is easy as looking how it already works, using the pre-existing classes. They are automagically found on startup.

It's up to your needs to make it run on startup, as a service, or likewise.

## Configuration ##

The configuration (`config.toml`) is split up using toml arrays and "sub sections", ex:

```toml
[[instance]]
interval = '10m'

    [instance.notifier]
    notifier = 'discord_webhook'
    url = 'https://discord.com/api/webhooks/id/token'
    username = 'ChangeScape'
    content = '<@userid> <@&roleid>'

    [instance.scraper]
    scraper = 'gruv'
    category = '4k_ultra_hd_bluray_movies_pre_order' # the ...com/category/<name>

[[instance]]
interval = '20h'

    [instance.notifier]
    notifier = 'discord_webhook'
    url = 'https://discord.com/api/webhooks/id/token'
    username = 'ChangeScape'
    content = '<@userid> <@&roleid>'

    [instance.scraper]
    scraper = 'another_user_defined_scraper'
    uses_kwargs_in_constructor = 'aaaaaaa'
```

The interval is formatted as: `<number><suffix>`, where suffix can be any of the following:
* **s** - seconds
* **m** - minutes
* **h** - hours
* **d** - days

Otherwise, everything else is either the name defined in the `<class>.name` attribute, or an argument in the class constructor (\_\_init\_\_).

## Implementation Details ##

All scrapers are initially run at startup.

Internally, it uses a sqlite3 database to save what items have already been found, columns are in the first few lines of ``main.py``. New columns can be added as needed, or similiar.