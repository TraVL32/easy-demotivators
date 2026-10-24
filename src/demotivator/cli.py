from __future__ import annotations

import argparse

from .core import DemotivatorStyle, create_demotivator


def main() -> None:
    p = argparse.ArgumentParser(prog="demotivator", description="Make a demotivator poster")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("-t", "--title", default="")
    p.add_argument("-s", "--subtitle", default="")
    p.add_argument("--font", default=None, help="path to .ttf for title and subtitle")
    p.add_argument("--upper", action="store_true")
    a = p.parse_args()
    style = DemotivatorStyle(title_font=a.font, subtitle_font=a.font, upper=a.upper)
    create_demotivator(a.input, a.title, a.subtitle, style).save(a.output)


if __name__ == "__main__":
    main()
