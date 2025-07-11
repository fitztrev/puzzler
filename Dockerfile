FROM python:3.13.5-bookworm

COPY . /puzzler/
WORKDIR /puzzler

RUN pip install -r requirements.txt

ENV ZULIPRC=/zuliprc

ENTRYPOINT zulip-run-bot puzzler.py --config-file $ZULIPRC
