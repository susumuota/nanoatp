# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from mimetypes import guess_type
from os import getenv
from typing import Any
from urllib.parse import urlparse, quote

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
        id = identifier or getenv("ATP_IDENTIFIER") or ""
        pw = password or getenv("ATP_PASSWORD") or ""
        session = self._server_createSession(id, pw)
        if session.get("error") or not session.get("accessJwt"):
            self.session = {}
            self.headers = {}
            raise Exception(str(session))
        self.session = session
        accessJwt = self.session.get("accessJwt")
        self.headers = {"Authorization": f"Bearer {accessJwt}"}
        return self.session

    def getPost(self, repo: str, rkey: str, cid: str = ""):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/bsky-agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        return self._repo_getRecord(repo, "app.bsky.feed.post", rkey, cid)

    def post(self, record: dict[str, Any]):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/bsky-agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        if not record.get("createdAt"):
            record.update({"createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")})
        if not record.get("$type"):
            record.update({"$type": "app.bsky.feed.post"})
        repo = self.session.get("did") or self.session.get("handle") or ""
        return self._repo_createRecord(repo, "app.bsky.feed.post", record)

    def deletePost(self, postUri: str):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/bsky-agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        repo, collection, rkey = parseAtUri(postUri)
        if not (repo and collection and rkey):
            raise Exception(f"Invalid postUri format: {postUri}")
        return self._repo_deleteRecord(repo, collection, rkey)

    def uploadBlob(self, data: bytes, encoding: str):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        return self._repo_uploadBlob(data, encoding)

    def resolveHandle(self, handle: str):
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        return self._identity_resolveHandle(handle)

    def uploadImage(self, path: str, alt: str = "", encoding: str = ""):
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json"""
        if not self.session:
            raise Exception("Not logged in")
        encoding = encoding or guess_type(path)[0] or "application/octet-stream"
        data = b""
        with open(path, "rb") as f:
            data = f.read()
        response = self._repo_uploadBlob(data, encoding)
        blob: dict[str, str] = response.get("blob") or {}
        if blob is {}:
            raise Exception(str(response))
        image: dict[str, Any] = {
            "$type": "app.bsky.embed.images#image",
            "alt": alt,
            "image": blob,
        }
        return image

    def uploadExternal(self, uri: str):
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/external.json"""
        if not self.session:
            raise Exception("Not logged in")
        metadata = getLinkMetaData(uri)
        external: dict[str, Any] = {
            "$type": "app.bsky.embed.external#external",
            "uri": uri,
            "title": metadata["title"],
            "description": metadata["description"],
        }
        if metadata["data"] and metadata["encoding"]:
            response = self._repo_uploadBlob(metadata["data"], metadata["encoding"])
            blob: dict[str, str] = response.get("blob") or {}
        external.update({"thumb": blob}) if blob is not {} else None
        return external

    def _server_createSession(self, identifier: str, password: str) -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/server/createSession.json"""
        json = {"identifier": identifier, "password": password}
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.server.createSession", json=json)
        return response.json()

    def _repo_createRecord(
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

    def _repo_getRecord(self, repo: str, collection: str, rkey: str, cid: str = "") -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/getRecord.json"""
        params = {"repo": repo, "collection": collection, "rkey": rkey}
        params.update({"cid": cid}) if cid != "" else None
        response = self.requests.get(
            f"{self.service}/xrpc/com.atproto.repo.getRecord", headers=self.headers, params=params
        )
        return response.json()

    def _repo_deleteRecord(
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

    def _repo_listRecords(
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

    def _repo_uploadBlob(self, data: bytes, encoding: str) -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/uploadBlob.json"""
        headers = {"Content-Type": encoding, "Content-Length": str(len(data))}
        headers.update(self.headers)
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.repo.uploadBlob", headers=headers, data=data)
        return response.json()

    def _identity_resolveHandle(self, handle: str) -> dict[str, str]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/identity/resolveHandle.json"""
        params = {"handle": handle}
        response = self.requests.get(
            f"{self.service}/xrpc/com.atproto.identity.resolveHandle", headers=self.headers, params=params
        )
        return response.json()

    def _graph_getBlocks(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/graph/getBlocks.json"""
        params: dict[str, str | int] = {}
        params.update({"limit": limit}) if limit != 50 else None  # 1 <= limit <= 100
        params.update({"cursor": cursor}) if cursor != "" else None
        response = self.requests.get(
            f"{self.service}/xrpc/app.bsky.graph.getBlocks", headers=self.headers, params=params
        )
        return response.json()


def parseAtUri(uri: str):
    """https://github.com/bluesky-social/atproto/blob/main/packages/uri/src/index.ts"""
    u = urlparse(uri)
    repo = u.netloc
    _, collection, rkey = u.path.split("/")
    return repo, collection, rkey


def getLinkMetaData(uri: str) -> dict[str, str | bytes]:
    """https://cardyb.bsky.app/v1/extract?url={quote(uri)}
    returns {"error", "likely_type", "url", "title", "description", "image", "data", "encoding"}
    or raises Exception.
    """
    response = requests.get(f"https://cardyb.bsky.app/v1/extract?url={quote(uri)}")
    if response.status_code != 200:
        raise Exception(f"HTTP status code {response.status_code}")
    json = response.json()
    if json["error"]:
        raise Exception(json["error"])
    json.update({"data": b""})
    json.update({"encoding": ""})
    if json["image"]:  # should be https://cardyb.bsky.app/v1/image?url=...
        try:
            image_data = getImageData(json["image"])
        except Exception:
            return json  # no image data
        json.update({"data": image_data["data"]})
        json.update({"encoding": image_data["encoding"]})
    return json


def getImageData(uri: str, chunk_size: int = 8192) -> dict[str, str | bytes]:
    """uri should be https://cardyb.bsky.app/v1/image?url=...
    returns {"data", "encoding"} or raises Exception.
    """
    try:
        response = requests.get(uri, stream=True)
        if response.status_code != 200:
            raise Exception(f"HTTP status code {response.status_code}")
        buffer = BytesIO()
        for chunk in response.iter_content(chunk_size=chunk_size):
            buffer.write(chunk) if chunk else None
        data = buffer.getvalue()
        encoding = response.headers.get("Content-Type") or ""
    finally:
        buffer.close() if buffer else None
        response.close() if response else None
    if data and encoding:
        return {"data": data, "encoding": encoding}
    else:
        raise Exception("no data or encoding")
