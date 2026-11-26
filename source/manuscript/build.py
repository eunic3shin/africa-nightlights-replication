"""Fill the LaTeX template with computed results and build the thesis."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def fill(template, scalars):
    def replacement(match):
        key, style = match.groups()
        number = scalars[key]
        fmt, *options = style.split("-")
        if fmt == "sci":
            lead, exponent = f"{number:.2e}".split("e")
            result = rf"{lead}\times 10^{{{int(exponent)}}}"
        elif fmt == "double2":
            result = f"{float(f'{number:.3f}'):.2f}"
        else:
            result = format(number, fmt)
        if "se" in options:
            result = f"({result})"
        if "stars" in options or "rstars" in options:
            p = scalars[key.removesuffix(".estimate") + ".p"]
            cutoffs = (.001, .01, .05) if "rstars" in options else (.01, .05, .1)
            stars = next(("*" * (3 - i) for i, cutoff in enumerate(cutoffs) if p < cutoff), "")
            if stars:
                result = "{" + result + "}" + f"^{{{stars}}}"
        return result

    return re.sub(r"\\Result\{([^{}]+)\}\{([^{}]+)\}", replacement, template)


def main():
    template, scalars, output = map(Path, sys.argv[1:])
    latexmk = shutil.which("latexmk")
    if not latexmk:
        raise SystemExit("Install a full TeX distribution with latexmk to build the manuscript.")
    work = output.parent / "latex"
    work.mkdir(parents=True, exist_ok=True)
    source = work / f"{output.stem}.tex"
    source.write_text(fill(template.read_text(), json.loads(scalars.read_text())))
    subprocess.run([
        latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error",
        f"-outdir={work}", str(source),
    ], check=True)
    shutil.copyfile(work / output.name, output)


if __name__ == "__main__":
    main()
