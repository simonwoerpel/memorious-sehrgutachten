# memorious-sehrgutachten

A simple [memorious](https://memorious.readthedocs.io/en/latest/)
extension to download documents from the
[Wissenschaftliche Dienste des Deutschen Bundestags](https://www.bundestag.de/ausarbeitungen/)

Other than the name suggests, it's not technical based on
https://sehrgutachten.de but scrapes the website of the bundestag directly.

Visit a public instance here: https://aleph.ninja/sehrgutachten

## local development

    git clone https://github.com/simonwoerpel/memorious-sehrgutachten.git
    cd memorious-sehrgutachten
    pip install -e .

### run the crawler

    memorious run sehrgutachten

### make changes

All the magic happens in `src/sehrgutachten.py` and `config/sehrgutachten.yml`

### deployment

Please refer to the official documentation of
[memorious](https://memorious.readthedocs.io/en/latest/) and
[aleph](https://alephdata.org) on how to setup the infrastructure...
