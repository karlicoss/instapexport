#!/usr/bin/env python3
import json
import sys

from kython.misc import import_from

instapaper = import_from('/L/zzz_syncthing/soft/backup/instapaper/', 'instapaper')

from instapaper import Instapaper

from instapaper_secrets import *

LIMIT = 500

# on first login, execute:
if False:
    USERNAME = None
    PASSWORD = None

    from instapaper import Instapaper
    api = Instapaper(OAUTH_ID, OAUTH_SECRET)
    odata = api.login(USERNAME, PASSWORD)
    print("paste this into your secrets file")
    print(repr(odata))
    sys.exit(0)

api = Instapaper(OAUTH_ID, OAUTH_SECRET)
api.login_with_token(**OAUTH_PARAMS)

res = {
    'bookmarks': [],
    'highlights': [],
}
for f in ['unread', 'archive']:
    bm = api.bookmarks_raw(folder=f, limit=LIMIT)
    del bm['user']
    for k, l in bm.items():
        res[k].extend(l)


json.dump(res, sys.stdout, ensure_ascii=False, indent=1, sort_keys=True)
