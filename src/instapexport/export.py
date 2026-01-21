from __future__ import annotations

import json
import logging
import sys

# NOTE: uses custom version (has some changes that are not in upstream yet)
# https://github.com/karlicoss/instapaper
import instapaper  # type: ignore[import-untyped]

from .exporthelpers.export_helper import Json, Parser, setup_parser
from .exporthelpers.logging_helper import make_logger

instapaper._API_VERSION_ = "api/1.1"  # ty: ignore[invalid-assignment]
# see https://github.com/rsgalloway/instapaper/issues/11
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

# for debugging HTTP calls of instapaper lib
# import httplib2
# httplib2.debuglevel = 4


logger = make_logger(__name__)


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

    # very rarely, we get one off 504 Gateway Time-out, usually retrying immediately after works
    @retry(
        # retry=retry_if_exception_message(match='.*504 Gateway Time-out.*')  # hmm this isn't working because it can't match multiline?
        retry=retry_if_exception(predicate=lambda e: '504 Gateway Time-out' in str(e)),
        wait=wait_exponential(max=10),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    def query_api() -> Json:
        user_folders = api.folders()
        folders: list[str] = [
            ## default, as per api docs
            'unread',
            'archive',
            'starred',
            ##
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

    return query_api()


def login(*, oauth_id: str | None = None, oauth_secret: str | None = None, **kwargs) -> None:  # noqa: ARG001
    print("NOTE: You'll need to enter you username/password (once) in order to get oauth_token", file=sys.stderr)
    # if some api params were already passed, no need to ask for them again
    if oauth_id is None:
        oauth_id = input('Your oauth_id: ')
    if oauth_secret is None:
        oauth_secret = input('Your oauth_secret: ')
    username = input('Your username: ')
    password = input('Your password: ')

    api = instapaper.Instapaper(oauth_id, oauth_secret)
    odata = api.login(username, password)
    print("Now paste this into your secrets file", file=sys.stderr)
    print(odata)


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()

    params = args.params
    dumper = args.dumper

    if args.login:
        login(**params)
        return

    j = get_json(**params)
    js = json.dumps(j, indent=1, ensure_ascii=False, sort_keys=True)
    dumper(js)


def make_parser():
    parser = Parser(
        """
Export your personal Instapaper data: bookmarked articles and highlights.
""",
    )
    setup_parser(
        parser=parser,
        params=[
            'oauth_id',
            'oauth_secret',
            'oauth_token',
            'oauth_token_secret',
        ],
        extra_usage='''
You can also import `instapexport.export` as a module and call `get_json` function directly to get raw JSON.
'''.lstrip(),
    )
    parser.add_argument(
        '--login',
        action='store_true',
        help='''
Pass to FIXME.
Note: OAUTH_ID/OAUTH_SECRET have to be requrested by email
https://www.instapaper.com/main/request_oauth_consumer_token
    '''.strip(),
    )
    return parser


if __name__ == '__main__':
    main()
