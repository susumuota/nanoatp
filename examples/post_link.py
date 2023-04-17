# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from nanoatp import BskyAgent, RichText

agent = BskyAgent()
agent.login()

uri = "https://example.com"
title = "This is a link title"
description = "This is a link description."

external = {"$type": "app.bsky.embed.external#external", "uri": uri, "title": title, "description": description}
embed = {"$type": "app.bsky.embed.external#main", "external": external}

rt = RichText("Hello @ota.bsky.social, check out this link: https://example.com")
rt.detectFacets(agent)

record = {"text": rt.text, "facets": rt.facets, "embed": embed}
response = agent.post(record)
print(response)
