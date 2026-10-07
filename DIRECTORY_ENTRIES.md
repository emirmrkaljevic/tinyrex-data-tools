# Directory / awesome-list entries (prepared, NOT submitted)

## 1. jivoi/awesome-osint (best fit; CONTRIBUTING allows self-promo with up-front disclosure, one PR per entry, alphabetical)
Section: "Domain and IP Research", insert between `[StatsCrop]` and `[TinyScan]`:
* [Tech Stack Detector](https://apify.com/tinyrex/tech-stack-detector) - Bulk website technology lookup for lists of domains (7,600+ Wappalyzer-compatible fingerprints) plus email provider (MX), SPF senders and DMARC policy, exported as JSON/CSV.
PR title: Add Tech Stack Detector to Domain and IP Research
PR body: Adds https://apify.com/tinyrex/tech-stack-detector, a bulk technology profiler (CMS, e-commerce, analytics, CDN) that also reports MX provider, SPF senders and DMARC policy, useful for profiling many domains at once in OSINT/recon. Disclosure: I am the author of this tool. It is a paid hosted tool (about $4 per 1,000 domains, failed lookups free, Apify free tier covers a trial).

## 2. foxck016077/awesome-apify-actors (accepts PRs; format "Name by `user` - N runs"; prefers 10k+ lifetime runs -> submit only once runs grow)
Jobs:
- [Greenhouse / Lever / Ashby Jobs Scraper](https://apify.com/tinyrex/ats-jobs-scraper) by `tinyrex` - All open jobs from Greenhouse, Lever, Ashby, Personio, Teamtailor and Recruitee boards in one schema; auto-detects the ATS from a company website.
- [Workday Jobs Scraper](https://apify.com/tinyrex/workday-jobs-scraper) by `tinyrex` - All jobs from myworkdayjobs.com career sites with full descriptions and exact posting dates.
- [Arbeitsagentur Jobs Scraper](https://apify.com/tinyrex/dach-jobs-scraper) by `tinyrex` - Jobs from the Bundesagentur fuer Arbeit and EURES (DE, AT, CH, EU) via the official APIs.
E-commerce:
- [Shopify Products Scraper](https://apify.com/tinyrex/shopify-products-scraper) by `tinyrex` - Products, variants, prices, discounts and stock from any Shopify store.
- [WooCommerce Products Scraper](https://apify.com/tinyrex/woocommerce-products-scraper) by `tinyrex` - Products, variations, prices and stock from any WooCommerce store.
Lead Generation:
- [Tech Stack Detector](https://apify.com/tinyrex/tech-stack-detector) by `tinyrex` - Bulk Wappalyzer-style technology lookup plus email provider, SPF and DMARC for lists of domains.
(Add "- N runs" from the Store API at submission time.)

## 3. AgentsAPI/awesome-agent-apis: no action needed; it auto-imports public Apify actors daily by Store category.

## Checked and NOT suitable (rules exclude us)
- lorien/awesome-web-scraping: CONTRIBUTING restricts web services/remote APIs and anything MCP/AI-agent related.
- punkpeye/awesome-mcp-servers: only installable MCP servers with a GitHub repo; our actors are reachable via Apify's MCP server, which is already listed.
- public-apis/public-apis: free public APIs only, not paid wrappers.
- mcp.so / Smithery / Glama / other MCP directories: require an account or web-form submission (not allowed for me).
- makegov/awesome-procurement-data (TED fit): unmaintained since 2023, US-focused.
