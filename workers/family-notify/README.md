# Family-notify Worker — "What's new" push notifications

A Cloudflare Worker that sends one push notification to every subscribed phone or browser
each time the site publishes new curated "What's new" entries (milestones, corrections,
new people). Routine document additions never notify on their own; they only add
"+N new documents" to a summary.

How it fits together:

1. **The site** (`family-tree-viewer/`) shows a "Turn on notifications" bar at the top of
   the What's new panel once this Worker's `/health` answers. A tap asks the browser for
   permission, creates a push subscription and sends it here. On iPhone/iPad (iOS 16.4+)
   this only works after the site is added to the Home Screen and opened from there; the
   bar says so.
2. **This Worker** stores each subscription in KV — only the push-service URL, two browser
   keys and the language (EN/PT). Nothing personal. It accepts subscriptions only from the
   site's origin, and only for real push services (Apple, Google, Mozilla, Microsoft).
3. **The deploy workflow** (`.github/workflows/static.yml`) compares the live
   `updates.json` with the one being published (`scripts/push_new_updates.py`). After the
   deploy it calls `/notify` with one bilingual summary. The Worker encrypts it for each
   device (RFC 8291) and signs it with VAPID (RFC 8292). Expired subscriptions are deleted
   automatically. Without the GitHub secrets below, those steps are simply skipped.

The Worker has no dependencies, so it can be pasted into the dashboard. Its crypto is
covered by `tests/js/push-crypto.test.mjs`, which decrypts and verifies what it produces.

## Current deployment (2026-10-09)

Deployed with Wrangler to <https://family-notify.juan-armond.workers.dev> (KV namespace
`SUBSCRIPTIONS`, id in `wrangler.toml`; secrets `VAPID_PRIVATE_KEY` and `NOTIFY_TOKEN` set
from `_local/`). The GitHub repository secrets `NOTIFY_ENDPOINT` and `NOTIFY_TOKEN` are set,
so every deploy that adds a curated What's new entry now sends one notification. To
redeploy after editing `worker.js`: `cd workers/family-notify && wrangler deploy`.

## Keys (already generated)

`node workers/family-notify/generate-keys.mjs` was run on 2026-10-09:

- the **public key** is in [`wrangler.toml`](wrangler.toml) (`VAPID_PUBLIC_KEY`) — not secret;
- the **private key** is in `_local/notify-vapid-private-key.txt` — secret, gitignored;
- the **deploy token** is in `_local/notify-token.txt` — secret, gitignored.

Never rotate the keys casually: every existing subscription is tied to the public key.

## Deploy (dashboard, ~5 minutes)

1. **Workers & Pages → Create → Worker**, name it `family-notify` (the site expects
   `https://family-notify.juan-armond.workers.dev`). Deploy the default, then **Edit code**,
   paste the whole of [`worker.js`](worker.js) and **Deploy**.
2. **Storage & Databases → KV → Create a namespace** (e.g. `family-notify-subscriptions`),
   then **your Worker → Settings → Bindings → Add → KV namespace**, variable name
   `SUBSCRIPTIONS`.
3. **Your Worker → Settings → Variables and Secrets:**
   - `VAPID_PUBLIC_KEY` — type *Text*, the value from `wrangler.toml`;
   - `VAPID_PRIVATE_KEY` — type *Secret*, the contents of `_local/notify-vapid-private-key.txt`;
   - `NOTIFY_TOKEN` — type *Secret*, the contents of `_local/notify-token.txt`.
4. Open <https://family-notify.juan-armond.workers.dev/health>. It should answer
   `{"ok":true,"publicKey":"…"}`.

## Deploy (Wrangler CLI, alternative)

```sh
cd workers/family-notify
npx wrangler kv namespace create SUBSCRIPTIONS     # paste the id into wrangler.toml
npx wrangler secret put VAPID_PRIVATE_KEY < ../../_local/notify-vapid-private-key.txt
npx wrangler secret put NOTIFY_TOKEN < ../../_local/notify-token.txt
npx wrangler deploy
```

## Connect the deploy workflow (GitHub)

Add two **repository secrets** (Settings → Secrets and variables → Actions):

- `NOTIFY_ENDPOINT` = `https://family-notify.juan-armond.workers.dev`
- `NOTIFY_TOKEN` = the contents of `_local/notify-token.txt`

With the GitHub CLI: `gh secret set NOTIFY_ENDPOINT --body https://family-notify.juan-armond.workers.dev`
and `gh secret set NOTIFY_TOKEN < _local/notify-token.txt`.

## Check it works

1. Open the site on your phone (on iPhone: from the Home Screen icon), open **What's new**,
   tap **Turn on notifications** and allow them.
2. From this repository, send a test notification to every subscribed device:

   ```sh
   NOTIFY_ENDPOINT=https://family-notify.juan-armond.workers.dev \
   NOTIFY_TOKEN="$(cat _local/notify-token.txt)" \
   python3 scripts/push_new_updates.py --test
   ```

3. From then on, every deploy that adds a curated What's new entry sends one notification.
   Tapping it opens the site on What's new.

## Limits

- Cloudflare's free plan allows 50 outgoing requests per Worker call, so `/notify` sends to
  40 devices at a time and returns a cursor; the script follows it until everyone is reached.
- Push delivery is best effort: phones in power-saving mode may show it late, and a device
  that never opens the site again eventually drops its subscription.
