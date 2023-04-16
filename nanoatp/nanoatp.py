# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
import os
from mimetypes import guess_type
from typing import Any
from urllib.parse import urlparse

import requests


# TODO: replace Any
# TODO: split BskyAgent and AtpAgent code
class BskyAgent:
    def __init__(self, service: str = "https://bsky.social"):
        self.service = service
        self.requests = requests.Session()
        self.session: dict[str, str] = {}
        self.headers: dict[str, str] = {}

    def login(self, identifier: str = "", password: str = ""):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/agent.ts"""
        id = identifier or os.getenv("ATP_IDENTIFIER") or ""
        pw = password or os.getenv("ATP_PASSWORD") or ""
        session = self.createSession(id, pw)
        if not verifySession(session):
            self.session = {}
            self.headers = {}
            raise Exception(str(session))
        self.session = session
        accessJwt = self.session.get("accessJwt")
        self.headers = {"Authorization": f"Bearer {accessJwt}"}
        return self.session

    def getPost(self, repo: str, rkey: str, cid: str = "") -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/bsky-agent.ts"""
        return self.getRecord(repo, "app.bsky.feed.post", rkey, cid)

    def post(self, record: dict[str, Any]):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/bsky-agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        if not record.get("createdAt"):
            record.update({"createdAt": now()})
        if not record.get("$type"):
            record.update({"$type": "app.bsky.feed.post"})
        repo = self.session.get("did") or self.session.get("handle") or ""
        return self.createRecord(repo, "app.bsky.feed.post", record)

    def deletePost(self, postUri: str):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/bsky-agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        repo, collection, rkey = parseUri(postUri)
        if not (repo and collection and rkey):
            raise Exception(f"Invalid postUrl format: {postUri}")
        return self.deleteRecord(repo, collection, rkey)

    def uploadImage(self, path: str, alt: str = "", encoding: str = ""):
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json"""
        if not self.session:
            raise Exception("Not logged in")
        encoding = encoding or guess_type(path)[0] or "application/octet-stream"
        data = b""
        with open(path, "rb") as f:
            data = f.read()
        response = self.uploadBlob(data, encoding)
        blob: dict[str, str] = response.get("blob") or {}
        if blob is {}:
            raise Exception(str(response))
        image: dict[str, Any] = {
            "$type": "app.bsky.embed.images#image",
            "alt": alt,
            "image": {
                "$type": "blob",
                "ref": blob.get("ref"),
                "mimeType": blob.get("mimeType"),
                "size": blob.get("size"),
            },
        }
        return image

    def createSession(self, identifier: str, password: str) -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/server/createSession.json"""
        json = {"identifier": identifier, "password": password}
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.server.createSession", json=json)
        return response.json()

    def createRecord(
        self,
        repo: str,
        collection: str,
        record: dict[str, Any],
        rkey: str = "",
        validate: bool = True,
        swapCommit: str = "",
    ) -> dict[str, str]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/createRecord.json"""
        json: dict[str, str | bool | dict[str, Any]] = {"repo": repo, "collection": collection, "record": record}
        json.update({"rkey": rkey}) if rkey != "" else None
        json.update({"validate": validate}) if not validate else None  # default is True
        json.update({"swapCommit": swapCommit}) if swapCommit != "" else None
        response = self.requests.post(
            f"{self.service}/xrpc/com.atproto.repo.createRecord", headers=self.headers, json=json
        )
        return response.json()

    def getRecord(self, repo: str, collection: str, rkey: str, cid: str = "") -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/getRecord.json"""
        params = {"repo": repo, "collection": collection, "rkey": rkey}
        params.update({"cid": cid}) if cid != "" else None
        response = self.requests.get(
            f"{self.service}/xrpc/com.atproto.repo.getRecord", headers=self.headers, params=params
        )
        return response.json()

    def deleteRecord(
        self, repo: str, collection: str, rkey: str, swapRecord: str = "", swapCommit: str = ""
    ) -> requests.Response:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/deleteRecord.json"""
        json = {"repo": repo, "collection": collection, "rkey": rkey}
        json.update({"swapRecord": swapRecord}) if swapRecord != "" else None
        json.update({"swapCommit": swapCommit}) if swapCommit != "" else None
        response = self.requests.post(
            f"{self.service}/xrpc/com.atproto.repo.deleteRecord", headers=self.headers, json=json
        )
        return response  # TODO

    def listRecords(
        self,
        repo: str,
        collection: str,
        limit: int = 50,
        cursor: str = "",
        rkeyStart: str = "",
        rkeyEnd: str = "",
        reverse: bool = False,
    ) -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/listRecords.json"""
        params: dict[str, str | int | bool] = {"repo": repo, "collection": collection}
        params.update({"limit": limit}) if limit != 50 else None  # 1 <= limit <= 100
        params.update({"cursor": cursor}) if cursor != "" else None
        params.update({"rkeyStart": rkeyStart}) if rkeyStart != "" else None
        params.update({"rkeyEnd": rkeyEnd}) if rkeyEnd != "" else None
        params.update({"reverse": reverse}) if reverse else None  # default is False
        response = self.requests.get(
            f"{self.service}/xrpc/com.atproto.repo.listRecords", headers=self.headers, params=params
        )
        return response.json()

    def uploadBlob(self, data: bytes, encoding: str) -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/uploadBlob.json"""
        headers = {"Content-Type": encoding, "Content-Length": str(len(data))}
        headers.update(self.headers)
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.repo.uploadBlob", headers=headers, data=data)
        return response.json()


# TODO: create util.py?
def verifySession(session: dict[str, str]):
    """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/server/createSession.json"""
    # email is optional
    return not session.get("error") and set(session.keys()).issuperset({"did", "handle", "accessJwt", "refreshJwt"})


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def parseUri(uri: str):
    u = urlparse(uri)
    repo = u.netloc
    _, collection, rkey = u.path.split("/")
    return repo, collection, rkey
