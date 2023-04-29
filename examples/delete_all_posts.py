# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

# THIS SCRIPT DELETES ALL POSTS FROM YOUR ACCOUNT. USE WITH CAUTION!!!

from time import sleep

from nanoatp import BskyAgent

agent = BskyAgent()
session = agent.login()

cursor = ""
records = []
while True:
    # newest first
    response = agent._repo_listRecords(session["did"], "app.bsky.feed.post", limit=10, cursor=cursor)
    print(response.get("cursor"), len(response.get("records") or []))
    cursor = response.get("cursor") or ""
    records.extend(response.get("records") or [])
    if not cursor:
        break
    sleep(1)

records.reverse()  # oldest first
# records = sorted(records, key=lambda x: x["value"]["createdAt"])  # should be same as above

# delete all posts from oldest to newest
for record in records:
    print("deleting...", record["value"]["text"].replace("\n", " ")[:40])
    r = agent.deletePost(record["uri"])
    print("deleting...done: ", r.status_code)
    sleep(1)
