import argparse
from pathlib import Path
import sys
from typing import Sequence, Dict, Any


Json = Dict[str, Any]


def setup_parser(parser: argparse.ArgumentParser, params: Sequence[str]):
    PARAMS_KEY = 'params'

    # eh, doesn't seem to be possible to achieve this via mutually exclusive groups in argparse...
    # and still, cryptic error message if you forget to specify either :(
    set_from_file = False
    set_from_cmdl = False

    class SetParamsFromFile(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if set_from_cmdl:
                raise RuntimeError("Please use either --secrets or individual --param arguments")
            nonlocal set_from_file; set_from_file = True

            secrets_file = values
            obj = {} # type: ignore

            # we control the file with secrets so exec is fine
            exec(secrets_file.read_text(), {}, obj)

            def get(k):
                if k not in obj:
                    raise RuntimeError("Couldn't extract '{}' param from file {} (got {})".format(k, secrets_file, obj))
                return obj[k]

            pdict = {k: get(k) for k in params}
            setattr(namespace, PARAMS_KEY, pdict)

    class SetParam(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if set_from_file:
                raise RuntimeError("Please use either --secrets or individual --param arguments")
            nonlocal set_from_cmdl; set_from_cmdl = True

            pdict = getattr(namespace, PARAMS_KEY, {})
            pdict[self.dest] = values
            setattr(namespace, PARAMS_KEY, pdict)

    class SetOutput(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            output_path = values

            def dump_to_stdout(data):
                sys.stdout.write(data)

            def dump_to_file(data):
                with output_path.open('w') as fo:
                    fo.write(data)
                print('saved data to {output_path}'.format(output_path=output_path), file=sys.stderr)

            if output_path is None:
                dumper = dump_to_stdout
            else:
                dumper = dump_to_file

            setattr(namespace, 'dumper', dumper)

    parser.add_argument(
        '--secrets',
        type=Path,
        action=SetParamsFromFile,
        required=False,
        help='.py file containing {} variables'.format(", ".join(params)),
    )
    gr = parser.add_argument_group('API parameters')
    for param in params:
        gr.add_argument('--' + param, type=str, action=SetParam)

    parser.add_argument(
        'path',
        type=Path,
        action=SetOutput,
        nargs='?',
        help='Optional path to backup, otherwise will be printed to stdout',
    )
