# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from nanoatp import BskyAgent, RichText

agent = BskyAgent()
agent.login()

rt = RichText("Hello @nanoatp.bsky.social, check out this link: https://example.com")
rt.detectFacets(agent)
print(rt.facets)

record = {"text": rt.text, "facets": rt.facets}
response = agent.post(record)
print(response)
