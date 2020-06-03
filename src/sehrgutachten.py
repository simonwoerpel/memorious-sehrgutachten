# https://github.com/okfde/sehrgutachten/blob/master/app/scrapers/wd_ausarbeitungen_scraper.rb

import os
import re

from urllib.parse import urljoin, urlparse
from datetime import datetime

from alephclient.api import AlephAPI
from followthemoney import model
from memorious.core import manager
from memorious.helpers import make_id
from normality import normalize


# init memorious config
# FIXME - this should happen somehow different
# when figured out how to properly "package" crawlers...
def init_memorious():
    file_path = os.path.dirname(__file__)
    config_path = os.path.join(file_path, '..', 'config')
    manager.load_path(config_path)


DEFAULT_URL = 'https://www.bundestag.de/ajax/filterlist/de/dokumente/ausarbeitungen/474644-474644/'
PER_PAGE = 10
MONTHS = (
    'januar',
    'februar',
    'märz',
    'april',
    'mai',
    'juni',
    'juli',
    'august',
    'september',
    'oktober',
    'november',
    'dezember'
)
WD_NAMES = {
    'wd1': 'Geschichte, Zeitgeschichte und Politik',
    'wd2': 'Auswärtiges, Völkerrecht, Wirtschaftliche Zusammenarbeit und Entwicklung, Verteidigung, Menschenrechte und humanitäre Hilfe',  # noqa
    'wd3': 'Verfassung und Verwaltung',
    'wd4': 'Haushalt und Finanzen',
    'wd5': 'Wirtschaft und Technologie, Ernährung, Landwirtschaft und Verbraucherschutz, Tourismus',
    'wd6': 'Arbeit und Soziales',
    'wd7': 'Zivil-, Straf- und Verfahrensrecht, Umweltschutzrecht, Verkehr, Bau und Stadtentwicklung',
    'wd8': 'Umwelt, Naturschutz, Reaktorsicherheit, Bildung und Forschung',
    'wd9': 'Gesundheit, Familie, Senioren, Frauen und Jugend',
    'wd10': 'Kultur, Medien und Sport',
    'pe6': 'Europa'
}
META = (
    'url',
    'source_url',
    'foreign_id',
    'title',
    'author',
    'file_name',
    'modified_at',
    'published_at'
)


def _make_url_key(url):
    return make_id(normalize(url))


def _xp(html, path):
    part = html.xpath(path)
    if isinstance(part, list) and part:
        part = part[0]
    if hasattr(part, 'text'):
        part = part.text
    if isinstance(part, str):
        return part.strip()
    return part


def _clean_date(value):
    value = value.lower().replace(' ', '')
    for i, month in enumerate(MONTHS):
        if month in value:
            value = value.replace(month, '%s.' % str(i + 1).zfill(2))
            return datetime.strptime(value, '%d.%m.%Y').date().isoformat()


def init(context, data):
    store = context.datastore['sehrgutachten']
    url = context.get('url', DEFAULT_URL)
    host = '{0}://{1}'.format(*urlparse(url))
    per_page = context.get('per_page', PER_PAGE)
    page = data.get('page', 1)

    res = context.http.get(url, params={
        'limit': per_page,
        'offset': page * per_page if page > 1 else 0
    })

    rows = res.html.xpath('//table[@class="table bt-table-data"]/tbody/tr')

    for row in rows:
        path = _xp(row, './/a[@class="bt-link-dokument"]/@href')
        if not path:
            continue

        url = urljoin(host, path)
        key = _make_url_key(url)
        if store.find_one(key=key):
            continue

        try:
            title = _xp(row, ".//div[@class='bt-documents-description']/p/strong")
            data = {
                'url': url,
                'key': key,
                'title': title,
                'file_name': title or url.split('/')[-1],
                'published_at': _clean_date(_xp(row, './td[@data-th="Veröffentlichung"]/p')),
                'keywords': _xp(row, './td[@data-th="Thema"]/p'),
                'category': _xp(row, './td[@data-th="Dokumenttyp"]/p'),
                'mime_type': 'application/pdf',
                'source_url': url,
                'publisher': 'Wissenschaftliche Dienste des Deutschen Bundestages',
                'publisher_url': 'https://www.bundestag.de/ausarbeitungen/'
            }

            wd_match = re.match(r'(?P<wd>wd|pe)\s*(?P<wd_id>\d+).*(?P<doc_id>\d+\/\d+)', data['title'], re.IGNORECASE)
            if wd_match:
                wd_id = wd_match.group('wd').lower() + wd_match.group('wd_id')
                wd_id_nice = f"{wd_match.group('wd')} {wd_match.group('wd_id')}"
                wd_name = WD_NAMES.get(wd_id, wd_id_nice)
                data['publisher'] = f'Wissenschaftlicher Dienst "{wd_id_nice}: {wd_name}" des Deutschen Bundestages'  # noqa
                data['publisher_url'] = f'https://www.bundestag.de/dokumente/analysen/{wd_id}'
                data['foreign_id'] = '-'.join((wd_id, wd_match.group('doc_id')))

            store.insert(data)
            context.emit(data={k: v for k, v in data.items() if k in META and v})

        except Exception as e:
            context.log.error(f"Error at `{url}`: {e}")

    if len(rows):
        context.recurse(data={'page': page + 1})


def enrich(context, data):
    store = context.datastore['sehrgutachten']
    enrich_data = store.find_one(key=_make_url_key(data['url']))
    if enrich_data:
        api = AlephAPI()
        document = data['aleph_id']
        collection = data['aleph_collection_id']
        publisher = model.make_entity('PublicBody')
        publisher.make_id(enrich_data['publisher'])
        publisher.add('name', enrich_data['publisher'])
        publisher.add('website', enrich_data['publisher_url'])
        publisher.add('country', 'Germany')

        link = model.make_entity('UnknownLink')
        link.make_id('link', publisher.id, document)
        link.add('subject', document)
        link.add('object', publisher)
        link.add('role', 'publisher')

        api.write_entities(collection, [publisher.to_dict(), link.to_dict()])
