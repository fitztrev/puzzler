import os


def zuliprc():
    return os.getenv("ZULIPRC")


def version():
    return os.getenv("COMMIT_HASH", "unknown")


def last_commit():
    return os.getenv("LAST_COMMIT", "unknown")
