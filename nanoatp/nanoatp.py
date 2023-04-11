# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
import os

import requests


class BskyAgent:
    def __init__(self, service: str = "https://bsky.social") -> None:
        self.service = service
        self.requests = requests.Session()
        self.session = None

    def login(self, identifier: str | None = None, password: str | None = None) -> dict[str, str]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/server/createSession.json"""
        id = identifier or os.getenv("ATP_IDENTIFIER")
        pw = password or os.getenv("ATP_PASSWORD")
        json = {"identifier": id, "password": pw}
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.server.createSession", json=json)
        sess = response.json()
        if not self._validateSession(sess):
            self.session = None
            raise Exception(str(sess))
        self.session = sess
        return self.session

    def post(self, record: dict[str, str]) -> dict[str, str]:
        """https://github.com/bluesky-social/atproto/blob/main/lexicons/com/atproto/repo/createRecord.json"""
        if not self.session:
            raise Exception("Not logged in")
        if not record.get("createdAt"):
            record["createdAt"] = self._now()
        accessJwt = self.session.get("accessJwt")
        headers = {"Authorization": f"Bearer {accessJwt}"}
        json = {"repo": self.session.get("did"), "collection": "app.bsky.feed.post", "record": record}
        response = self.requests.post(f"{self.service}/xrpc/com.atproto.repo.createRecord", headers=headers, json=json)
        return response.json()

    def _validateSession(self, json: dict[str, str]) -> bool:
        return not json.get("error") and list(json.keys()) == ["did", "handle", "email", "accessJwt", "refreshJwt"]

    def _now(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
