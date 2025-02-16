# SPDX-FileCopyrightText: 2023-2025 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from time import sleep

import pytest
import requests

import nanoatp


@pytest.fixture
def png(tmpdir) -> str:  # type: ignore
    response = requests.get("https://bsky.app/static/favicon-16x16.png")
    tmpfile = tmpdir.join("favicon-16x16.png")
    with tmpfile.open("wb") as f:
        f.write(response.content)
    yield str(tmpfile)
    tmpfile.remove()


def test_version():
    assert nanoatp.__version__ == "0.5.0"
    print("test_version passed")


def test_richtext():
    agent = nanoatp.BskyAgent()
    agent.login()
    sleep(1)
    text = "Hello @nanoatp.bsky.social, check out this link: https://example.com"
    rt = nanoatp.RichText(text)
    rt.detectFacets(agent)
    assert len(rt.facets) == 2
    for facet in rt.facets:
        start = facet["index"]["byteStart"]
        end = facet["index"]["byteEnd"]
        assert start < end
        assert start >= 0
        assert end <= len(rt.text)
        if facet["features"][0]["$type"] == "app.bsky.richtext.facet#link":
            assert text[start:end] == facet["features"][0]["uri"]
        elif facet["features"][0]["$type"] == "app.bsky.richtext.facet#mention":
            assert facet["features"][0]["did"]
    print("test_richtext passed")


def test_login():
    agent = nanoatp.BskyAgent()
    assert agent is not None
    assert agent.service == "https://bsky.social"
    assert agent.requests is not None
    assert agent.session == {}
    assert agent.headers == {}
    session = agent.login()
    sleep(1)
    assert agent.session != {}
    assert agent.headers != {}
    assert session != {}
    assert session.get("did") is not None
    assert session.get("handle") is not None
    assert session.get("email") is not None
    assert session.get("accessJwt") is not None
    assert session.get("refreshJwt") is not None
    handle = agent.resolveHandle(session["handle"])
    sleep(1)
    assert handle is not None
    assert handle.get("did") is not None
    assert handle.get("did") == session.get("did")
    print("test_login passed")


def test_post():
    agent = nanoatp.BskyAgent()
    agent.login()
    sleep(1)
    posted = agent.post({"text": "Hello"})
    sleep(1)
    assert posted is not None
    assert posted.get("uri") is not None
    assert posted.get("cid") is not None
    deleted = agent.deletePost(posted.get("uri"))
    sleep(1)
    assert deleted is not None
    assert deleted.status_code == 200
    print("test_post passed")


def test_get_post():
    agent = nanoatp.BskyAgent()
    agent.login()
    sleep(1)
    posted = agent.post({"text": "Hello"})
    sleep(1)
    assert posted is not None
    assert posted.get("uri") is not None
    assert posted.get("cid") is not None
    repo, _, rkey = nanoatp.parseAtUri(posted.get("uri"))
    got = agent.getPost(repo, rkey, posted.get("cid"))
    sleep(1)
    assert got is not None
    assert got.get("uri") == posted.get("uri")
    assert got.get("cid") == posted.get("cid")
    deleted = agent.deletePost(posted.get("uri"))
    sleep(1)
    assert deleted is not None
    assert deleted.status_code == 200
    print("test_get_post passed")


def test_upload_image(png):
    agent = nanoatp.BskyAgent()
    agent.login()
    sleep(1)
    image = agent.uploadImage(png, "this is alt")
    sleep(1)
    print(f"image: {image}")
    assert image is not None
    assert image.get("alt") is not None
    assert image.get("image") is not None
    embed = {"$type": "app.bsky.embed.images", "images": [image]}
    record = {"text": "upload image test", "embed": embed}
    posted = agent.post(record)
    sleep(1)
    print(f"posted: {posted}")
    assert posted is not None
    assert posted.get("uri") is not None
    assert posted.get("cid") is not None
    deleted = agent.deletePost(posted.get("uri"))
    sleep(1)
    assert deleted is not None
    assert deleted.status_code == 200
    print("test_upload_image passed")


def test_upload_external():
    agent = nanoatp.BskyAgent()
    agent.login()
    sleep(1)
    external = agent.uploadExternal("https://huggingface.co/")
    sleep(1)
    assert external is not None
    assert external.get("$type") is not None
    assert external.get("uri") is not None
    assert external.get("title") is not None
    assert external.get("description") is not None
    assert external.get("thumb") is not None
    embed = {"$type": "app.bsky.embed.external", "external": external}
    record = {"text": "external link test", "embed": embed}
    posted = agent.post(record)
    sleep(1)
    assert posted is not None
    assert posted.get("uri") is not None
    assert posted.get("cid") is not None
    deleted = agent.deletePost(posted.get("uri"))
    sleep(1)
    assert deleted is not None
    assert deleted.status_code == 200
    print("test_upload_external passed")
