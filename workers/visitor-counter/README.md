# Visitor counter Worker

A tiny Cloudflare Worker that powers the home-page greeting on the family site
(`juanarmond.github.io`): **"you're visiting from 🇧🇷 Brazil · you are visitor #N"**.

- **Country** comes from Cloudflare's edge (`request.cf.country`) — no third-party
  geo-IP service, no cookies, no personal data stored.
- **Count** is a single running total kept in a KV namespace. The visitor's own
  number is remembered by the browser (`localStorage`), so a reload never
  re-increments it; the global total only grows when a brand-new visitor loads
  the page (the front-end calls the Worker with `?new=1`).

The Worker source is [`worker.js`](worker.js). It is **not** part of the GitHub
Pages build — it runs on Cloudflare and the site calls it over `fetch`.

## Deploy (dashboard, ~3 minutes)

1. **dash.cloudflare.com → Compute (Workers) → Create → Create Worker.** Name it
   e.g. `family-visitor-counter`. Deploy the default, then **Edit code**.
2. Paste the whole contents of `worker.js` over the template, and **Deploy**.
3. Create the KV store: **Storage & Databases → KV → Create a namespace**, name it
   `family-visitors`.
4. Bind it to the Worker: **your Worker → Settings → Bindings → Add → KV namespace.**
   Set **Variable name** to exactly `COUNTER` and select the `family-visitors`
   namespace. Save and redeploy if prompted.
5. Copy the Worker's URL — it looks like
   `https://family-visitor-counter.<your-subdomain>.workers.dev`. Send that URL to
   the maintainer; it goes into `VISITOR_API` in
   `family-tree-viewer/app.js` and the greeting goes live.

Until `VISITOR_API` is set, the front-end feature is dormant and the greeting
stays hidden — nothing breaks.

## Deploy (Wrangler CLI, alternative)

```sh
npm i -g wrangler
wrangler login
wrangler kv namespace create COUNTER          # note the returned id
# add the id to wrangler.toml under [[kv_namespaces]], then:
wrangler deploy
```

A ready-to-edit [`wrangler.toml`](wrangler.toml) is included; drop in the KV
namespace id it prints and run `wrangler deploy`.

## Privacy

Country-level only. No cookies, no IP stored, nothing that identifies a person.
Consistent with the site's privacy posture; the footer already discloses that
visitor statistics are collected anonymously.
