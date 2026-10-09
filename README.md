# TinyRex Data Tools: web data APIs and scraper guides

Practical, copy-paste guides for pulling clean, structured data from the public web with small, pay-per-result tools on [Apify](https://apify.com/tinyrex): **bulk tech stack lookup (Wappalyzer / BuiltWith alternative)**, **job postings from Greenhouse, Lever, Ashby, Personio and Workday**, **Shopify and WooCommerce product export to CSV**, **remote jobs from Himalayas, Remote OK and We Work Remotely**, **RSS/Atom feeds to JSON/CSV**, **all URLs from XML sitemaps (with broken link check)**, **EU public tenders from TED** and **EU funding calls (Horizon Europe)**.

**Website:** https://emirmrkaljevic.github.io/tinyrex-data-tools/

Every guide includes a working input example, real sample output, and Python, JavaScript and curl snippets, plus how to call the tool from AI agents (Claude, Cursor, n8n) through the [Apify MCP server](https://mcp.apify.com).

## Guides

| Guide | Tool on Apify | Price |
|---|---|---|
| [Bulk tech stack lookup: a Wappalyzer / BuiltWith alternative for thousands of domains](https://emirmrkaljevic.github.io/tinyrex-data-tools/bulk-tech-stack-lookup-wappalyzer-alternative/) | [tech-stack-detector](https://apify.com/tinyrex/tech-stack-detector) | about $4 per 1,000 analyzed domains; unreachable, blocked and timed-out domains are free |
| [How to scrape Greenhouse, Lever and Ashby jobs (plus Personio, Teamtailor, Recruitee)](https://emirmrkaljevic.github.io/tinyrex-data-tools/scrape-greenhouse-lever-ashby-jobs/) | [ats-jobs-scraper](https://apify.com/tinyrex/ats-jobs-scraper) | $1 per 1,000 jobs; companies without a supported ATS and filtered-out jobs are free |
| [How to export all products from any Shopify store to CSV or JSON](https://emirmrkaljevic.github.io/tinyrex-data-tools/export-shopify-store-products-to-csv/) | [shopify-products-scraper](https://apify.com/tinyrex/shopify-products-scraper) | $0.70 per 1,000 products (+$0.50 per 1,000 for optional stock details) |
| [How to scrape jobs from Workday career sites (myworkdayjobs.com)](https://emirmrkaljevic.github.io/tinyrex-data-tools/scrape-workday-jobs-myworkdayjobs/) | [workday-jobs-scraper](https://apify.com/tinyrex/workday-jobs-scraper) | $0.80 per 1,000 jobs with full descriptions; inputs without a Workday site are free |
| [How to export products from any WooCommerce store to CSV or JSON](https://emirmrkaljevic.github.io/tinyrex-data-tools/export-woocommerce-store-products-to-csv/) | [woocommerce-products-scraper](https://apify.com/tinyrex/woocommerce-products-scraper) | $0.60 per 1,000 products |
| [How to export EU public tenders from TED (Tenders Electronic Daily) to CSV or JSON](https://emirmrkaljevic.github.io/tinyrex-data-tools/ted-tenders-api-export/) | [ted-tenders-scraper](https://apify.com/tinyrex/ted-tenders-scraper) | $2.50 per 1,000 notices; already-seen notices in alert mode are free |
| [How to scrape remote jobs from Himalayas, Remote OK, We Work Remotely and more in one run](https://emirmrkaljevic.github.io/tinyrex-data-tools/remote-jobs-api-himalayas-remoteok-weworkremotely/) | [remote-jobs-scraper](https://apify.com/tinyrex/remote-jobs-scraper) | $0.80 per 1,000 jobs with full descriptions; filtered-out, duplicate and already-seen jobs are free |
| [How to export open EU funding calls (Horizon Europe, Digital Europe, cascade funding) to CSV or JSON](https://emirmrkaljevic.github.io/tinyrex-data-tools/eu-funding-calls-horizon-europe-api/) | [eu-grants-scraper](https://apify.com/tinyrex/eu-grants-scraper) | $3 per 1,000 funding calls; filtered-out and already-seen calls are free |
| [How to turn any RSS or Atom feed into JSON or CSV (bulk, with monitoring)](https://emirmrkaljevic.github.io/tinyrex-data-tools/rss-feed-to-json-csv-api/) | [rss-feed-scraper](https://apify.com/tinyrex/rss-feed-scraper) | $0.30 per 1,000 feed items; failed feeds, filtered, duplicate and already-seen items are free |
| [How to extract all URLs from a website's sitemap (and find broken links)](https://emirmrkaljevic.github.io/tinyrex-data-tools/extract-all-urls-from-sitemap/) | [sitemap-scraper](https://apify.com/tinyrex/sitemap-scraper) | $0.20 per 1,000 URLs ($0.50 per 1,000 status checks); sites without a sitemap are free |

## Tutorials

- [How to get any Shopify store's products into Google Sheets](https://emirmrkaljevic.github.io/tinyrex-data-tools/shopify-products-to-google-sheets/)
- [How to find which websites in a list use Shopify, WooCommerce or HubSpot](https://emirmrkaljevic.github.io/tinyrex-data-tools/find-shopify-stores-from-domain-list/)
- [How to get daily alerts for new EU public tenders (TED)](https://emirmrkaljevic.github.io/tinyrex-data-tools/eu-tender-alerts-google-sheets-slack/)
- [How to get remote job listings from 5 job boards into one spreadsheet](https://emirmrkaljevic.github.io/tinyrex-data-tools/remote-jobs-to-google-sheets/)
- [How to send new items from many RSS feeds to Google Sheets or Slack](https://emirmrkaljevic.github.io/tinyrex-data-tools/rss-feeds-to-google-sheets-slack/)
- [How to find broken pages and redirects in your XML sitemap](https://emirmrkaljevic.github.io/tinyrex-data-tools/find-broken-links-in-sitemap/)

## Quick start (any tool)

```bash
curl -X POST "https://api.apify.com/v2/acts/tinyrex~tech-stack-detector/run-sync-get-dataset-items?format=json" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"domains": ["vercel.com", "gymshark.com"]}'
```

```python
from apify_client import ApifyClient
client = ApifyClient("<YOUR_APIFY_TOKEN>")
run = client.actor("tinyrex/ats-jobs-scraper").call(run_input={"companies": ["stripe.com"]})
print(list(client.dataset(run["defaultDatasetId"]).iterate_items())[:3])
```

### Use from an AI agent (MCP)

```json
{ "mcpServers": { "apify": { "url": "https://mcp.apify.com?tools=tinyrex/tech-stack-detector,tinyrex/ats-jobs-scraper,tinyrex/shopify-products-scraper,tinyrex/workday-jobs-scraper,tinyrex/woocommerce-products-scraper,tinyrex/ted-tenders-scraper,tinyrex/remote-jobs-scraper,tinyrex/eu-grants-scraper,tinyrex/rss-feed-scraper,tinyrex/sitemap-scraper" } } }
```

## Rebuilding the site / adding a new actor

1. Make sure the actor is **public** on Apify (under `tinyrex`) and has `README.md` (with a ```json example input block) and `sample-output.json` in `/workspace/zarada/actors/<name>/`.
2. Add an entry for it to the `G` dict in `build.py` (slug, ptitle, h1, desc, kw, short, price, intro, steps, faq). Actors without an entry are skipped.
3. Rebuild and publish:

```bash
cd /workspace/zarada/site
APIFY_TOKEN=... python3 build.py      # regenerates docs/ (pages, sitemap.xml, robots.txt)
git add -A && git commit -m "Add <name> guide" && git push   # GitHub Pages redeploys from main /docs
```

4. Add the guide link line (see existing actor READMEs, placed just above `## Related actors`) to the actor's README and `apify push`.

## Principles

- Only public data; official APIs and public feeds wherever they exist.
- Pay per delivered result; failed, blocked or filtered-out inputs are free or much cheaper.
- Clean, flat JSON that works in spreadsheets and LLM tools alike.

## Repository layout

- `docs/` is the static site served by GitHub Pages.
- `build.py` regenerates the site from the actor metadata.

Found a bug or want a data source covered? Open an issue.

## License

Content and code examples: MIT.
