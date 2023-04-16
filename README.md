# nanoatp

A nano implementation of the AT Protocol (Authenticated Transfer Protocol).

## Getting started

First install the package:

```bash
pip install nanoatp
```

Then in your application:

```python
from nanoatp import BskyAgent

agent = BskyAgent("https://bsky.social")
```

## Usage

### Session management

Log into a server using these APIs. You'll need an active session for most methods.

```python
from nanoatp import BskyAgent

agent = BskyAgent("https://bsky.social")

agent.login('alice@mail.com', 'hunter2')

# if you don't specify credentials, ATP_IDENTIFIER and ATP_PASSWORD environment variables will be used
# agent.login()
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

For example, to post a record, reply to it, and upload an image:

```python
from nanoatp import BskyAgent

agent = BskyAgent("https://bsky.social")
session = agent.login()

record = {"text": "Hello, world! 0"}
r = agent.post(record)
root = r
parent = r

record = {"text": "Hello, world! 1", "reply": {"root": root, "parent": parent}}
r = agent.post(record)
parent = r

image = agent.uploadImage("favicon-16x16.png", "image/png")
embed = {"$type": "app.bsky.embed.images#main", "images": [image]}
record = {
    "text": "Hello, world! 2",
    "reply": {"root": root, "parent": parent},
    "embed": embed
}
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
        "$type": "app.bsky.feed.post",  # record
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
poetry run -- ptw -- -s  # run pytest and watch for changes
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

Susumu Ota
