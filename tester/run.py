"""
Main entrypoint for tester container
"""

import os
import sys
import time

NOSEPATH = "/usr/local/bin/nosetests"


def unit(*suites):
    """
    Run all unit tests of given suites
    """
    if not suites:
        suites = ["api", "slackbot"]
    os.execv(NOSEPATH, [NOSEPATH] + list(suites))


def e2e(*suites):
    """
    Run all e2e tests of given suites
    """
    if not suites:
        suites = ["tester"]
    os.execv(NOSEPATH, [NOSEPATH] + list(suites))


def test_all():
    """
    Run all tests
    """
    os.execv(NOSEPATH, [NOSEPATH, "api", "slackbot", "tester"])


def main():
    """
    Module main entry proc
    """
    args = sys.argv[1:]
    if not args:
        print("No test suite given; waiting indefinitely")
        while True:
            time.sleep(10000)
    else:
        classes = {"unit": unit, "e2e": e2e, 'all': test_all}
        if args[0] in classes:
            classes[args[0]](*args[1:])


if __name__ == "__main__":
    main()
