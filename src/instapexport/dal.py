#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, NamedTuple, Sequence, Union, List, TypeVar, Optional
import pytz

from .exporthelpers import dal_helper, logging_helper
from .exporthelpers.dal_helper import Json, PathIsh, Res

logger = logging_helper.logger('endoexport', level='debug')

Bid = str
Hid = str


def _make_dt(ts: float) -> datetime:
    return pytz.utc.localize(datetime.utcfromtimestamp(ts))


class Highlight(NamedTuple):
    raw: Json

    # TODO shit. maybe it's not utc...
    @property
    def dt(self) -> datetime:
        "UTC"
        return _make_dt(self.raw['time'])

    @property
    def hid(self) -> Bid:
        return str(self.raw['highlight_id'])

    @property
    def bid(self) -> Bid:
        return str(self.raw['bookmark_id'])

    @property
    def text(self) -> str:
        return self.raw['text']

    @property
    def note(self) -> Optional[str]:
        return self.raw['note']

    @property
    def instapaper_link(self) -> str:
        return f'https://instapaper.com/read/{self.bid}/{self.hid}'


# TODO use cproprety here? generally might be interesting to benchmark/profile
class Bookmark(NamedTuple):
    raw: Json

    @property
    def bid(self) -> Bid:
        return str(self.raw['bookmark_id'])

    @property
    def dt(self) -> datetime:
        "UTC"
        return _make_dt(self.raw['time'])

    @property
    def url(self) -> str:
        return self.raw['url']

    @property
    def title(self) -> str:
        return self.raw['title']

    @property
    def instapaper_link(self) -> str:
        return f'https://instapaper.com/read/{self.bid}'


class Page(NamedTuple):
    bookmark: Bookmark
    highlights: List[Highlight]

    @property
    def dt(self) -> datetime:
        return self.bookmark.dt

    @property
    def url(self) -> str:
        return self.bookmark.url

    @property
    def title(self) -> str:
        return self.bookmark.title


class DAL:
    def __init__(self, sources: Sequence[PathIsh]) -> None:
        self.sources = list(map(Path, sources))
    # TODO assume that stuff only gets added, so we can be iterative?

    # TODO yield? again, my idea with simultaneous iterators fits well here..
    def _get_all(self):
        # bookmarks and highlights are processed simultaneously, so makes sense to do them in single method
        # TODO unclear how to distinguish deleted and ones past 500 limit :shrug:

        # TODO highlights don't make much sense without bookmarks as they only have bookmark id...
        # TODO yeah ok just access them through pages. Maybe even reasonable for DAL?
        # it's ok for hl not to have URL if we access it through page
        all_hls = {}
        all_bks = {}

        # TODO not sure if necessary to sort here.. get_files handles this already
        for f in sorted(self.sources):
            j = json.loads(f.read_text())

            hls: List[Json] = []
            bks: List[Json] = []
            if 'highlights' in j:
                # legacy format
                hls.extend(j['highlights'])
                bks.extend(j['bookmarks'])
            else:
                # current format
                for folder, b in j['bookmarks'].items():
                    hls.extend(b['highlights'])
                    bks.extend(b['bookmarks'])

            # TODO FIXME hl_key assert?
            for h in hls:
                hid = str(h['highlight_id'])
                all_hls[hid] = Highlight(h)
            for b in bks:
                bid = str(b['bookmark_id'])
                all_bks[bid] = Bookmark(b)
        return all_bks, all_hls

    # TODO support folders? I don't use them so let it be homework for other people..

    # TODO shit. should that be a list instead?
    def bookmarks(self) -> Dict[Bid, Bookmark]:
        return self._get_all()[0]

    def highlights(self) -> Dict[Hid, Highlight]:
        return self._get_all()[1]

    def pages(self) -> List[Page]:
        bks, hls = self._get_all()
        page2hls: Dict[Bid, List[Highlight]] = {bid: [] for bid in bks}
        for hid, h in hls.items():
            page2hls[h.bid].append(h)

        pages_ = [
            Page(
                bookmark=bks[page_bid],
                highlights=list(sorted(page_hls, key=lambda b: b.dt))
            )
            for page_bid, page_hls in page2hls.items()
        ]
        return list(sorted(pages_, key=lambda p: p.dt))


def demo(dao: DAL) -> None:
    # TODO split errors properly? move it to dal_helper?
    # highlights = list(w for w in dao.highlights() if not isinstance(w, Exception))

    pages = dao.pages()
    print(f"Parsed {len(pages)} pages")

    from collections import Counter
    from pprint import pprint
    common = Counter({(x.url, x.title): len(x.highlights) for x in pages}).most_common(10)
    print("10 most highlighed pages:")
    for (url, title), count in common:
        print(f'{count:4d} {url} "{title}"')


if __name__ == '__main__':
    dal_helper.main(DAL=DAL, demo=demo)
