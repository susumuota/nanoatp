# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest
import requests

import nanoatp


@pytest.fixture
def png(tmpdir) -> str:  # type: ignore
    response = requests.get("https://staging.bsky.app/static/favicon-16x16.png")
    tmpfile = tmpdir.join("favicon-16x16.png")
    with tmpfile.open("wb") as f:
        f.write(response.content)
    yield str(tmpfile)
    tmpfile.remove()


def test_version():
    assert nanoatp.__version__ == "0.1.0"


def test_bskyagent(png):
    agent = nanoatp.BskyAgent()
    print(agent)
    assert agent is not None
    assert agent.service == "https://bsky.social"
    assert agent.requests is not None
    assert agent.session is None

    session = agent.login()  # Use environment variables ATP_IDENTIFIER and ATP_PASSWORD
    print(session)
    assert session is not None
    assert session.get("did") is not None
    assert session.get("handle") is not None
    assert session.get("email") is not None
    assert session.get("accessJwt") is not None
    assert session.get("refreshJwt") is not None

    record = {"text": "Hello0"}
    response = agent.post(record)
    print(response)
    assert response is not None
    assert response.get("uri") is not None
    assert response.get("cid") is not None
    root = response
    parent = root

    record = {"text": "Hello1", "reply": {"root": root, "parent": parent}}
    response = agent.post(record)
    print(response)
    assert response is not None
    assert response.get("uri") is not None
    assert response.get("cid") is not None
    parent = response

    images = [agent.uploadImage(png, f"this is alt {i}") for i in range(4)]
    embed = {"$type": "app.bsky.embed.images#main", "images": images}
    record = {"text": "Hello2", "reply": {"root": root, "parent": parent}, "embed": embed}
    response = agent.post(record)
    print(response)
    assert response is not None
    assert response.get("uri") is not None
    assert response.get("cid") is not None
