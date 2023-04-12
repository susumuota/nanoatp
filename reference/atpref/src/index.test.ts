// SPDX-FileCopyrightText: 2023 Susumu OTA <1632335+susumuota@users.noreply.github.com>
// SPDX-License-Identifier: MIT

import { test, expect } from 'vitest';
import process from 'node:process';
import { BskyAgent } from '../dist/atpref';

const SERVICE = 'https://bsky.social/';

test('test bsky', async () => {
  const agent = new BskyAgent({ service: SERVICE });
  expect(agent.service.toString()).toBe(SERVICE);

  let r: any;
  r = await agent.login({ identifier: process.env.ATP_IDENTIFIER, password: process.env.ATP_PASSWORD });
  expect(r.success).toBe(true);
  expect(r.data).toBeDefined();
  const { did, handle, email, accessJwt, refreshJwt } = r.data;
  expect(did).toBeDefined();
  expect(handle).toBeDefined();
  expect(email).toBeDefined();
  expect(accessJwt).toBeDefined();
  expect(refreshJwt).toBeDefined();

  let record: any;
  record = { text: 'Hello0' };
  r = await agent.post(record);
  expect(r.uri).toBeDefined();
  expect(r.cid).toBeDefined();
  console.log(r);

  let root: any;
  let parent: any;
  root = r;
  parent = r;
  record = { text: 'Hello1', reply: { root, parent } };
  r = await agent.post(record);
  expect(r.uri).toBeDefined();
  expect(r.cid).toBeDefined();
  console.log(r);
  parent = r;

  r = await fetch('https://staging.bsky.app/static/favicon-16x16.png');
  r = await agent.uploadBlob(r.body, { encoding: 'image/png' });
  expect(r.success).toBe(true);
  expect(r.data).toBeDefined();
  const blob = r.data.blob;
  console.log(blob);
  console.log(blob.ref.toString());

  const image = {
    $type: 'app.bsky.embed.images#image',
    image: { $type: 'blob', ref: blob.ref.toString(), mimeType: blob.mimeType, size: blob.size },
    alt: 'this is alt',
  };
  record = {
    $type: 'app.bsky.feed.post',
    text: 'Hello2',
    reply: { root, parent },
    embed: { $type: 'app.bsky.embed.images#main', images: [image] },
  };
  r = await agent.post(record);
  expect(r.uri).toBeDefined();
  expect(r.cid).toBeDefined();
  console.log(r);
});
