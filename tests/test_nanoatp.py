# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from time import sleep

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
    assert nanoatp.__version__ == "0.3.1"


def test_richtext():
    agent = nanoatp.BskyAgent()
    agent.login()  # Use environment variables ATP_IDENTIFIER and ATP_PASSWORD
    text = "Hello @ota.bsky.social, check out this link: https://example.com"
    rt = nanoatp.RichText(text)
    rt.detectFacets(agent)
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
    print(rt.facets)


def test_bskyagent(png):
    agent = nanoatp.BskyAgent()
    print(agent)
    assert agent is not None
    assert agent.service == "https://bsky.social"
    assert agent.requests is not None
    assert agent.session == {}

    session = agent.login()  # Use environment variables ATP_IDENTIFIER and ATP_PASSWORD
    print(session)
    assert session != {}
    assert session.get("did") is not None
    assert session.get("handle") is not None
    assert session.get("email") is not None
    assert session.get("accessJwt") is not None
    assert session.get("refreshJwt") is not None
    sleep(1)

    response = agent.resolveHandle(session["handle"])
    assert response is not None
    assert response.get("did") is not None
    assert response.get("did") == session.get("did")
    print(response)
    sleep(1)

    cursor = ""
    for i in range(1):
        response = agent.listRecords(session["did"], "app.bsky.feed.post", limit=100, cursor=cursor)
        print({"i": i, "cursor": response.get("cursor"), "records": len(response["records"])})
        assert response is not None
        assert response.get("cursor") is None or isinstance(response.get("cursor"), str)
        assert response.get("records") is not None
        cursor = response.get("cursor")
        for record in response["records"]:
            print({"uri": record["uri"]})
            r = agent.deletePost(record["uri"])
            print({"status_code": r.status_code})
            sleep(1)
        if cursor is None:
            break

    text = "Hello @ota.bsky.social, check out this link: https://example.com"
    rt = nanoatp.RichText(text)
    rt.detectFacets(agent)
    record = {"text": rt.text, "facets": rt.facets}
    response = agent.post(record)
    print(response)
    assert response is not None
    assert response.get("uri") is not None
    assert response.get("cid") is not None

    # record = {"text": "Hello0"}
    # response = agent.post(record)
    # print(response)
    # assert response is not None
    # assert response.get("uri") is not None
    # assert response.get("cid") is not None
    # root = response
    # parent = root
    # sleep(1)

    # record = {"text": "Hello1", "reply": {"root": root, "parent": parent}}
    # response = agent.post(record)
    # print(response)
    # assert response is not None
    # assert response.get("uri") is not None
    # assert response.get("cid") is not None
    # parent = response
    # sleep(1)

    # images = [agent.uploadImage(png, f"this is alt {i}") for i in range(4)]
    # embed = {"$type": "app.bsky.embed.images#main", "images": images}
    # record = {"text": "Hello2", "reply": {"root": root, "parent": parent}, "embed": embed}
    # response = agent.post(record)
    # print(response)
    # assert response is not None
    # assert response.get("uri") is not None
    # assert response.get("cid") is not None
    # sleep(1)

    # repo, collection, rkey = nanoatp.parseUri(response["uri"])
    # record = agent.getRecord(repo, collection, rkey)
    # assert response["uri"] == record["uri"]
    # assert response["cid"] == record["cid"]
    # print({"uri": record["uri"], "cid": record["cid"]})
    # sleep(1)
