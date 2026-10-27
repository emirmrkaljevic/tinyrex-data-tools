# TinyRex automation examples

Ready-to-import workflows that call TinyRex actors on Apify through the public Apify API
(`run-sync-get-dataset-items`). Each one runs the actor and returns the dataset items as output.

| Workflow | Actor | n8n | Make |
|---|---|---|---|
| Remote jobs by keyword | [Remote Jobs Scraper](https://apify.com/tinyrex/remote-jobs-scraper) | [n8n/remote-jobs.json](n8n/remote-jobs.json) | [make/remote-jobs.json](make/remote-jobs.json) |
| Shopify store catalog | [Shopify Products Scraper](https://apify.com/tinyrex/shopify-products-scraper) | [n8n/shopify-products.json](n8n/shopify-products.json) | [make/shopify-products.json](make/shopify-products.json) |
| Audio/video to text | [Audio & Video Transcriber](https://apify.com/tinyrex/audio-video-transcriber) | [n8n/transcriber.json](n8n/transcriber.json) | [make/transcriber.json](make/transcriber.json) |

## n8n
1. Workflows, Import from file, pick the JSON.
2. Create a Query Auth credential with name `token` and your Apify API token as value.
3. Edit the JSON body (keywords, stores, media URLs) and run. You can also replace the HTTP node with the official Apify node (Run actor and get dataset).

## Make
1. Create a scenario, open the menu, Import Blueprint, pick the JSON.
2. Replace `{{APIFY_TOKEN}}` with your token, or use the official Apify app module "Run an Actor".

Runs longer than 5 minutes should use the async run endpoint plus a webhook instead of the sync call.
Missing a field or an integration? Open an issue in this repo.
