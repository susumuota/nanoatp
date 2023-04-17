# nanoatp

A nano implementation of the AT Protocol (Authenticated Transfer Protocol) for Python.

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
embed = {"$type": "app.bsky.embed.images#main", "images": [image]}
record = {"text": rt.text, "facets": rt.facets, "embed": embed}

# post it
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
res1 = agent.createRecord(
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

Susumu Ota
