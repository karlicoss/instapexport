#!/usr/bin/env python3
import argparse
import json
from typing import List

from .exporthelpers.export_helper import Json

# NOTE: uses custom version (has some changes that are not in upstream yet)
# https://github.com/karlicoss/instapaper
import instapaper # type: ignore[import]
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


def login():
    print("NOTE: You'll need your username/password once in order to get oauth_token")
    oauth_id     = input('Your ouath_id: ')
    oauth_secret = input('Your ouath_secret: ')
    username     = input('Your username: ')
    password     = input('Your password: ')

    api = instapaper.Instapaper(oauth_id, oauth_secret)
    odata = api.login(username, password)
    print("Now paste this into your secrets file")
    print(odata)


def main():
    parser = make_parser()
    args = parser.parse_args()

    params = args.params
    dumper = args.dumper

    if args.login:
        login()
        return

    j = get_json(**params)
    js = json.dumps(j, indent=1, ensure_ascii=False, sort_keys=True)
    dumper(js)


def make_parser():
    from .exporthelpers.export_helper import setup_parser, Parser
    parser = Parser("""
Export your personal Instapaper data: bookmarked articles and highlights.
""")
    setup_parser(
        parser=parser,
        params=[
            'oauth_id',
            'oauth_secret',
            'oauth_token',
            'oauth_token_secret',
        ],
        extra_usage='''
You can also import ~instapexport.export~ as a module and call ~get_json~ function directly to get raw JSON.
''')
    parser.add_argument('--login', action='store_true', help='''
    Note: OAUTH_ID/OAUTH_SECRET have to be requrested by email
    https://www.instapaper.com/main/request_oauth_consumer_token
    ''')
    return parser


if __name__ == '__main__':
    main()
