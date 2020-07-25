# -*- coding: utf-8 -*-
"""Cache filepath to file."""

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, Iterator, TextIO, Tuple

_xdg_cache_home = os.getenv("XDG_CACHE_HOME")

CACHE_DIR = (
    Path(_xdg_cache_home) / "cachef" if _xdg_cache_home else Path.home() / "cachef"
)

CACHE_FILE = CACHE_DIR / "cachef.txt"


class CacheFileNotFound(Exception):
    """Raise if CACHE_FILE is not found."""


def _cache_contents(cache_file: Path) -> Tuple[str, ...]:
    with cache_file.open("r", newline=None) as ifile:
        contents = tuple(l.strip() for l in ifile)

    return contents


def _already_cached(realpath: Path, cache_file: Path) -> bool:
    cache_contents = _cache_contents(cache_file)

    return str(realpath) in cache_contents


def _not_cached_realpaths(filepaths: Iterable[str], cache_file: Path) -> Iterator[Path]:
    """Yield realpaths that are not cached yet."""
    cache_contents = _cache_contents(cache_file)

    for filepath in filepaths:
        realpath = Path(filepath).resolve()

        if str(realpath) in cache_contents:
            continue

        yield realpath


def clean_cache_file(cache_file: Path):
    """Remove non exist path from CACHE_FILE."""
    if not cache_file.exists():
        raise CacheFileNotFound("cache file is not found.")

    def __existing_paths():
        with cache_file.open("r") as ifile:
            for line in ifile:
                if not Path(line.strip()).exists():
                    continue

                yield line.strip()

    exising_paths = list(__existing_paths())

    with cache_file.open("w") as ofile:
        ofile.write("\n".join(exising_paths))
        ofile.write("\n")


def _setup_cache_file(cache_file: Path):
    if not cache_file.parent.exists():
        cache_file.parent.mkdir(parents=True)

    # Create empty file
    if not cache_file.exists():
        with cache_file.open("w") as ofile:
            ofile.write("")


def _cache_realpath(realpath: Path, cache_file_io: TextIO):
    """Cache a realpath to cache_file."""
    cache_file_io.write(str(realpath))
    cache_file_io.write("\n")


def cache_filepath(filepath: str, cache_file: Path):
    """Cache a realpath of filepath to cache_file."""
    real = Path(filepath).resolve()

    if _already_cached(real, cache_file):
        # Do nothing
        return

    with cache_file.open("a") as ofile:
        _cache_realpath(real, ofile)


def cache_filepaths(filepaths: Iterable[str], cache_file: Path):
    """Cache multiple realpaths of filepaths to cache_file."""
    _setup_cache_file(cache_file)

    for realpath in _not_cached_realpaths(filepaths, cache_file):
        with cache_file.open("a") as ofile:
            _cache_realpath(realpath, ofile)


def _parse_args() -> argparse.Namespace:
    """Parse commandline argument."""
    parser = argparse.ArgumentParser(description="Cache filepath.")

    # Positional argument
    parser.add_argument(
        "filepath", nargs="*", default=None, help="filepath to be cached."
    )

    # Optional argument
    parser.add_argument(
        "--cache-file",
        dest="cache_file",
        action="store_true",
        help="Print cache filepath.",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean cache file.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    if args.cache_file:
        print(CACHE_FILE)
        sys.exit(0)

    if args.clean:
        try:
            clean_cache_file(CACHE_FILE)
            sys.exit(0)
        except CacheFileNotFound as e:
            print(e)
            sys.exit(1)

    if args.filepath:
        cache_filepaths(args.filepath, CACHE_FILE)
