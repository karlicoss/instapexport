#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, NamedTuple, Sequence, Union, List, TypeVar, Iterator, Optional

import dal_helper
from dal_helper import Json, PathIsh, Res


logger = dal_helper.logger('endoexport', level='debug')

Bid = str
Hid = str


class Highlight(NamedTuple):
    raw: Json
    # dt: datetime # utc
    # uid: Hid
    # bid: Bid
    # text: str
    # note: Optional[str]
    # url: str
    # title: str

    @property
    def instapaper_link(self) -> str:
        return f'https://www.instapaper.com/read/{self.bid}/{self.uid}'


class Bookmark(NamedTuple):
    raw: Json
    # bid: Bid
    # dt: datetime # utc
    # url: str
    # title: str

    @property
    def instapaper_link(self) -> str:
        return f'https://www.instapaper.com/read/{self.bid}'



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

    def bookmarks(self) -> Dict[Bid, Bookmark]:
        return self._get_all()[0]

    def highlights(self) -> Dict[Hid, Highlight]:
        return self._get_all()[1]



def demo(dao: DAL) -> None:
    # TODO split errors properly? move it to dal_helper?
    highlights = list(w for w in dao.highlights() if not isinstance(w, Exception))

    print(f"Parsed {len(highlights)} highlights")


if __name__ == '__main__':
    dal_helper.main(DAL=DAL, demo=demo)
