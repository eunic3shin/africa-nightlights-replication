"""Extract the two panel CSVs into SCons-managed output paths."""

import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile


def main():
    archive, *targets = map(Path, sys.argv[1:])
    targets[0].parent.mkdir(parents=True, exist_ok=True)
    try:
        with ZipFile(archive) as source, TemporaryDirectory(dir=targets[0].parent) as temp:
            staging = Path(temp)
            for target in targets:
                with source.open(target.name) as member, (staging / target.name).open("wb") as out:
                    shutil.copyfileobj(member, out)
            for target in targets:
                (staging / target.name).replace(target)
    except BadZipFile as exc:
        with archive.open("rb") as stream:
            if stream.read(43).startswith(b"version https://git-lfs.github.com/spec/v1"):
                raise SystemExit("Panel archive is a Git LFS pointer. Run git lfs pull and retry.") from exc
        raise


if __name__ == "__main__":
    main()
