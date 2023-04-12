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

agent = new BskyAgent("https://bsky.social")
```

## Usage

### Session management

Log into a server using these APIs. You'll need an active session for most methods.

```python
from nanoatp import BskyAgent

agent = new BskyAgent("https://bsky.social")

agent.login('alice@mail.com', 'hunter2')

# if you don't specify credentials, ATP_IDENTIFIER and ATP_PASSWORD environment variables will be used
# agent.login()
```

### API calls

The agent includes methods for many common operations, including:

```python
# Feeds and content
agent.post(record)
agent.uploadBlob(data, contentType)
agent.uploadImage(path, alt, contentType)

# Session management
agent.login(identifier, password)
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
