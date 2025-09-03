

Export your personal Instapaper data: bookmarked articles and
highlights.

<!-- TODO WTF? without a comment it moves execution output under heading otherwise? -->

# Installing

## Basic install

Install with pip:

`pip3 install 'instapexport[export,dal,optional] @ git+https://github.com/karlicoss/instapexport'`

The
[‘extras’](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras)
in square brackets provide additional dependencies, feel free to omit
some of them if you don’t need it:

- `export` is needed for [export functionality](#exporting)
- `dal` is needed to [access exported data](#using-the-data)
- `optional` is for nicer logging facilities and faster json processing

See [`optional-dependencies`](pyproject.toml) section in
`pyproject.toml` for more details.

## Advanced install options

- editable install

  You’ll need to clone the repository with submodules.

  - use `git clone --recursive`, or
    `git pull && git submodules update --init`
  - after that, you can use `pip3 install --editable`

- run via `uvx`

  This allows you to run instapexport without installing if you just
  want to quickly try it out. E.g.:

  `uvx --from 'instapexport[export,dal,optional] @ git+https://github.com/karlicoss/instapexport' python3 -m instapexport.export ...`

  It’s a little awkward though since you can’t install tools without
  ‘executable scripts’ with uv at the moment – please let me know

# Exporting

## Running export

Usage:

**Recommended**: create `secrets.py` keeping your API parameters, e.g.:

    oauth_id = "OAUTH_ID"
    oauth_secret = "OAUTH_SECRET"
    oauth_token = "OAUTH_TOKEN"
    oauth_token_secret = "OAUTH_TOKEN_SECRET"

After that, use:

    python3 -m instapexport.export --secrets /path/to/secrets.py

That way you type less and have control over where you keep your
plaintext secrets.

**Alternatively**, you can pass parameters directly, e.g.

    python3 -m instapexport.export --oauth_id <oauth_id> --oauth_secret <oauth_secret> --oauth_token <oauth_token> --oauth_token_secret <oauth_token_secret>

However, this is verbose and prone to leaking your keys/tokens/passwords
in shell history.

You can also import `instapexport.export` as a module and call
`get_json` function directly to get raw JSON.

I **highly** recommend checking exported files at least once just to
make sure they contain everything you expect from your export If they
don’t, please feel free to ask or raise an issue!

## Setting up API parameters

1.  To use the API, you need to [request `oauth_id` and
    `oauth_secret`](https://www.instapaper.com/main/request_oauth_consumer_token)
    first.

2.  Once you retrieved them, use them to get `oauth_token` and
    `oauth_token_secret`: `python3 -m instapexport.export --login`

    You’ll only need this step once, after that you should be able to
    use the API without re-authenticating.

3.  Use the `oauth_token` and `oauth_token_secret` to set up
    `secrets.py` as mentioned above.

# Using the data

You can use `instapexport.dal` (stands for “Data Access/Abstraction
Layer”) to access your exported data, even offline. I elaborate on
motivation behind it [here](https://beepb00p.xyz/exports.html#dal).

- main usecase is to be imported as python module to allow for
  **programmatic access** to your data.

  You can find some inspiration in
  [`my.`](https://beepb00p.xyz/mypkg.html) package that I’m using as an
  API to all my personal data.

- to test it against your export, simply run:
  `python3 -m instapexport.dal --source /path/to/export`

- you can also try it interactively in an Ipython shell:
  `python3 -m instapexport.dal --source /path/to/export --interactive`

## Example output

    Parsed 203 pages
    10 most highlighed pages:
      41 https://www.wired.com/1995/06/xanadu/ "The Curse of Xanadu"
      14 https://jborichevskiy.com/posts/digital-tools/ "Digital Tools I Wish Existed"
      12 http://slatestarcodex.com/2017/08/07/contra-grant-on-exaggerated-differences/ "Contra Grant On Exaggerated Differences"
      12 https://slatestarcodex.com/2019/06/04/book-review-the-secret-of-our-success/ "Book Review: The Secret Of Our Success"
      10 https://intelligence.org/2013/12/13/aaronson/ "Scott Aaronson on Philosophical Progress - Machine Intelligence Research Institute"
      10 http://www.thebioneer.com/nervous-system-training-muscle-fiber-recruitment-rate-coding-explained/ "Nervous System Training - Muscle Fiber Recruitment and Rate Coding Explained - The Bioneer"
       9 https://srconstantin.wordpress.com/2016/06/06/nootropics/ "Nootropics"
       9 https://blog.dropbox.com/topics/work-culture/-the-mind-at-work--guido-van-rossum-on-how-python-makes-thinking "The Mind at Work: Guido van Rossum on how Python makes thinking in code easier"
       9 https://slatestarcodex.com/2019/12/11/acc-is-eating-meat-a-net-harm/ "[ACC] Is Eating Meat A Net Harm?"
       9 https://beepb00p.xyz/my-data.html "What data on myself I collect and why? | Mildly entertainingᵝ"

# Contributing

If you want to contribute/develop this project, check out [github
actions](.github/workflows/main.yml) to see how the project is
run/tested.

Generally you should be able to run various checks via `tox`, e.g.

`uv tool run --with tox-uv tox -e <check>`

See the top of [tox.ini](tox.ini) for available checks.

## Updating README

This README is generated from a ‘literate’ Quarto
[README.qmd](README.qmd) via the following command:

`uv run --with=quarto-cli --with=jupyter quarto render README.qmd`

If you want to correct something, feel free to simply update `README.md`
though, I can reconcile the changes next time I regenerate it.
