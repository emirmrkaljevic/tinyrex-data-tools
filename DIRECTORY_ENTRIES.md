# Directory / awesome-list entries

## Status (9 Oct 2026)
- jivoi/awesome-osint PR #1262 (Tech Stack Detector): CLOSED without merge by maintainer on 8 Oct, no comment. Do not resubmit.
- serpapi/awesome-seo-tools PR #418 (Sitemap Scraper): open, https://github.com/serpapi/awesome-seo-tools/pull/418
- AboutRSS/ALL-about-RSS PR #159 (RSS Feed Scraper): open, https://github.com/AboutRSS/ALL-about-RSS/pull/159
- Skipped: julionc/awesome-shopify (only open-source entries), foxck016077/awesome-apify-actors (wants 10k+ runs).
- AgentsAPI/awesome-agent-apis auto-lists all 9 older public actors (snapshot 8 Oct; still shows dach-jobs-scraper, should drop on the next daily refresh). RSS + Sitemap should appear on the next refresh.

## Status (16 Oct 2026)
- serpapi/awesome-seo-tools #418 and AboutRSS/ALL-about-RSS #159: still OPEN, no comments/reviews (last update 9 Oct).
- NEW teles/awesome-seo PR #224 (SEO On-Page Audit, 💰 badge, disclosure): https://github.com/teles/awesome-seo/pull/224 (fork emirmrkaljevic/awesome-seo, branch add-seo-on-page-audit).

## Status (19 Oct 2026)
- #418, #159, #224 still OPEN, no comments/reviews.
- NEW bekatom/awesome-growth-hacking PR #106 (Contact Details Extractor in Tools, disclosure): https://github.com/bekatom/awesome-growth-hacking/pull/106 (fork emirmrkaljevic/awesome-growth-hacking, branch add-contact-details-extractor). Maintainer hasn't merged since 26 Aug; ~15 tool PRs queued ahead.
- Next D10 PR #3 candidate: marketingtoolslist/awesome-marketing (broken-link-checker, Technical SEO).

## D2 shortlist (16 Oct 2026): lists that accept paid / hosted tools
One PR per list, disclosure in the PR body, neutral one-line entry, no mass self-promo.
1. serpapi/awesome-seo-tools (1.1k★, active) – PR #418 open (sitemap-scraper). Wait.
2. AboutRSS/ALL-about-RSS – PR #159 open (rss-feed-scraper). Wait.
3. teles/awesome-seo (885★) – README legend has 💰 paid badge; maintainer batch-reviews open PRs (last batch 30 Sep, flags "mass self-promotion"). Alphabetical, `- [Name](url) - Desc. <badge>`. → PR #224 opened 16 Oct (seo-on-page-audit).
4. bekatom/awesome-growth-hacking (538★) – merges single "Add X to Tools" PRs (3 merged 26 Aug), SaaS allowed, no CONTRIBUTING. Candidate: contact-details-extractor or tech-stack-detector in Tools. → next PR (D6).
5. dariubs/awesome-lead-generation (86★) – CONTRIBUTING allows paid if marked "(paid)", one entry/PR, neutral text, no affiliate links. Caveat: ~15 open PRs, maintainer closes some, merges rarely (pushes directly). Candidate: contact-details-extractor in Prospecting & Data Enrichment (another Apify actor PR already pending there). Low odds.
6. marketingtoolslist/awesome-marketing (484★) – "send a PR, put it alphabetically"; has Technical SEO / On-Page SEO / Competitor Analysis sections; last merges Aug 2025 (slow). Candidate: broken-link-checker in Technical SEO.
7. YuzeHao2023/Awesome-MCP-Servers (1.1k★) – categories incl. Research & Data, Search & Web; open-source servers. Candidate: tinyrex-mcp (repo is MIT). Merges are rare.
8. punkpeye/awesome-mcp-servers – tinyrex-mcp now qualifies (open-source repo), but this account already has 3 open PRs there (mesh2cad, behave, usb-rea from other projects). Wait until one is merged before adding a 4th (D10).
9. Germey/AwesomeWebScraping (265★) – has web_services.md "Web data extraction services" (a PR adding four Apify actors is pending). Follows lorien CONTRIBUTING, which restricts services → only one entry, if at all.
10. Lead-Orchestra/awesome-b2b-leads (25★) – sections No-Code Scraping Tools / Enrichment; simple CONTRIBUTING; no merges visible since Dec 2025. Low priority.

Checked 16 Oct and NOT suitable: bmpi-dev/awesome-seo (SaaS only with industry recognition + 2 third-party refs), lukasz-madon/awesome-remote-job and tramcar/awesome-job-boards (job boards only), iAmCorey/awesome-indie-hacker-tools (indie-dev stack, Chinese), ScrapeRouter/awesome-scraping (open-source libraries), restyler/awesome-n8n (n8n nodes only), makegov/awesome-procurement-data (unmaintained).

# Prepared entries

## 1. jivoi/awesome-osint (best fit; CONTRIBUTING allows self-promo with up-front disclosure, one PR per entry, alphabetical)
Section: "Domain and IP Research", insert between `[StatsCrop]` and `[TinyScan]`:
* [Tech Stack Detector](https://apify.com/tinyrex/tech-stack-detector) - Bulk website technology lookup for lists of domains (7,600+ Wappalyzer-compatible fingerprints) plus email provider (MX), SPF senders and DMARC policy, exported as JSON/CSV.
PR title: Add Tech Stack Detector to Domain and IP Research
PR body: Adds https://apify.com/tinyrex/tech-stack-detector, a bulk technology profiler (CMS, e-commerce, analytics, CDN) that also reports MX provider, SPF senders and DMARC policy, useful for profiling many domains at once in OSINT/recon. Disclosure: I am the author of this tool. It is a paid hosted tool (about $4 per 1,000 domains, failed lookups free, Apify free tier covers a trial).

## 2. foxck016077/awesome-apify-actors (accepts PRs; format "Name by `user` - N runs"; prefers 10k+ lifetime runs -> submit only once runs grow)
Jobs:
- [Greenhouse / Lever / Ashby Jobs Scraper](https://apify.com/tinyrex/ats-jobs-scraper) by `tinyrex` - All open jobs from Greenhouse, Lever, Ashby, Personio, Teamtailor and Recruitee boards in one schema; auto-detects the ATS from a company website.
- [Workday Jobs Scraper](https://apify.com/tinyrex/workday-jobs-scraper) by `tinyrex` - All jobs from myworkdayjobs.com career sites with full descriptions and exact posting dates.
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
