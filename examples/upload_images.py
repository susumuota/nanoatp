# SPDX-FileCopyrightText: 2023-2025 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

import os
import tempfile

import requests

from nanoatp import BskyAgent

agent = BskyAgent()
agent.login()

# download an image for example
response = requests.get("https://bsky.app/static/favicon-16x16.png")

with tempfile.TemporaryDirectory() as tmp_dir:
    # save to a temporary file
    tmp_file = os.path.join(tmp_dir, "favicon-16x16.png")
    with open(tmp_file, "wb") as f:
        f.write(response.content)
    # upload the image 4 times
    images = [agent.uploadImage(tmp_file, f"this is alt {i}") for i in range(4)]
    # post a record with 4 images
    embed = {"$type": "app.bsky.embed.images", "images": images}
    record = {"text": "upload images", "embed": embed}
    response = agent.post(record)
    print(response)
