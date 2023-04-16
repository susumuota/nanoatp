# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
# SPDX-License-Identifier: MIT

from time import sleep

from nanoatp import BskyAgent

agent = BskyAgent()
session = agent.login()  # Use environment variables ATP_IDENTIFIER and ATP_PASSWORD
print(session.get("did"))
sleep(1)

record = {"text": "Hello World!"}
response = agent.post(record)
print(response)
sleep(1)

parent = response  # set parent
root = response  # set root

record = {"text": "Reply 1", "reply": {"root": root, "parent": parent}}
response = agent.post(record)
print(response)
sleep(1)

parent = response  # change parent
# root = parent    # not change root

record = {"text": "Reply 2", "reply": {"root": root, "parent": parent}}
response = agent.post(record)
print(response)
sleep(1)

parent = response  # change parent
root = response  # change root

record = {"text": "Reply 3", "reply": {"root": root, "parent": parent}}
response = agent.post(record)
print(response)
sleep(1)

# not change parent
# not change root

record = {"text": "Reply 4", "reply": {"root": root, "parent": parent}}
response = agent.post(record)
print(response)
