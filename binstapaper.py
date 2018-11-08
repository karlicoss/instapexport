#!/usr/bin/env python3
from instapaper import Instapaper

from instapaper_secrets import *

LIMIT = 500

api = Instapaper(OAUTH_ID, OAUTH_SECRET)
api.login(USERNAME, PASSWORD)
# TODO 
for f in ['unread', 'archive']:
    bm = api.bookmarks_raw(folder='unread', limit=LIMIT)
    print(bm)

