# Puzzler Bot

## Local Development

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Docker

Test docker build locally:

```bash
docker build -t zulip-puzzler .
docker run -it --rm -v ~/Downloads/zuliprc:/zuliprc zulip-puzzler
```

Push to Docker Hub:

```bash
docker build -t fitztrev/zulip-puzzler .
docker push fitztrev/zulip-puzzler
```
