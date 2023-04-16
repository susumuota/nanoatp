# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from nanoatp import BskyAgent

agent = BskyAgent()
session = agent.login()  # Use environment variables ATP_IDENTIFIER and ATP_PASSWORD

record = {"text": "Hello World!"}
response = agent.post(record)
print(response)
