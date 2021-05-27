# memorious-sehrgutachten

A simple [memorious](https://memorious.readthedocs.io/en/latest/)
extension to download documents from the
[Wissenschaftliche Dienste des Deutschen Bundestags](https://www.bundestag.de/ausarbeitungen/)

Other than the name suggests, it's not technical based on
https://sehrgutachten.de but scrapes the website of the bundestag directly.

It downloads the files and metadata into a local folder.

## usage

The `startdate` and `enddate` parameters need to be set via env vars:

    STARTDATE=2021-05-01 ENDDATE=`date '+%Y-%m-%d'` memorious run sehrgutachten

if running locally, make sure the memorious config env is set as well:

    MEMORIOUS_CONFIG_PATH=src

## local installation / developement

    git clone https://github.com/simonwoerpel/memorious-sehrgutachten.git
    cd memorious-sehrgutachten
    pip install -e .

### make changes

All the magic happens in `src/sehrgutachten.py` and `src/sehrgutachten.yml`

## production use / deployment

To use the scraper for a production basis, a proper redis and psql should be used.

Please refer to the official documentation of
[memorious](https://memorious.readthedocs.io/en/latest/installation.html#installation-running-your-own-crawlers)
