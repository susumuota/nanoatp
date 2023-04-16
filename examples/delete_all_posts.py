# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

# THIS SCRIPT DELETES ALL POSTS FROM YOUR ACCOUNT. USE WITH CAUTION!!!

from time import sleep

from nanoatp import BskyAgent

agent = BskyAgent()
session = agent.login()  # Use environment variables ATP_IDENTIFIER and ATP_PASSWORD

cursor = ""
while True:
    response = agent.listRecords(session["did"], "app.bsky.feed.post", limit=100, cursor=cursor, reverse=True)
    print(response.get("cursor"))
    cursor = response.get("cursor") or ""
    for record in response["records"]:
        print(record["value"]["text"])
        r = agent.deletePost(record["uri"])
        print(r.status_code)
        sleep(1)
    if not cursor:
        break
