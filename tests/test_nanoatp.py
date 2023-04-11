# SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

import nanoatp


def test_version():
    assert nanoatp.__version__ == "0.1.0"


def test_bskyagent():
    agent = nanoatp.BskyAgent()
    print(agent)
    assert agent is not None
    assert agent.service == "https://bsky.social"
    assert agent.requests is not None
    assert agent.session is None
    session = agent.login()  # Use environment variables ATP_IDENTIFIER and ATP_PASSWORD
    print(session)
    assert session is not None
    assert session.get("did") is not None
    assert session.get("handle") is not None
    assert session.get("email") is not None
    assert session.get("accessJwt") is not None
    assert session.get("refreshJwt") is not None
    response = agent.post({"text": "Hello, world!"})
    print(response)
    assert response is not None
    assert response.get("uri") is not None
    assert response.get("cid") is not None
