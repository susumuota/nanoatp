# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from mimetypes import guess_type
import os
from typing import Any

import requests


# TODO: replace Any
class BskyAgent:
    def __init__(self, service: str = "https://bsky.social") -> None:
        self.service = service
        self.requests = requests.Session()
        self.session = None
        self.headers = {}

    def login(self, identifier: str = "", password: str = "") -> Any:
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/agent.ts"""
        id = identifier or os.getenv("ATP_IDENTIFIER") or ""
        pw = password or os.getenv("ATP_PASSWORD") or ""
        session = self.createSession(id, pw)
        if not self._verifySession(session):
            self.session = None
            self.headers = {}
            raise Exception(str(session))
        self.session = session
        accessJwt = self.session["accessJwt"]
        self.headers = {"Authorization": f"Bearer {accessJwt}"}
        return self.session

    def post(self, record: dict[str, Any]) -> Any:
        """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/bsky-agent.ts"""
        if not self.session:
            raise Exception("Not logged in")
        if not record.get("createdAt"):
            record["createdAt"] = self._now()
        if not record.get("$type"):
            record["$type"] = "app.bsky.feed.post"
        return self.createRecord(self.session["did"], "app.bsky.feed.post", record)

    def uploadImage(self, path: str, alt: str = "", contentType: str = "") -> Any:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/embed/images.json"""
        if not self.session:
            raise Exception("Not logged in")
        contentType = contentType or guess_type(path)[0] or "application/octet-stream"
        data = b""
        with open(path, "rb") as f:
            data = f.read()
        response = self.uploadBlob(data, contentType)
        if not response.get("blob"):
            raise Exception(str(response))
        blob = response.get("blob")
        image = {
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

    def createSession(self, identifier: str, password: str) -> Any:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/server/createSession.json"""
        json = {"identifier": identifier, "password": password}
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.server.createSession", json=json)
        return response.json()

    def createRecord(self, repo: str, collection: str, record: dict[str, Any]) -> Any:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/createRecord.json"""
        json = {"repo": repo, "collection": collection, "record": record}
        response = self.requests.post(
            f"{self.service}/xrpc/com.atproto.repo.createRecord", headers=self.headers, json=json
        )
        return response.json()

    def uploadBlob(self, data: bytes, contentType: str) -> Any:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/uploadBlob.json"""
        headers = {"Content-Type": contentType, "Content-Length": str(len(data))}
        headers.update(self.headers)
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.repo.uploadBlob", headers=headers, data=data)
        return response.json()

    def _verifySession(self, json: dict[str, str]) -> bool:
        return not json.get("error") and list(json.keys()) == ["did", "handle", "email", "accessJwt", "refreshJwt"]

    def _now(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
