from setuptools import setup, find_namespace_packages # type: ignore


def main() -> None:
    pkgs = find_namespace_packages('src')
    pkg = min(pkgs)
    return setup(
        name=pkg,
        zip_safe=False,
        packages=pkgs,
        package_dir={'': 'src'},
        package_data={pkg: ['py.typed']},

        install_requires=[
            # my version has some changes not in the upstream yet..
            'instapaper @ git+https://github.com/karlicoss/instapaper.git',
        ],
        extras_require={
            'testing': ['pytest'],
            'linting': ['pytest', 'mypy', 'lxml'],  # lxml for mypy coverage report
            'optional': ['orjson', 'colorlog', 'enlighten'],
        },
    )


if __name__ == '__main__':
    main()
