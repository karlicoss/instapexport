#!/usr/bin/env python3
import argparse
import json
from typing import List

from export_helper import Json

import modules.instapaper.instapaper as instapaper # type: ignore[import]
instapaper._API_VERSION_ = "api/1.1"
# see https://github.com/rsgalloway/instapaper/issues/11


def get_json(
        oauth_id: str,
        oauth_secret: str,
        oauth_token: str,
        oauth_token_secret: str,
) -> Json:
    LIMIT = 500
    # default limit is something stupid
    # TODO need merging logic in DAL

    api = instapaper.Instapaper(oauth_id, oauth_secret)
    api.login_with_token(oauth_token, oauth_token_secret)

    user_folders = api.folders()
    folders: List[str] = [
        'unread', 'archive', 'starred', # default, as per api docs
        *(str(f['folder_id']) for f in user_folders),
    ]
    bookmarks = {}
    for f in folders:
        fbookmarks = api.bookmarks_raw(folder=f, limit=LIMIT, have=None)
        bookmarks[f] = fbookmarks
    return {
        'folders': user_folders,
        'bookmarks': bookmarks,
    }


def login(oauth_id: str, oauth_secret: str):
    """
    Note: OAUTH_ID/OAUTH_SECRET have to be requrested by email
    https://www.instapaper.com/main/request_oauth_consumer_token
    """
    USERNAME = None
    PASSWORD = None

    api = instapaper.Instapaper(oauth_id, oauth_secret)
    odata = api.login(USERNAME, PASSWORD)
    print("paste this into your secrets file")
    print(repr(odata))


def main():
    from export_helper import setup_parser
    parser = argparse.ArgumentParser("Tool to export your personal Instapaper data")
    setup_parser(parser=parser, params=[
        'oauth_id',
        'oauth_secret',
        'oauth_token',
        'oauth_token_secret',
    ])
    parser.add_argument('--login', action='store_true', help='''
    TODO
    ''')
    args = parser.parse_args()

    params = args.params
    dumper = args.dumper

    if args.login:
        login(**params)
        return

    j = get_json(**params)
    js = json.dumps(j, indent=1, ensure_ascii=False, sort_keys=True)
    dumper(js)


if __name__ == '__main__':
    main()
