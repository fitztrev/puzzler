FROM python:3.13.5-bookworm

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /python-zulip-api/zulip_bots/zulip_bots/bots/puzzler/
WORKDIR /python-zulip-api/zulip_bots/zulip_bots/bots/puzzler

ENV ZULIPRC=/zuliprc

ENTRYPOINT \
    COMMIT_HASH=$(git rev-parse --short HEAD) \
    LAST_COMMIT=$(git log -1 --pretty="%ad %s") \
    zulip-run-bot puzzler.py --config-file $ZULIPRC
