# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from nanoatp import BskyAgent, RichText

agent = BskyAgent()
agent.login()

rt = RichText("Hello @nanoatp.bsky.social, check out this link: https://huggingface.co/")
rt.detectFacets(agent)

uri = rt.facets[1]["features"][0]["uri"]
external = agent.uploadExternal(uri)
embed = {"$type": "app.bsky.embed.external#main", "external": external}

record = {"text": rt.text, "facets": rt.facets, "embed": embed}
response = agent.post(record)
print(response)
