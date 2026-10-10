#!/usr/bin/env python3
"""Static site generator for the TinyRex data tools guide site (GitHub Pages).
Usage: APIFY_TOKEN=... python3 build.py  -> regenerates ./docs from public tinyrex actors that have an entry in G.
To add an actor: add it to G below, rebuild, commit and push (see README "Rebuilding the site")."""
import json, os, re, html, datetime, urllib.request, shutil
from _product_landing import PRODUCTS, PREVIEW_CSV_NAME, restore_static, extra_public_actors, render_product_page
ROOT = os.path.dirname(os.path.abspath(__file__))
ACT = "/workspace/zarada/actors"
OUT = os.path.join(ROOT, "docs")
BASE = os.environ.get("SITE_BASE", "https://emirmrkaljevic.github.io/tinyrex-data-tools")
STORE = "https://apify.com/tinyrex/"
TODAY = datetime.date.today().isoformat()
E = html.escape

# Per-actor SEO copy. Each guide targets the long-tail phrases people actually search.
G = {
 "tech-stack-detector": dict(
  slug="bulk-tech-stack-lookup-wappalyzer-alternative",
  ptitle="Free Wappalyzer Alternative for Bulk Tech Stack Lookup (API + CSV)",
  h1="Bulk tech stack lookup: a Wappalyzer / BuiltWith alternative for thousands of domains",
  desc="Check which CMS, e-commerce platform, analytics and email provider thousands of websites use. Bulk Wappalyzer alternative with API, CSV export and MCP.",
  kw=["free wappalyzer alternative bulk","builtwith alternative","bulk tech stack lookup","find all shopify stores from a domain list","detect website technology api"],
  short="Detect 7,600+ technologies (CMS, Shopify, WooCommerce, analytics, CDN) plus email provider, SPF senders and DMARC for thousands of domains.",
  price="about $4 per 1,000 analyzed domains; unreachable, blocked and timed-out domains are free",
  intro=["Wappalyzer's browser extension is great for one site at a time, but checking a list of 5,000 prospects by hand is not realistic, and bulk plans of BuiltWith-style tools are expensive. This guide shows how to run a bulk tech stack lookup over any domain list and get one clean JSON or CSV row per domain.",
         "It uses an open-source, Wappalyzer-compatible fingerprint database (7,600+ technologies) and also tells you each company's email provider (Google Workspace, Microsoft 365...), the SaaS tools in its SPF record and its DMARC policy."],
  steps=["Collect your domains (a CRM export, a list of competitors, a directory scrape). URLs and duplicates are normalized automatically.",
         "Optionally set <code>onlyIfUses</code> (e.g. <code>[\"Shopify\"]</code>) to keep only matching domains, which turns it into a lead filter.",
         "Run it from the Apify Console, the API, or an AI agent, then export the dataset as CSV/Excel/JSON."],
  faq=[("Is there a free Wappalyzer alternative for bulk lookups?","Apify's free plan includes monthly platform credit, which covers roughly a thousand domain lookups with this actor at about $4 per 1,000. Failed domains are not charged."),
       ("How do I find all Shopify stores in a list of domains?","Pass the list as <code>domains</code> and set <code>onlyIfUses</code> to <code>[\"Shopify\"]</code>. Non-matching domains are dropped (and charged at a much lower rate), so the dataset contains only Shopify stores."),
       ("Does it execute JavaScript?","No. It analyzes the homepage HTML, headers, cookies and script URLs over plain HTTP, which is why it is fast and cheap. Technologies detectable only through browser-side JavaScript may be missed.")]),
 "ats-jobs-scraper": dict(
  slug="scrape-greenhouse-lever-ashby-jobs",
  ptitle="Scrape Greenhouse, Lever & Ashby Jobs via API (Personio, Teamtailor, Recruitee too)",
  h1="How to scrape Greenhouse, Lever and Ashby jobs (plus Personio, Teamtailor, Recruitee)",
  desc="Get every open job from Greenhouse, Lever, Ashby, Personio, Teamtailor and Recruitee career pages as JSON/CSV. Auto-detects the ATS from a company website.",
  kw=["scrape greenhouse jobs api","lever jobs api","ashby job board api","personio jobs scraper","job postings dataset from career pages"],
  short="All open jobs from Greenhouse, Lever, Ashby, Personio, Teamtailor and Recruitee career pages in one normalized schema; auto-detects the ATS.",
  price="$1 per 1,000 jobs; companies without a supported ATS and filtered-out jobs are free",
  intro=["Greenhouse, Lever and Ashby all expose public job-board feeds, but each has a different URL scheme and schema, and you first need to know which ATS a company uses and what its board token is. Doing that for 200 companies by hand takes a day.",
         "This guide shows how to give a list of company websites (e.g. <code>stripe.com</code>) or board URLs and get every open job in one normalized dataset: title, department, locations, country, remote/hybrid, salary where published, posting date and description."],
  steps=["List companies as websites, careers URLs, board URLs or <code>ats:token</code> shortcuts like <code>personio:kb1</code>.",
         "Add title / location keywords and <code>postedWithinDays</code> to keep only relevant jobs (filtered jobs are free).",
         "Schedule it with monitoring mode on to receive only jobs that are new since the previous run."],
  faq=[("Does Greenhouse have a public jobs API?","Yes, Greenhouse's Job Board API (boards-api.greenhouse.io) is public for each company's board. The actor uses it and the equivalent official feeds of Lever, Ashby, Personio, Teamtailor and Recruitee, so no HTML scraping or login is involved."),
       ("How do I find which ATS a company uses?","Just pass the company website. The actor scans the site and careers pages for ATS links and checks the company name on each supported ATS."),
       ("Can I use it as a hiring signal for sales?","Yes. Monitoring mode returns only new jobs per run, which is a common trigger for outbound (e.g. companies hiring a first data engineer).")]),
 "shopify-products-scraper": dict(
  slug="export-shopify-store-products-to-csv",
  ptitle="Export Shopify Store Products to CSV (Any Store, Prices, Variants, Stock)",
  h1="How to export all products from any Shopify store to CSV or JSON",
  desc="Export products from any Shopify store (not just yours): prices, compare-at prices, variants, SKUs, stock and images to CSV, Excel or JSON. Price monitoring via API.",
  kw=["export shopify store products to csv","scrape shopify store products","shopify competitor price monitoring","shopify products.json all pages","download products from shopify store"],
  short="Products from any Shopify store: prices, discounts, variants, SKUs, stock and images, with price-change monitoring.",
  price="$0.70 per 1,000 products (+$0.50 per 1,000 for optional stock details)",
  intro=["Shopify's admin export only works for your own store. For competitor research, dropshipping catalogs or price monitoring you need the public product data of other stores, including every variant, the compare-at price and availability.",
         "This guide shows how to export the complete catalog of any Shopify store (or just one collection) to CSV or JSON in a single run, and how to schedule it to track price changes."],
  steps=["Add store domains or collection URLs to <code>stores</code> (custom domains work, headless stores too).",
         "Choose <code>outputMode</code>: one row per product or one row per variant (better for spreadsheets).",
         "Download as CSV/Excel, or schedule daily runs to monitor prices and discounts."],
  faq=[("Can I export products from a Shopify store that isn't mine?","Yes, as long as the products are publicly visible on the storefront. The actor reads the same public product data that the storefront serves to every visitor."),
       ("Why not just open /products.json?","It is paginated, limited to 250 items per page, omits some fields and is not available on every store. The actor handles pagination, collections, headless stores and normalization for you."),
       ("How do I monitor competitor prices?","Schedule the actor daily and compare <code>price</code> and <code>compareAtPrice</code> across runs; <code>onSale</code> and <code>discountPercent</code> are calculated for you.")]),
 "workday-jobs-scraper": dict(
  slug="scrape-workday-jobs-myworkdayjobs",
  ptitle="Workday Jobs Scraper: Export myworkdayjobs.com Jobs via API",
  h1="How to scrape jobs from Workday career sites (myworkdayjobs.com)",
  desc="Export all jobs from Workday career sites (myworkdayjobs.com) with full descriptions and exact posting dates to JSON or CSV. Works for many companies per run.",
  kw=["scrape workday jobs","myworkdayjobs api","workday job postings export","workday careers scraper python","fortune 500 jobs dataset"],
  short="Every job from Workday career sites (myworkdayjobs.com) with full descriptions, exact posting dates, locations and remote type.",
  price="$0.80 per 1,000 jobs with full descriptions; inputs without a Workday site are free",
  intro=["Most Fortune 500 companies, banks and pharma companies hire through Workday. Their career sites (<code>company.wd5.myworkdayjobs.com/...</code>) render with JavaScript and show relative dates like \"Posted 30+ days ago\", which makes them annoying to scrape.",
         "This guide shows how to pull every job from many Workday sites at once, with the full description and the exact posting date, using the same public job feed the career site loads in your browser."],
  steps=["Paste Workday career site URLs, or company websites (the actor finds the linked Workday site).",
         "Filter by title keywords, country codes, workplace type and <code>postedWithinDays</code>.",
         "Export to CSV/JSON or schedule it to receive new jobs every day."],
  faq=[("Does Workday have a public jobs API?","Each Workday career site loads its jobs from a public JSON endpoint. The actor uses that feed, so it needs no browser and no login."),
       ("Which companies use Workday?","Thousands of large employers such as NVIDIA, Salesforce and Intel. Pass a company website and the actor will detect a linked Workday site."),
       ("Do I get the full description?","Yes, full descriptions are included at the same price.")]),
 "woocommerce-products-scraper": dict(
  slug="export-woocommerce-store-products-to-csv",
  ptitle="Export WooCommerce Store Products to CSV (Prices, Variations, Stock)",
  h1="How to export products from any WooCommerce store to CSV or JSON",
  desc="Export products from any WooCommerce store: prices, sale prices, variations, SKUs, stock, categories and images to CSV, Excel or JSON. No API keys needed.",
  kw=["export woocommerce products from another store","scrape woocommerce store","woocommerce price monitoring competitor","woocommerce store api products","download woocommerce products csv"],
  short="Products from any WooCommerce store: prices, sale prices, variations, SKUs, stock, categories and images.",
  price="$0.60 per 1,000 products",
  intro=["WooCommerce's built-in exporter and REST API need admin keys, so they only work for your own shop. To analyse a competitor or build a supplier catalog you need the products the store already shows publicly.",
         "This guide shows how to export the complete public catalog of any WooCommerce store, including variations, regular vs sale price and stock status, to CSV or JSON, without API keys."],
  steps=["Add store URLs (homepage, shop page or category URL) to <code>stores</code>.",
         "Choose <code>outputMode</code> (products or variations) and optionally <code>onlyInStock</code>.",
         "Export as CSV/Excel or schedule it for price monitoring."],
  faq=[("Can I export products from someone else's WooCommerce store?","Yes, the publicly visible products. The actor reads the store's public storefront data; no admin access is involved."),
       ("Does it get variations?","Yes, with attributes, prices, SKUs and stock per variation."),
       ("What if the store isn't WooCommerce?","Run the Tech Stack Detector first to check, or use the Shopify Products Scraper for Shopify stores.")]),
 "ted-tenders-scraper": dict(
  slug="ted-tenders-api-export",
  ptitle="TED Tenders API Export: Download EU Public Tenders to CSV/JSON",
  h1="How to export EU public tenders from TED (Tenders Electronic Daily) to CSV or JSON",
  desc="Export EU public tenders and contract awards from TED by CPV code, country and deadline to CSV/JSON via the official TED API. Daily tender alerts, no coding required.",
  kw=["ted tenders api export","tenders electronic daily api","eu public procurement data csv","ted cpv code search export","eu tender alerts by cpv"],
  short="EU public tenders and contract awards from TED (official API): CPV, country, deadline, estimated and awarded value, winners.",
  price="$2.50 per 1,000 notices; already-seen notices in alert mode are free",
  intro=["TED (ted.europa.eu) publishes every EU/EEA public tender above the EU thresholds, but its search UI is slow for repeat work and its API returns deeply nested eForms data that is hard to use in a spreadsheet.",
         "This guide shows how to export tenders by CPV codes, countries and dates to flat CSV/JSON rows (buyer, CPV, deadline, value, winners, links to the PDF and documents), and how to turn it into a daily tender alert."],
  steps=["Pick CPV codes (e.g. <code>72000000</code> IT services) and buyer countries, or use keywords.",
         "Set <code>publishedWithinDays</code>, <code>noticeCategories</code> (competition/result/planning) and <code>onlyOpen</code>.",
         "Schedule daily with <i>Only new notices</i> on and connect it to email, Slack or a Google Sheet."],
  faq=[("Is there an official TED API?","Yes, the TED Search API (api.ted.europa.eu). The actor uses it, so there is no HTML scraping and no blocking, and flattens the results for you."),
       ("Can I get contract award winners?","Yes. Use <code>noticeCategories: [\"result\"]</code> to get awarded values, winners and award dates."),
       ("How do I get daily tender alerts?","Enable the only-new-notices option and create an Apify schedule; each run returns only notices you have not seen before.")]),
 "remote-jobs-scraper": dict(
  slug="remote-jobs-api-himalayas-remoteok-weworkremotely",
  ptitle="Remote Jobs API: Scrape Himalayas, Remote OK & We Work Remotely to CSV/JSON",
  h1="How to scrape remote jobs from Himalayas, Remote OK, We Work Remotely and more in one run",
  desc="Get remote jobs from Himalayas, Remote OK, We Work Remotely, Working Nomads and Arbeitnow as one deduplicated JSON/CSV dataset with salary, location rules and full descriptions.",
  kw=["remote jobs api","scrape remote ok jobs","himalayas jobs api","we work remotely scraper","remote jobs dataset csv"],
  short="Remote jobs from 5 boards (Himalayas, Remote OK, We Work Remotely, Working Nomads, Arbeitnow) in one deduplicated schema, with salary and location rules.",
  price="$0.80 per 1,000 jobs with full descriptions; filtered-out, duplicate and already-seen jobs are free",
  intro=["Remote job boards each have their own feed format: Himalayas has a search API, Remote OK a JSON feed, We Work Remotely and Working Nomads RSS, Arbeitnow a paged API. Combining them by hand means five parsers and a lot of duplicates, because the same job is often posted on several boards.",
         "This guide shows how to search all five boards by keyword in one run and get one clean, deduplicated dataset: title, company, who can apply (country and timezone restrictions), employment type, seniority, salary where published, tags and the full description."],
  steps=["Add job titles or skills to <code>keywords</code> (e.g. <code>python</code>, <code>customer support</code>), or leave it empty for the newest remote jobs.",
         "Filter by candidate <code>countries</code>, <code>publishedWithinDays</code>, employment type, seniority or only jobs with a salary (filtered jobs are free).",
         "Schedule it daily with <i>Only new jobs</i> on to build a remote job feed for a newsletter, Slack channel or job board."],
  faq=[("Is there a free remote jobs API?","Several boards publish free public feeds (Himalayas, Remote OK, We Work Remotely RSS, Arbeitnow). The actor reads those official feeds, merges them into one schema and removes duplicates, so you do not have to maintain five integrations."),
       ("Can I get only jobs open to candidates in my country?","Yes. Set <code>countries</code> (e.g. <code>[\"Germany\"]</code>) and choose whether to keep worldwide jobs with <code>includeWorldwide</code>."),
       ("Can I republish the jobs on my own site?","The boards ask for attribution and a link back to the original job; <code>url</code> and <code>sourceName</code> are included for that. Himalayas and Remote OK do not allow resubmitting their jobs to aggregators such as Google Jobs or LinkedIn.")]),
 "eu-grants-scraper": dict(
  slug="eu-funding-calls-horizon-europe-api",
  ptitle="EU Funding Calls API: Export Horizon Europe & EU Grants to CSV/JSON",
  h1="How to export open EU funding calls (Horizon Europe, Digital Europe, cascade funding) to CSV or JSON",
  desc="Export open and upcoming EU funding calls from the official EU Funding & Tenders Portal: deadlines, budgets, EU contribution per project and real status. Weekly grant alerts.",
  kw=["eu funding tenders portal api","horizon europe calls export","eu grants database csv","cascade funding open calls","eu grant alerts"],
  short="Open and upcoming EU funding calls (Horizon Europe, Digital Europe, LIFE, Erasmus+, cascade funding) with deadlines, budgets and real status.",
  price="$3 per 1,000 funding calls; filtered-out and already-seen calls are free",
  intro=["The EU Funding & Tenders Portal lists every Horizon Europe, Digital Europe, LIFE, Erasmus+ and CEF topic, but its search UI is slow for repeat work, exports are limited, and many calls flagged as <i>open</i> or <i>forthcoming</i> have deadlines that already passed (more than half in our tests).",
         "This guide shows how to export calls by programme, keyword and deadline window into flat rows (identifier, title, programme, opening date, deadlines, budget, expected grants, EU contribution per project, type of action, link), with the real status computed from the dates, and how to turn it into a weekly funding alert."],
  steps=["Pick <code>programmes</code> (e.g. <code>HORIZON</code>, <code>DIGITAL</code>) or leave empty for all, and add <code>keywords</code> such as <code>artificial intelligence</code>.",
         "Keep the default statuses (open + forthcoming) and optionally set <code>deadlineTo</code>.",
         "Schedule it weekly with <i>Only new calls</i> on and send new calls to email, Slack or a Google Sheet."],
  faq=[("Does the EU Funding & Tenders Portal have an API?","Yes, the portal's own search API. The actor uses it (no HTML scraping) and flattens budgets and deadlines into simple columns."),
       ("Why does the portal show expired calls as open?","Status flags on the portal are often not updated. The actor computes <code>status</code> from the opening date and deadlines and keeps the portal's flag as <code>portalStatus</code>."),
       ("What is cascade funding?","EU-funded projects re-grant part of their budget through their own open calls, often EUR 10k to 500k for SMEs and startups. These calls are included.")]),
 "rss-feed-scraper": dict(
  slug="rss-feed-to-json-csv-api",
  ptitle="RSS Feed to JSON/CSV: Bulk RSS & Atom Feed Reader API",
  h1="How to turn any RSS or Atom feed into JSON or CSV (bulk, with monitoring)",
  desc="Convert RSS, Atom and JSON feeds (or any website, feeds auto-discovered) to clean JSON/CSV: titles, links, dates, authors, full text, images and podcast enclosures.",
  kw=["rss to json","rss feed to csv","rss feed reader api","atom feed parser online","monitor rss feeds keywords"],
  short="Any RSS, Atom or JSON Feed, or a website with auto-discovered feeds, as clean JSON/CSV with keyword filters, dedupe and monitoring.",
  price="$0.30 per 1,000 feed items; failed feeds, filtered, duplicate and already-seen items are free",
  intro=["RSS and Atom are still the cheapest way to follow news sites, blogs, podcasts, YouTube channels and changelogs, but every feed is slightly different: RSS 2.0, RDF, Atom, JSON Feed, HTML inside descriptions, emails in author fields, missing dates. Most online RSS-to-JSON converters handle one feed at a time.",
         "This guide shows how to read hundreds of feeds in one run (or just paste website URLs and let the feeds be discovered), get one normalized row per item (title, link, publish date, author, summary, full text, image, categories, enclosure), filter by keywords and date, and receive only new items on a schedule."],
  steps=["Add <code>feeds</code>: feed URLs or plain website URLs (the actor finds their feeds).",
         "Optionally set <code>keywords</code>, <code>excludeKeywords</code> and <code>publishedWithinDays</code>.",
         "Schedule it with <i>Only new items</i> on and send new items to Slack, email, a Google Sheet or an LLM summary."],
  faq=[("Can I convert RSS to JSON for free?","Apify's free plan includes monthly platform credit, which covers thousands of feed items at $0.30 per 1,000. Feeds that fail are not charged."),
       ("Does it find the feed if I only have the website?","Yes. It reads the site's feed links and tries the common feed paths (/feed, /rss, /atom.xml and others)."),
       ("Does it work for podcasts and YouTube?","Yes. Podcast enclosures (audio URL, length, type, duration) and YouTube channel feeds are supported.")]),
 "sitemap-scraper": dict(
  slug="extract-all-urls-from-sitemap",
  ptitle="Extract All URLs from a Sitemap to CSV (+ Broken Link Check)",
  h1="How to extract all URLs from a website's sitemap (and find broken links)",
  desc="Get every URL from any website's XML sitemaps as CSV or JSON: auto-discovery via robots.txt, sitemap indexes, .gz, lastmod, images, hreflang, plus an optional HTTP status check.",
  kw=["extract urls from sitemap","sitemap to csv","get all urls of a website","sitemap url extractor","find broken links in sitemap"],
  short="Every URL from any website's XML sitemaps (robots.txt discovery, indexes, .gz) with lastmod, images and hreflang, plus optional status/redirect check.",
  price="$0.20 per 1,000 URLs ($0.50 per 1,000 status checks); sites without a sitemap are free",
  intro=["Sitemaps are the fastest way to get a complete list of a website's pages: no crawling, no guessing. But big sites split them into sitemap indexes, gzip files and image or news sitemaps, and online sitemap viewers stop after a few hundred URLs.",
         "This guide shows how to turn the sitemaps of one or hundreds of websites into a flat table (URL, lastmod, change frequency, priority, images, hreflang alternates), filter it by URL pattern or date, optionally check the HTTP status of every URL to find broken and redirected pages, and get only new URLs on a schedule."],
  steps=["Add <code>startUrls</code>: domains, sitemap URLs or robots.txt URLs. Sitemaps are discovered from robots.txt and common paths.",
         "Optionally filter with <code>includeUrlPatterns</code> (e.g. <code>/blog/</code>) and <code>lastModifiedWithinDays</code>.",
         "Turn on <code>checkStatus</code> for a broken link and redirect audit, or <i>Only new URLs</i> to monitor a competitor's new pages."],
  faq=[("How do I get all URLs of a website?","If the site has a sitemap (most do), reading it is the fastest and most complete way. Enter the domain; the actor finds the sitemaps through robots.txt and the usual paths and follows sitemap indexes."),
       ("Can it find broken links in my sitemap?","Yes. With <code>checkStatus</code> every URL is requested once and you get the status code, final status after redirects and the redirect chain. Filter for 4xx/5xx to find pages that should not be in the sitemap."),
       ("What if a site has no sitemap?","It is reported in the SITES record and costs nothing. Use a crawler for sites without sitemaps.")]),
}

# Use-case tutorials (long-tail "how to get X into a spreadsheet" searches). Rendered only when the actor is public.
SHEETS_STEPS = ["To get the rows into Google Sheets: download the run's dataset as CSV and import it, or, for automatic updates, add an integration on the actor's <i>Integrations</i> tab (Apify's Google Sheets Import &amp; Export actor, Make, Zapier or n8n) so every finished run appends its rows to your sheet.",
                "Alternatively, in Google Sheets use <code>=IMPORTDATA(\"https://api.apify.com/v2/acts/{tid}/runs/last/dataset/items?format=csv&amp;status=SUCCEEDED&amp;token=YOUR_TOKEN\")</code>. Anyone with edit access to the sheet can see the token, so only do this in private sheets (or use a scoped token).",
                "Add a <i>Schedule</i> in Apify (daily or weekly) so the sheet stays fresh."]
UC = [
 dict(slug="shopify-products-to-google-sheets", actor="shopify-products-scraper",
  ptitle="How to Export Shopify Products to Google Sheets (Prices, Stock, Variants)",
  h1="How to get any Shopify store's products into Google Sheets (and keep prices updated)",
  desc="Step-by-step: export all products, variants, prices and stock of any Shopify store to Google Sheets or Excel, and refresh them daily for price monitoring.",
  intro=["Competitor price tracking, dropshipping research and catalog migrations all start with the same table: every product of a Shopify store with its variants, SKUs, prices, compare-at prices and stock. Copying it by hand stops working after 20 products.",
         "Most Shopify stores expose their public catalog in a structured way, so you can get the whole catalog in seconds without a browser. Here is how to get it into a spreadsheet and keep it updated."],
  input={"stores": ["https://www.allbirds.com"], "maxProductsPerStore": 500},
  steps=["Open the Shopify Products Scraper, paste one or more store URLs into <code>stores</code> and run it.", "@SHEETS", "To track price changes, turn on the monitoring option so each run only returns changed products."],
  faq=[("Does this need access to the store's admin?","No. It only reads the public catalog that any visitor can see."),
       ("Can I get one row per variant?","Yes, every variant (size, color) with its own SKU, price and availability is included.")]),
 dict(slug="find-shopify-stores-from-domain-list", actor="tech-stack-detector",
  ptitle="How to Find Which Websites Use Shopify in a List of Domains (Free Tool)",
  h1="How to find which websites in a list use Shopify, WooCommerce or HubSpot",
  desc="Filter a list of thousands of domains down to the ones that use Shopify, WooCommerce, HubSpot or any of 7,600+ technologies. CSV in, CSV out, about $4 per 1,000 domains.",
  intro=["Agencies, app developers and SaaS sales teams often have a list of domains (from a CRM, a trade show, a directory) and need to know which of them run on a specific platform. Opening each site with a browser extension does not scale.",
         "A bulk technology lookup answers it in minutes: give it the list, tell it which technology you care about, and keep only the matches."],
  input={"domains": ["allbirds.com", "gymshark.com", "wordpress.org", "example.com"], "onlyIfUses": ["Shopify"]},
  steps=["Paste your domains into <code>domains</code> (URLs and duplicates are cleaned up automatically).", "Set <code>onlyIfUses</code> to <code>[\"Shopify\"]</code> (or WooCommerce, HubSpot, Klaviyo...). Non-matching domains are not saved.", "@SHEETS"],
  faq=[("How accurate is it?","It uses an open-source Wappalyzer-compatible fingerprint database and checks the HTML, headers, cookies and scripts of each homepage. Platforms like Shopify and WooCommerce are detected very reliably."),
       ("What does it cost?","About $4 per 1,000 analyzed domains; unreachable domains are free.")]),
 dict(slug="eu-tender-alerts-google-sheets-slack", actor="ted-tenders-scraper",
  ptitle="Free EU Tender Alerts: New TED Tenders to Google Sheets, Email or Slack",
  h1="How to get daily alerts for new EU public tenders (TED) by CPV code and country",
  desc="Set up daily alerts for new EU public tenders from TED, filtered by CPV code, country and keywords, delivered to Google Sheets, email or Slack. Official TED API, $2.50 per 1,000 notices.",
  intro=["Paid tender alert services cost hundreds of euros per year, yet the underlying data, TED (Tenders Electronic Daily), is the EU's official open data. With a scheduled run you get only new notices that match your CPV codes, countries and keywords.",
         "This tutorial sets up a daily alert in about five minutes."],
  input={"cpvCodes": ["72000000"], "countries": ["DE", "AT"], "publishedWithinDays": 1, "onlyNew": True},
  steps=["Open the TED Tenders Scraper and set your CPV codes (e.g. <code>72000000</code> for IT services), buyer countries and optional keywords.", "Turn on the <i>only new notices</i> mode so each run returns only notices you have not seen.", "Create a daily Schedule, then add an integration: Google Sheets, email or Slack (Integrations tab of the actor or task).", "@SHEETS"],
  faq=[("Is TED data free to reuse?","Yes, TED is official EU open data published by the Publications Office of the EU and may be reused, including commercially, with attribution."),
       ("What is a CPV code?","The EU's Common Procurement Vocabulary: an 8-digit code for what is being bought, e.g. 45000000 construction work or 72000000 IT services.")]),
 dict(slug="remote-jobs-to-google-sheets", actor="remote-jobs-scraper",
  ptitle="How to Get Remote Job Listings into a Spreadsheet (5 Job Boards, Daily)",
  h1="How to get remote job listings from 5 job boards into one spreadsheet",
  desc="Collect remote jobs from Himalayas, Remote OK, We Work Remotely, Working Nomads and Arbeitnow into Google Sheets or CSV daily, deduplicated, with salary and location rules.",
  intro=["Job seekers, recruiters and job board owners all end up checking the same five remote job boards every day. A single deduplicated table with title, company, salary, location restrictions and the full description saves that time and makes filtering easy.",
         "The data comes from the boards' official public APIs and RSS feeds."],
  input={"keywords": ["python", "data engineer"], "maxResultsPerSearch": 300, "onlyNewJobs": True},
  steps=["Open the Remote Jobs Scraper, add keywords (or leave empty for everything) and pick the boards.", "Turn on the option for only new jobs if you schedule it daily.", "@SHEETS"],
  faq=[("Are duplicates removed?","Yes, the same job posted on several boards appears once."),
       ("Do I get salaries?","When the board publishes them, yes, as min/max/currency columns.")]),
 dict(slug="rss-feeds-to-google-sheets-slack", actor="rss-feed-scraper",
  ptitle="RSS to Google Sheets or Slack: Monitor Many Feeds with Keywords",
  h1="How to send new items from many RSS feeds to Google Sheets or Slack (with keyword filters)",
  desc="Monitor dozens of RSS, Atom or JSON feeds, keep only items matching your keywords, and send new items to Google Sheets or Slack on a schedule. $0.30 per 1,000 items.",
  intro=["Google Sheets' IMPORTFEED handles one feed at a time and breaks easily, and most RSS-to-Slack tools charge per feed. If you follow 30 company blogs, changelogs or industry news sources, you want one deduplicated stream filtered by your keywords.",
         "Here is how to set that up with a scheduled run."],
  input={"feeds": ["https://blog.cloudflare.com/rss/", "https://github.com/apify/crawlee/releases.atom", "https://www.nasa.gov/feed/"], "keywords": ["ai", "release"], "onlyNewItems": True},
  steps=["Paste feed URLs or plain website URLs into <code>feeds</code> (feeds are discovered automatically).", "Add <code>keywords</code> and turn on <i>Only new items</i>.", "Schedule it hourly or daily and add the Slack or Google Sheets integration.", "@SHEETS"],
  faq=[("Can I use any feed?","Technically yes, but check each publisher's terms: some news feeds allow only personal, non-commercial use."),
       ("Does it get the full article?","It returns the full text when the feed includes it; it does not open article pages.")]),
 dict(slug="find-broken-links-in-sitemap", actor="sitemap-scraper",
  ptitle="How to Find Broken Links and Redirects in Your Sitemap (Free Check)",
  h1="How to find broken pages and redirects in your XML sitemap",
  desc="Check every URL in your XML sitemap for 404s, 5xx errors and redirects, and export the results to CSV. Works for sitemap indexes and large sites. $0.50 per 1,000 checked URLs.",
  intro=["Search engines expect a sitemap to list only live, canonical URLs. After migrations or product deletions, sitemaps often contain 404s and redirected URLs, which waste crawl budget and show up as errors in Search Console.",
         "This tutorial checks every URL in a sitemap and gives you a CSV of the problems."],
  input={"startUrls": ["https://crawlee.dev"], "checkStatus": True, "maxUrlsPerSite": 5000},
  steps=["Open the Sitemap Scraper and enter your domain (or the sitemap URL).", "Turn on <code>checkStatus</code>. URLs disallowed by robots.txt are skipped by default.", "Run it, then filter the dataset for <code>finalStatusCode</code> 400 and above, or rows with a non-empty <code>redirectChain</code>.", "@SHEETS"],
  faq=[("Will it overload my server?","No. It sends one request per URL with low concurrency per site (3 by default, adjustable)."),
       ("Does it crawl links on the pages?","No, it checks only the URLs listed in the sitemap.")]),
]

def tutorial(t, a, actors):
    store = STORE + a["name"]; tid = f"tinyrex~{a['name']}"
    steps = []
    for st in t["steps"]:
        steps += [x.replace("{tid}", tid) for x in SHEETS_STEPS] if st == "@SHEETS" else [st]
    inp = json.dumps(t["input"], indent=2)
    faq = "".join(f"<h3>{E(q)}</h3><p>{ans}</p>" for q, ans in t["faq"])
    body = f"""<h1>{E(t['h1'])}</h1>
<p class="mut">Updated {TODAY} · Tool: <a href="{store}">{E(a['title'])}</a> · {E(a['price'])}</p>
{''.join(f'<p>{p}</p>' for p in t['intro'])}
<a class="cta" href="{store}">Open the tool on Apify →</a>
<h2>Step by step</h2><ol>{''.join(f'<li>{x}</li>' for x in steps)}</ol>
<h2>Example input</h2>{code(inp,'json')}
<p>Same thing from the command line (returns CSV directly):</p>{code(f"curl -X POST 'https://api.apify.com/v2/acts/{tid}/run-sync-get-dataset-items?format=csv' -H 'Authorization: Bearer $APIFY_TOKEN' -H 'Content-Type: application/json' -d '{json.dumps(t['input'])}' > results.csv",'bash')}
<p>More code examples (Python, JavaScript, MCP for AI agents) are in the <a href="../{a['slug']}/">full guide</a>.</p>
<h2>FAQ</h2>{faq}
<a class="cta" href="{store}">Try it on Apify →</a>"""
    ld = [{"@context": "https://schema.org", "@type": "HowTo", "name": t["h1"], "description": t["desc"], "step": [{"@type": "HowToStep", "position": i+1, "text": re.sub('<[^>]+>', '', x)} for i, x in enumerate(steps)]},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', ans)}} for q, ans in t["faq"]]}]
    return page(f"{t['slug']}/", t["ptitle"], t["desc"], body, ld)

PRIVATE_KEYS = re.compile(r"(email|phone|telefon|contact|kontakt|fax)", re.I)

def trim(v, depth=0):
    if isinstance(v, dict):
        return {k: trim(x, depth+1) for k, x in v.items() if not PRIVATE_KEYS.search(k)}
    if isinstance(v, list):
        t = [trim(x, depth+1) for x in v[:3]]
        return t + (["..."] if len(v) > 3 else [])
    if isinstance(v, str) and len(v) > 220:
        return v[:220] + "..."
    return v

def load_actors():
    tok = os.environ["APIFY_TOKEN"]
    req = urllib.request.Request("https://api.apify.com/v2/acts?my=1&limit=100", headers={"Authorization": f"Bearer {tok}"})
    items = json.load(urllib.request.urlopen(req))["data"]["items"]
    res = []
    for it in items:
        n = it["name"]
        req = urllib.request.Request(f"https://api.apify.com/v2/acts/tinyrex~{n}", headers={"Authorization": f"Bearer {tok}"})
        d = json.load(urllib.request.urlopen(req))["data"]
        if not d.get("isPublic") or n not in G:
            continue  # only published actors that have a written guide
        readme = open(f"{ACT}/{n}/README.md").read()
        m = re.findall(r"```json\n(.*?)```", readme, re.S)
        sample = json.load(open(f"{ACT}/{n}/sample-output.json"))
        res.append(dict(name=n, title=d["title"], input=json.loads(m[0]), sample=trim(sample[0] if isinstance(sample, list) else sample), **G[n]))
    order = list(G)
    return sorted(res, key=lambda a: order.index(a["name"]))

CSS = """:root{--fg:#1d2330;--mut:#5b6474;--acc:#0b7a4b;--bg:#fff;--code:#f4f6f8}*{box-sizing:border-box}body{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
header,main,footer{max-width:860px;margin:0 auto;padding:0 20px}header{display:flex;align-items:center;gap:12px;padding-top:18px}header a{color:var(--fg);text-decoration:none;font-weight:700}
h1{font-size:2rem;line-height:1.25;margin:.8em 0 .4em}h2{margin-top:1.8em}a{color:var(--acc)}code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:.9em}
pre{background:#0f1720;color:#e6edf3;padding:14px;border-radius:8px;overflow:auto;font-size:.82rem;line-height:1.45}pre code{background:none;padding:0}
.cta{display:inline-block;background:var(--acc);color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:600;margin:8px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}.card{border:1px solid #e3e7ec;border-radius:10px;padding:16px}.card h3{margin:0 0 6px;font-size:1.05rem}
.mut{color:var(--mut)}footer{margin-top:60px;padding:20px;border-top:1px solid #e3e7ec;color:var(--mut);font-size:.9rem}details{margin:6px 0}
.cta.sec{background:#fff;color:var(--acc);border:2px solid var(--acc)}.cta.row{margin-right:10px}
table.sample{width:100%;border-collapse:collapse;font-size:.9rem;margin:1em 0}table.sample th,table.sample td{border:1px solid #e3e7ec;padding:8px 10px;text-align:left;vertical-align:top}table.sample th{background:var(--code)}
.pricebox{border:1px solid #e3e7ec;border-radius:10px;padding:16px;margin:12px 0}"""

def page(path, title, desc, body, ld=None):
    url = f"{BASE}/{path}"
    ldj = f'<script type="application/ld+json">{json.dumps(ld)}</script>' if ld else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{url}">
<link rel="stylesheet" href="{'../' if path else ''}style.css">{ldj}</head><body>
<header><a href="{'../' if path else './'}">🦖 TinyRex Data Tools</a><span class="mut">practical guides for web data APIs</span></header>
<main>{body}</main>
<footer>TinyRex Data Tools. Guides and examples for <a href="https://apify.com/tinyrex">TinyRex actors on Apify</a>. Only public data; respect each site's terms. Source on <a href="https://github.com/emirmrkaljevic/tinyrex-data-tools">GitHub</a>.</footer></body></html>"""

def code(s, lang=""):
    return f'<pre><code class="language-{lang}">{E(s)}</code></pre>'

def guide(a, actors):
    aid = f"tinyrex/{a['name']}"; tid = f"tinyrex~{a['name']}"; store = STORE + a["name"]
    inp = json.dumps(a["input"], indent=2, ensure_ascii=False)
    py = f'''from apify_client import ApifyClient  # pip install apify-client

client = ApifyClient("<YOUR_APIFY_TOKEN>")
run_input = {inp}
run = client.actor("{aid}").call(run_input=run_input)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)'''
    js = f'''import {{ ApifyClient }} from 'apify-client'; // npm i apify-client

const client = new ApifyClient({{ token: process.env.APIFY_TOKEN }});
const run = await client.actor('{aid}').call({inp});
const {{ items }} = await client.dataset(run.defaultDatasetId).listItems();
console.log(items);'''
    curl = f'''# Runs the actor and returns the results directly (CSV here; use format=json for JSON)
curl -X POST "https://api.apify.com/v2/acts/{tid}/run-sync-get-dataset-items?format=csv" \\
  -H "Authorization: Bearer $APIFY_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(a["input"], ensure_ascii=False)}' > results.csv'''
    mcp = json.dumps({"mcpServers": {"apify": {"url": f"https://mcp.apify.com?tools={aid}", "headers": {"Authorization": "Bearer <YOUR_APIFY_TOKEN>"}}}}, indent=2)
    others = "".join(f'<li><a href="../{o["slug"]}/">{E(o["h1"])}</a></li>' for o in actors if o is not a)
    faq = "".join(f"<h3>{E(q)}</h3><p>{ans}</p>" for q, ans in a["faq"])
    body = f"""<h1>{E(a['h1'])}</h1>
<p class="mut">Updated {TODAY} · Tool used: <a href="{store}">{E(a['title'])}</a> on Apify · Price: {E(a['price'])}</p>
{''.join(f'<p>{p}</p>' for p in a['intro'])}
<a class="cta" href="{store}">Open {E(a['title'].split(' - ')[0].split(':')[0])} on Apify →</a>
<h2>Steps</h2><ol>{''.join(f'<li>{s}</li>' for s in a['steps'])}</ol>
<h2>Example input</h2>{code(inp,'json')}
<h2>Example output (one item, shortened)</h2>{code(json.dumps(a['sample'], indent=2, ensure_ascii=False),'json')}
<p>Every run's dataset can be downloaded as JSON, CSV, Excel, XML or HTML from the Apify Console, or via <code>https://api.apify.com/v2/datasets/&lt;datasetId&gt;/items?format=csv</code>.</p>
<h2>Run it from code</h2><h3>Python</h3>{code(py,'python')}<h3>JavaScript / Node.js</h3>{code(js,'javascript')}<h3>curl (no SDK)</h3>{code(curl,'bash')}
<p>Get your API token in Apify Console → Settings → API &amp; Integrations. The free Apify plan includes monthly credit that is enough to try this.</p>
<h2>Use it from an AI agent (MCP)</h2>
<p>The <a href="https://mcp.apify.com">Apify MCP server</a> exposes this actor as a tool for Claude, Cursor, VS Code, n8n and other MCP clients. Add this to your client's MCP config (or use the OAuth flow at mcp.apify.com instead of a token):</p>{code(mcp,'json')}
<p>Then ask in plain language, e.g. <i>"{E(a['kw'][0].capitalize())} for this list and give me a table"</i>.</p>
<h2>Pricing</h2><p>Pay per result: {E(a['price'])}. You can cap the cost of every run in the run options.</p>
<h2>FAQ</h2>{faq}
<a class="cta" href="{store}">Try it on Apify →</a>
<h2>More guides</h2><ul>{others}</ul>"""
    ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": a["h1"], "description": a["desc"], "dateModified": TODAY, "keywords": ", ".join(a["kw"]), "about": {"@type": "SoftwareApplication", "name": a["title"], "url": store, "applicationCategory": "DeveloperApplication", "operatingSystem": "Web"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', ans)}} for q, ans in a["faq"]]}]
    return page(f"{a['slug']}/", a["ptitle"], a["desc"], body, ld)

def index(actors, tuts=()):
    cards = "".join(f'<div class="card"><h3><a href="{a["slug"]}/">{E(a["title"].split(" - ")[0])}</a></h3><p>{E(a["short"])}</p><p class="mut">{E(a["price"])}</p><p><a href="{a["slug"]}/">Guide</a> · <a href="{STORE}{a["name"]}">Apify Store</a></p></div>' for a in actors)
    body = f"""<h1>Practical guides for pulling clean data from the web</h1>
<p>TinyRex builds small, cheap, API-first data tools on <a href="https://apify.com/tinyrex">Apify</a>: bulk tech stack lookup, job postings from ATS and remote job boards, e-commerce product catalogs, RSS feeds, website sitemaps, EU public tenders and EU funding calls. Every tool returns clean JSON/CSV, charges only per delivered result, and works from Python, JavaScript, plain HTTP, no-code tools and AI agents (via the Apify MCP server).</p>
<p>Each guide below has a working example input, real sample output and copy-paste code.</p>
<div class="cards">{cards}</div>
{('<h2>Tutorials</h2><ul>' + ''.join(f'<li><a href="{t["slug"]}/">{E(t["h1"])}</a></li>' for t in tuts) + '</ul>') if tuts else ''}
{('<h2>Data products</h2><ul>' + ''.join(f'<li><a href="{p["slug"]}/">{E(p["h1"])}</a> — free preview + weekly Excel on Gumroad</li>' for p in PRODUCTS) + '</ul>') if PRODUCTS else ''}
<h2>Use any of these tools from an AI agent</h2>
<p>Connect Claude, Cursor or n8n to <code>https://mcp.apify.com?tools={','.join('tinyrex/'+a['name'] for a in actors)}</code> and the agent can call every tool above directly.</p>"""
    ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i+1, "url": f"{BASE}/{a['slug']}/", "name": a["title"]} for i, a in enumerate(actors)]}
    return page("", "TinyRex Data Tools: Web Data APIs & Scraper Guides (Jobs, E-commerce, Tenders)", "Guides with working examples for bulk tech stack lookup, Greenhouse/Workday and remote job APIs, Shopify/WooCommerce product export, RSS feeds, sitemaps, TED EU tenders and EU grants.", body, ld)

def main():
    actors = load_actors()
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    def w(path, s):
        full = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
        open(full, "w").write(s)
    by = {a["name"]: a for a in actors}
    try:
        for name, info in extra_public_actors(os.environ["APIFY_TOKEN"]).items():
            if name not in by:
                by[name] = info
    except Exception as ex:
        print("warn: could not list extra public actors:", ex)
    tuts = [t for t in UC if t["actor"] in by and by[t["actor"]].get("slug")]
    restore_static(OUT)  # CSV + logos + IndexNow before product pages that read the CSV
    w("index.html", index(actors, tuts)); w("style.css", CSS); w(".nojekyll", "")
    for a in actors:
        w(f"{a['slug']}/index.html", guide(a, actors))
    for t in tuts:
        w(f"{t['slug']}/index.html", tutorial(t, by[t["actor"]], actors))
    for prod in PRODUCTS:
        w(f"{prod['slug']}/index.html", render_product_page(prod, by, OUT, page, STORE, TODAY, E))
    urls = ([f"{BASE}/"]
            + [f"{BASE}/{a['slug']}/" for a in actors]
            + [f"{BASE}/{t['slug']}/" for t in tuts]
            + [f"{BASE}/{prod['slug']}/" for prod in PRODUCTS]
            + [f"{BASE}/data/{PREVIEW_CSV_NAME}"])
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    w("404.html", page("", "Page not found | TinyRex Data Tools", "Page not found",
                       '<h1>Page not found</h1><p><a href="./">Back to all guides</a></p>')
               .replace('href="style.css"', f'href="{BASE}/style.css"'))
    pages = [{"name": a["name"], "slug": a["slug"], "url": f"{BASE}/{a['slug']}/"} for a in actors]
    pages += [{"name": prod["slug"], "slug": prod["slug"], "url": f"{BASE}/{prod['slug']}/", "type": "product"} for prod in PRODUCTS]
    json.dump(pages, open(os.path.join(ROOT, "pages.json"), "w"), indent=1)
    print("built", len(actors), "guides:", [a["slug"] for a in actors],
          "tutorials:", [t["slug"] for t in tuts], "products:", [prod["slug"] for prod in PRODUCTS])

if __name__ == "__main__":
    main()
