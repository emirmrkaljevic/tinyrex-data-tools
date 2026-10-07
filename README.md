# TinyRex Data Tools: web data APIs and scraper guides

Practical, copy-paste guides for pulling clean, structured data from the public web with small, pay-per-result tools on [Apify](https://apify.com/tinyrex): **bulk tech stack lookup (Wappalyzer / BuiltWith alternative)**, **job postings from Greenhouse, Lever, Ashby, Personio, Workday and the Bundesagentur für Arbeit**, **Shopify and WooCommerce product export to CSV**, and **EU public tenders from TED**.

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
| [How to export jobs from the Bundesagentur für Arbeit (Arbeitsagentur) and EURES](https://emirmrkaljevic.github.io/tinyrex-data-tools/arbeitsagentur-jobs-api/) | [dach-jobs-scraper](https://apify.com/tinyrex/dach-jobs-scraper) | $1 per 1,000 jobs with full descriptions |

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
{ "mcpServers": { "apify": { "url": "https://mcp.apify.com?tools=tinyrex/tech-stack-detector,tinyrex/ats-jobs-scraper,tinyrex/shopify-products-scraper,tinyrex/workday-jobs-scraper,tinyrex/woocommerce-products-scraper,tinyrex/ted-tenders-scraper,tinyrex/dach-jobs-scraper" } } }
```

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
