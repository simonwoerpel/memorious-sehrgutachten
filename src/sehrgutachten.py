# https://github.com/okfde/sehrgutachten/blob/master/app/scrapers/wd_ausarbeitungen_scraper.rb

import os
import re
from datetime import datetime
from urllib.parse import urljoin

from furl import furl

MONTHS = (
    "januar",
    "februar",
    "märz",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "dezember",
)
WD_NAMES = {
    "wd1": "Geschichte, Zeitgeschichte und Politik",
    "wd2": "Auswärtiges, Völkerrecht, Wirtschaftliche Zusammenarbeit und Entwicklung, Verteidigung, Menschenrechte und humanitäre Hilfe",  # noqa
    "wd3": "Verfassung und Verwaltung",
    "wd4": "Haushalt und Finanzen",
    "wd5": "Wirtschaft und Technologie, Ernährung, Landwirtschaft und Verbraucherschutz, Tourismus",  # noqa
    "wd6": "Arbeit und Soziales",
    "wd7": "Zivil-, Straf- und Verfahrensrecht, Umweltschutzrecht, Verkehr, Bau und Stadtentwicklung",  # noqa
    "wd8": "Umwelt, Naturschutz, Reaktorsicherheit, Bildung und Forschung",
    "wd9": "Gesundheit, Familie, Senioren, Frauen und Jugend",
    "wd10": "Kultur, Medien und Sport",
    "pe6": "Europa",
}


def _xp(html, path):
    part = html.xpath(path)
    if isinstance(part, list) and part:
        part = part[0]
    if hasattr(part, "text"):
        part = part.text
    if isinstance(part, str):
        return part.strip()
    return part


def _clean_date(value):
    value = value.lower().replace(" ", "")
    for i, month in enumerate(MONTHS):
        if month in value:
            value = value.replace(month, "%s." % str(i + 1).zfill(2))
            return datetime.strptime(value, "%d.%m.%Y").date().isoformat()


def parse(context, data):
    res = context.http.rehash(data)

    rows = res.html.xpath('//table[@class="table bt-table-data"]/tbody/tr')

    for row in rows:
        path = _xp(row, './/a[@class="bt-link-dokument"]/@href')
        if not path:
            continue

        url = urljoin(data["url"], path)

        try:
            title = _xp(row, ".//div[@class='bt-documents-description']/p/strong")
            file_name = url.split("/")[-1]
            _, ext = os.path.splitext(file_name)
            detail_data = {
                "url": url,
                "title": title,
                "file_name": title + ext if title else file_name,
                "published_at": _clean_date(
                    _xp(row, './td[@data-th="Veröffentlichung"]/p')
                ),
                "keywords": _xp(row, './td[@data-th="Thema"]/p'),
                "category": _xp(row, './td[@data-th="Dokumenttyp"]/p'),
                "source_url": url,
                "publisher": "Wissenschaftliche Dienste des Deutschen Bundestages",
                "publisher_url": "https://www.bundestag.de/ausarbeitungen/",
            }

            wd_match = re.match(
                r"(?P<wd>wd|pe)\s*(?P<wd_id>\d+)[\s-]+(?P<doc_id>\d+\/\d+)",
                detail_data["title"],
                re.IGNORECASE,
            )

            if wd_match:
                wd_id = wd_match.group("wd").lower() + wd_match.group("wd_id")
                wd_id_nice = f"{wd_match.group('wd')} {wd_match.group('wd_id')}"
                wd_name = WD_NAMES.get(wd_id, wd_id_nice)
                detail_data[
                    "publisher"
                ] = f'Wissenschaftlicher Dienst "{wd_id_nice}: {wd_name}" des Deutschen Bundestages'  # noqa
                detail_data[
                    "publisher_url"
                ] = f"https://www.bundestag.de/dokumente/analysen/{wd_id}"
                detail_data["foreign_id"] = "-".join((wd_id, wd_match.group("doc_id")))

            context.emit("download", data=detail_data)

        except Exception as e:
            context.log.error(f"Error at `{url}`: {e}")

    # pagination
    if len(rows):
        fu = furl(data["url"])
        fu.args["offset"] = int(fu.args["limit"]) + int(fu.args.get("offset", 0))
        context.emit("fetch", data={"url": fu.url})
