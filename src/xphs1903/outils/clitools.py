from argparse import ArgumentParser, Namespace

epilog = """(c) Copyright 2026 Émile Jetzer. All Rights Reserved."""


def argparse() -> Namespace:
    ap = ArgumentParser(epilog=epilog, suggest_on_error=True)
    ap.add_argument("-d", "--debug", action="store_true")
    return ap.parse_args()
