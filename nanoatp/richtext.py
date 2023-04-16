# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from typing import Any

from tld import get_tld

from nanoatp import BskyAgent


# TODO: utf16
class RichText:
    def __init__(self, text: str):
        self.text = text
        self.facets: list[dict[str, Any]] = []

    def detectFacets(self, agent: BskyAgent):
        self.facets = detectFacets(self.text)
        for facet in self.facets:
            for feature in facet["features"]:
                if feature["$type"] == "app.bsky.richtext.facet#mention":
                    response = agent.resolveHandle(feature["did"])
                    feature["did"] = response.get("did") or ""
        self.facets.sort(key=lambda facet: facet["index"]["byteStart"])

    def __str__(self):
        return self.text

    def __len__(self):
        return len(self.text)


MENTION_PATTERN = re.compile(r"(^|\s|\()(@)([a-zA-Z0-9.-]+)(\b)")
LINK_PATTERN = re.compile(
    r"(^|\s|\()((https?:\/\/[\S]+)|(([a-z][a-z0-9]*(\.[a-z0-9]+)+)[\S]*))", re.IGNORECASE | re.MULTILINE
)


def detectFacets(text: str):
    """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/rich-text/detection.ts"""
    facets: list[dict[str, Any]] = []
    facets.extend(detectMentions(text))
    facets.extend(detectLinks(text))
    return facets


def detectMentions(text: str):
    """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/rich-text/detection.ts"""
    facets: list[dict[str, Any]] = []
    for m in re.findall(MENTION_PATTERN, text):
        domain = m[2]
        if not isValidDomain(domain) and not domain.endswith(".test"):
            continue
        start = text.find(domain) - 1  # -1 is "@"
        end = start + len(domain) + 1
        facets.append(
            {
                "$type": "app.bsky.richtext.facet",
                "index": {"byteStart": start, "byteEnd": end},
                # must be resolved afterwards
                "features": [{"$type": "app.bsky.richtext.facet#mention", "did": domain}],
            }
        )
    return facets


def detectLinks(text: str):
    """https://github.com/bluesky-social/atproto/blob/main/packages/api/src/rich-text/detection.ts"""
    facets: list[dict[str, Any]] = []
    for m in re.findall(LINK_PATTERN, text):
        uri = m[1]
        start = text.find(uri)
        end = start + len(uri)
        if re.match(r"[.,;!?]$", uri):
            uri = uri[:-1]
            end -= 1
        if re.match(r"[)]$", uri) and "(" not in uri:
            uri = uri[:-1]
            end -= 1
        facets.append(
            {
                "$type": "app.bsky.richtext.facet",
                "index": {"byteStart": start, "byteEnd": end},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": uri}],
            }
        )
    return facets


def isValidDomain(domain: str):
    return get_tld(domain, fail_silently=True, fix_protocol=True) is not None
