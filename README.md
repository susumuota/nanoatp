# nanoatp

[![PyPI](https://img.shields.io/pypi/v/nanoatp?color=blue)](https://pypi.org/project/nanoatp/)
[![GitHub License](https://img.shields.io/github/license/susumuota/nanoatp)](https://github.com/susumuota/nanoatp/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/susumuota/nanoatp)](https://github.com/susumuota/nanoatp/commits)
&emsp;
EN |
[JA](https://github-com.translate.goog/susumuota/nanoatp/blob/main/README.md?_x_tr_sl=en&_x_tr_tl=ja&_x_tr_hl=ja&_x_tr_pto=wapp) |
[ES](https://github-com.translate.goog/susumuota/nanoatp/blob/main/README.md?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=wapp) |
[ZH](https://github-com.translate.goog/susumuota/nanoatp/blob/main/README.md?_x_tr_sl=en&_x_tr_tl=zh-CN&_x_tr_hl=zh-CN&_x_tr_pto=wapp)

A nano implementation of the AT Protocol for Python.

## Demo

- A bot built with nanoatp that summarizes the top 30 most popular arXiv papers on Reddit and Hacker News in the last 30 days and posts them to Bluesky.
  - [@paper.bsky.social](https://staging.bsky.app/profile/paper.bsky.social)
    - It needs to have an account on Bluesky to see the posts. But there is a similar bot on Twitter [@susumuota](https://twitter.com/susumuota).
  - [Source code](https://github.com/susumuota/arxiv-reddit-summary)

## Getting started

- First, install the package.

```bash
pip install nanoatp
```

- Set your credentials as environment variables. Or you can pass them to `BskyAgent.login()`.

```bash
export ATP_IDENTIFIER="foo.bsky.social"
export ATP_PASSWORD="password"
```

- Then in your application,

```python
from nanoatp import BskyAgent, RichText

agent = BskyAgent("https://bsky.social")
agent.login()

# post a simple text
record = {"text": "Hello World!"}
response = agent.post(record)
print(response)

# create a RichText
rt = RichText("Hello @ota.bsky.social, check out this link: https://example.com")
rt.detectFacets(agent)
print(rt.facets)

# upload an image
image = agent.uploadImage("example.png")

# post a RichText with an image
embed = {"$type": "app.bsky.embed.images#main", "images": [image]}
record = {"text": rt.text, "facets": rt.facets, "embed": embed}
response = agent.post(record)
print(response)
```

See [examples](https://github.com/susumuota/nanoatp/tree/main/examples) for more.

## Usage

### Session management

Log into a server using these APIs. You'll need an active session for most methods.

```python
from nanoatp import BskyAgent

agent = BskyAgent("https://bsky.social")

# if you don't specify credentials,
# ATP_IDENTIFIER and ATP_PASSWORD environment variables will be used
agent.login("alice@mail.com", "hunter2")
```

### API calls

The agent includes methods for many common operations, including:

```python
# Feeds and content
agent.getPost(repo, rkey, cid)
agent.post(record)
agent.deletePost(postUri)
agent.uploadBlob(data, encoding)
agent.uploadImage(path, alt, encoding)  # wrapper for uploadBlob

# Identity
agent.resolveHandle(handle)

# Session management
agent.login(identifier, password)
```

### Rich text

Some records (ie posts) use the `app.bsky.richtext` lexicon. At the moment richtext is only used for links and mentions, but it will be extended over time to include bold, italic, and so on.

ℹ️ Currently the implementation is very naive. I have not tested it with UTF-16 text.

```python
from nanoatp import BskyAgent, RichText

agent = BskyAgent()
agent.login()

rt = RichText("Hello @ota.bsky.social, check out this link: https://example.com")
rt.detectFacets(agent)
record = {"text": rt.text, "facets": rt.facets}
agent.post(record)
```

## Advanced

### Advanced API calls

The methods above are convenience wrappers. It covers most but not all available methods.

The AT Protocol identifies methods and records with reverse-DNS names. You can use them on the agent as well:

```python
res1 = agent._repo_createRecord(
    agent.session["did"],  # repo
    "app.bsky.feed.post",  # collection
    {
        "$type": "app.bsky.feed.post",
        "text": "Hello, world!",
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    }
)
```

## Development

```bash
export ATP_IDENTIFIER="foo.bsky.social"
export ATP_PASSWORD="password"
poetry install
poetry run pytest -s     # run pytest once
poetry run -- ptw -- -s  # watch for changes and run pytest
```

## TODO:

- [ ] split BskyAgent and AtpAgent code
- [ ] implement a proper RichText parser with UTF-16 (currently it's very naive)
- [ ] type definitions
- [ ] structured tests
- [ ] more APIs

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

S. Ota
