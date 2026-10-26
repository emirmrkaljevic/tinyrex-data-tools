#!/usr/bin/env python3
"""Static site generator for the TinyRex data tools guide site (GitHub Pages).
Usage: APIFY_TOKEN=... python3 build.py  -> regenerates ./docs from public tinyrex actors that have an entry in G.
To add an actor: add it to G below, rebuild, commit and push (see README "Rebuilding the site")."""
import json, os, re, html, datetime, urllib.request, shutil
from _country_pages import country_pages, render_country_page
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
 "contact-details-extractor": dict(
  slug="extract-emails-socials-from-domain-list",
  ptitle="Contact Info Scraper Alternative: Extract Emails, Phones & Socials from a Domain List",
  h1="How to extract emails, phone numbers and social links from a list of company domains",
  desc="Bulk-enrich a list of company websites with public emails (role vs personal flags), phones, LinkedIn/X/Facebook links and addresses. CSV in, CSV out, ~$2 per 1,000 domains with a contact; empty domains are free.",
  kw=["contact info scraper alternative","extract emails from list of websites","bulk email finder from domains","scrape contact details from website","get linkedin company page from domain"],
  short="Public emails (role/personal flags), phones, LinkedIn/X/Facebook/Instagram/YouTube/GitHub/TikTok links and addresses for a list of company domains.",
  price="about $2 per 1,000 domains with a contact found; domains with no contact, unreachable or blocked hosts are free",
  input={"domains": ["apify.com", "example.com"], "maxPagesPerDomain": 8, "respectRobotsTxt": True},
  intro=["You already have the companies (a CRM export, a trade-show list, the output of a tech stack lookup), and now you need a way to reach them: the public info@ or sales@ inbox, a phone number and the LinkedIn company page. Opening 500 websites and hunting for the contact page by hand takes days, and many contact info scrapers charge per page or per result even when nothing is found.",
         "This guide shows how to give a list of domains and get one clean row per company: emails tagged as role/generic (info@, sales@) or personal-looking (first.last@), phones, social profiles, postal addresses and the page each value came from. It reads only the homepage and contact/about/impressum pages on the same host, respects robots.txt and needs no login or browser."],
  steps=["Paste your company domains or URLs into <code>domains</code> (one per line; URLs and duplicates are normalized).",
         "Optionally raise <code>maxPagesPerDomain</code> (default 8) for sites with deep contact pages, and keep <code>respectRobotsTxt</code> on.",
         "Run it, then filter the dataset on <code>hasContact</code> and <code>emails.roleOrGeneric</code> and export as CSV/Excel, or schedule it to refresh contact data monthly."],
  faq=[("Is this an alternative to the popular contact info scrapers?","Yes, for the common case where you already know the company websites. It does not crawl search engines or directories; it visits only the homepage and contact-looking pages of each domain you give it, which keeps it fast and cheap. You pay about $0.002 per domain where at least one contact was found, and nothing for domains without contacts or that fail."),
       ("How do I find the email address of a company from its website?","Most companies publish a role inbox (info@, hello@, sales@) on the homepage footer, contact page or impressum. The actor collects every mailto link and on-page address from those pages and flags which ones are role/generic, so you can pick the right inbox per company."),
       ("Can I get the LinkedIn company page for a list of domains?","Yes. Social links the company itself puts on its site (LinkedIn, X/Twitter, Facebook, Instagram, YouTube, GitHub, TikTok) are returned in the <code>socials</code> object, one column per network in the CSV export."),
       ("Is it GDPR compliant?","Emails and phone numbers can be personal data. You decide the purpose and act as the controller; the <code>personalLooking</code> flag helps you keep only role/generic addresses for outreach. Check the email-marketing rules of each recipient's country before contacting anyone.")]),
 "bulk-website-screenshot": dict(
  slug="bulk-website-screenshots-to-csv-google-drive",
  ptitle="Bulk Website Screenshots from a URL List to CSV or Google Drive (Full Page, Mobile)",
  h1="How to take bulk website screenshots from a URL list and save them to CSV or Google Drive",
  desc="Screenshot hundreds of URLs in one run: full-page or viewport PNG/JPEG, desktop or mobile, cookie banners hidden. Get a CSV with image links and send the files to Google Drive. $2 per 1,000 screenshots; failed pages are free.",
  kw=["bulk website screenshots","screenshot list of urls","full page screenshot api","website screenshots to google drive","mobile screenshots of many websites"],
  short="Full-page or viewport PNG/JPEG screenshots for a list of URLs on desktop, laptop, tablet or mobile, with cookie banners hidden and one CSV row per page.",
  price="$0.002 per saved screenshot ($2 per 1,000), no compute fees on top; unreachable pages, timeouts and HTTP errors are free",
  input={"urls": ["https://example.com", "https://apify.com"], "fullPage": True, "device": "desktop", "format": "jpeg", "jpegQuality": 80, "hideCookieBanners": True},
  intro=["Agencies archiving client pages before a redesign, SEO teams documenting a migration, and sales teams adding a homepage thumbnail to every lead all need the same thing: a screenshot of each page in a list. Browser extensions do one tab at a time, and many screenshot APIs bill every request, including the ones that time out or return a 404.",
         "This guide shows how to paste a list of URLs (or a whole sitemap), get one PNG or JPEG per page in a single run, and end up with a CSV where every row has the status code, page title, final URL after redirects and a direct <code>screenshotUrl</code>. It also shows how to move the images into Google Drive automatically, so they outlive the run storage."],
  steps=["Paste your pages into <code>urls</code>, one per line. Bare domains like <code>example.com</code> work, and duplicates are removed. To capture a whole site, run the <a href=\"https://apify.com/tinyrex/sitemap-scraper\">Sitemap Scraper</a> first and feed its <code>url</code> column in.",
         "Choose <code>fullPage</code> (scrolls once so lazy images load, capped at <code>maxFullPageHeight</code>), a <code>device</code> (desktop, laptop, tablet, mobile or custom) and <code>png</code> or the 3-10x smaller <code>jpeg</code>.",
         "Run it and export the dataset as CSV or Excel: one row per URL with <code>statusCode</code>, <code>title</code>, <code>screenshotUrl</code> and <code>error</code>. Failed rows are listed but not charged.",
         "To keep the files in Google Drive, add a Make, Zapier or n8n scenario on the actor's <i>Integrations</i> tab that runs on success, downloads each <code>screenshotUrl</code> and uploads it to a Drive folder (the same works for Dropbox or S3). Images in run storage expire with your plan's retention (7 days on the free plan).",
         "For dated archives or before/after comparisons, save the input as a task and add a daily or weekly <i>Schedule</i>."],
  faq=[("How do I take screenshots of a list of URLs at once?","Paste the list into <code>urls</code> and run. Pages are captured three at a time by default in headless Chromium, and every URL gets a dataset row with its image link or the reason it failed. A few hundred pages usually finish in minutes."),
       ("How do I save website screenshots to Google Drive?","Each dataset row has a public <code>screenshotUrl</code>. Connect the actor's run-succeeded event to Make, Zapier or n8n, download every image from that column and upload it to a Drive folder. If you only need the links, export the dataset as CSV and import it into Google Sheets; the <code>screenshotUrl</code> column opens each image."),
       ("Can I get full-page and mobile screenshots?","Yes. Turn on <code>fullPage</code> for the whole scrollable page (default cap 10,000 px, up to 30,000) and set <code>device</code> to <code>mobile</code> (390x844 at 2x with a mobile user agent) or <code>tablet</code>. Run twice with different devices to get both versions of each page."),
       ("What does it cost, and are failed pages charged?","$0.002 per saved screenshot, which is $2 per 1,000, with platform usage already included. DNS errors, refused connections, timeouts, file downloads and pages that answer with HTTP 4xx or 5xx are free because no image is saved."),
       ("Does it remove cookie banners?","Common consent popups (OneTrust, Cookiebot, Didomi, Quantcast, Usercentrics, TrustArc and generic cookie bars) are hidden with CSS; nothing is clicked or accepted. Add extra selectors in <code>hideSelectors</code> for chat widgets or promo bars. Pages behind a login, paywall or CAPTCHA can't be captured.")]),
 "us-uk-tenders-scraper": dict(
  slug="sam-gov-contracts-finder-tenders-api",
  ptitle="SAM.gov & UK Contracts Finder API: Export US and UK Tenders to CSV",
  h1="How to export US federal (SAM.gov) and UK (Contracts Finder) tenders to CSV or JSON",
  desc="Search SAM.gov contract opportunities and UK Contracts Finder notices through their official APIs and export title, buyer, deadline, value, NAICS/CPV and notice URL as CSV. $2.50 per 1,000 notices; empty runs and already-seen notices are free.",
  kw=["sam.gov api export","contracts finder api","us federal contract opportunities csv","uk public tenders api","government tender alerts"],
  short="US federal contract opportunities (SAM.gov) and UK public tenders (Contracts Finder) from the official APIs in one schema, with daily only-new alerts.",
  price="$2.50 per 1,000 notices; empty or failed runs and notices skipped as already seen are free",
  input={"sources": ["contracts-finder"], "keywords": ["software"], "publishedWithinDays": 14, "maxResults": 50, "cfStages": ["tender"]},
  intro=["SAM.gov lists every US federal contract opportunity and Contracts Finder lists UK public sector contracts above the publishing thresholds, but both websites are built for browsing one notice at a time, and their search pages don't give you a clean export or alerts with your own filters.",
         "This guide shows how to pull both through their official APIs (SAM.gov Get Opportunities Public API and the Contracts Finder OCDS search under the Open Government Licence) into one table with the same columns: title, buyer, publication and deadline dates, open/closed flag, estimated value and currency, NAICS or CPV code, procedure and notice type, and a direct notice URL."],
  steps=["Pick <code>sources</code>: <code>contracts-finder</code> needs no key; <code>sam.gov</code> needs a free public API key from your SAM.gov Account Details page, pasted into <code>samApiKey</code>.",
         "Add <code>keywords</code> (matched against titles, and UK descriptions), a <code>publishedWithinDays</code> window and <code>maxResults</code>. For SAM.gov you can also filter by <code>samNaicsCode</code>, <code>samState</code> and procurement type; for the UK by stage (planning, tender, award).",
         "Run it and export the dataset as CSV or Excel, or turn on <code>onlyNew</code> with a <code>stateKey</code> and schedule it daily for an alert feed of new notices only."],
  faq=[("Is there an API for SAM.gov contract opportunities?","Yes. GSA publishes the Get Opportunities Public API; you need a free public API key from your SAM.gov account. The actor calls that API with your key, so you get the same notices as the website, as clean rows."),
       ("Does UK Contracts Finder have an API?","Yes. Contracts Finder offers an OCDS (Open Contracting Data Standard) notice search that needs no key. Its data is published under the Open Government Licence v3.0, which allows commercial reuse with attribution."),
       ("How do I get alerts for new government tenders?","Turn on <code>onlyNew</code>, give each saved search its own <code>stateKey</code> and add a daily Schedule. Each run returns only notices it has not returned before, and the skipped ones are free. Send the rows to Google Sheets, email or Slack from the Integrations tab."),
       ("What does it cost?","$0.0025 per notice ($2.50 per 1,000). A run that finds nothing, fails, or only sees notices it already returned costs only the tiny start fee.")]),
 "france-company-search": dict(
  slug="siren-siret-lookup-french-company-list-api",
  ptitle="SIREN / SIRET Lookup API: French Company Data and B2B Lists from Sirene to CSV",
  h1="How to look up French companies by SIREN or SIRET and build a B2B list from Sirene",
  desc="Bulk SIREN, SIRET, VAT and name lookup plus French B2B lists by NAF code, department and headcount from the official API Recherche d'entreprises. CSV export, $1.50 per 1,000 companies; invalid numbers and no-match searches are free.",
  kw=["siren lookup api","siret api","french company database export","sirene api csv","list of companies in france by naf code"],
  short="French company data by SIREN, SIRET, VAT number or name, and B2B lists by NAF code, department, postal code and headcount, from the official Sirene-based API.",
  price="$0.0015 per company ($1.50 per 1,000); invalid numbers, no-match searches and duplicates are free",
  input={"companies": ["552032534", "Michelin"], "maxResultsPerName": 1, "preferLargest": True, "includeDirectors": False},
  intro=["Checking a French supplier, enriching a CRM export of SIREN numbers or sizing a market (\"how many software companies with 10 to 50 staff are there in Lyon?\") all need the same data: the official company register. The public directory site shows one company at a time, the raw Sirene files are several gigabytes, and paid French company databases charge a subscription.",
         "This guide shows how to use the French government's free company search API (API Recherche d'entreprises, the service behind annuaire-entreprises.data.gouv.fr, built on INSEE Sirene and the national business register) to get one clean row per company: name, SIREN and head-office SIRET, NAF code and label, legal form, size category, employee band, address with coordinates, intra-EU VAT number, latest published revenue and net income, and optionally directors. No API key or login is needed."],
  steps=["For lookups, paste SIREN (9 digits), SIRET (14 digits), French VAT numbers (<code>FR</code> + 11 digits) or company names into <code>companies</code>, one per line. Check digits are validated first, so typos come back as free rows instead of wrong companies.",
         "For a B2B list, leave <code>companies</code> empty and set filters instead: <code>nafCodes</code> (e.g. <code>62.01Z</code> software), <code>departments</code> (e.g. <code>69</code>), <code>postalCodes</code>, <code>employeeRanges</code> or <code>companyCategories</code>, plus optional free text in <code>searchQuery</code> and a <code>maxResults</code> cap.",
         "Keep <code>activeOnly</code> on to skip ceased companies, and turn <code>includeDirectors</code> on if you need officers (name and role only, no birth dates).",
         "Run it and export the dataset as CSV or Excel. Each row also links to the company's public Annuaire des Entreprises page. Add a <i>Schedule</i> to refresh the list monthly."],
  faq=[("Is there a free API for SIREN and SIRET lookups?","Yes. The French government (DINUM) runs API Recherche d'entreprises, which needs no key and combines INSEE Sirene with the national business register (RNE). This actor calls it for you, validates the numbers and returns flat rows ready for a spreadsheet."),
       ("How do I get a list of all companies in France with a given NAF code?","Put the NAF/APE code into <code>nafCodes</code> and narrow it with <code>departments</code> or <code>postalCodes</code>. The API serves at most 10,000 companies per search, so for a nationwide list run one department at a time."),
       ("Can I reuse the data commercially?","The data is open data under the Licence Ouverte / Open Licence 2.0, which allows commercial reuse with attribution (\"Source: Annuaire des Entreprises / Sirene, INSEE\"). Companies that opted out of public listing are not in the API. Director names are personal data, so check your GDPR legal basis before using them for outreach."),
       ("What does it cost?","$0.0015 per company returned ($1.50 per 1,000). Invalid SIREN/SIRET numbers, names with no match and duplicates are listed with the reason but not charged.")]),
"norway-company-search": dict(
  slug="norway-org-number-lookup-brreg-company-list",
  ptitle="Norway Org Number Lookup (Brreg API): Norwegian Company Data and Lead Lists to CSV",
  h1="How to look up Norwegian companies by organisation number and build lead lists from Brreg",
  desc="Bulk organisation number and name lookup plus Norwegian B2B lists by NACE code, municipality, employees and registration date from the official Brreg Enhetsregisteret API, with email, phone and website. $1 per 1,000 companies; invalid, no-match and filtered rows are free.",
  kw=["norway org number lookup","brreg api","enhetsregisteret api export","list of norwegian companies by industry","new companies registered in norway"],
  short="Norwegian company data by organisation number or name, and lead lists by NACE code, municipality, employees and registration date, from the official Brreg register.",
  price="$0.001 per company ($1 per 1,000); invalid org numbers, no-match searches, duplicates and filtered rows are free",
  input={"companies": ["923609016", "Telenor"], "maxResultsPerName": 1, "preferLargest": True},
  intro=["Every Norwegian company has a 9-digit organisation number in Enhetsregisteret, the central coordinating register run by the Brønnøysund Register Centre (Brreg). It holds far more than the name: industry code, employee count, business address, email, phone and website when the company registered them, VAT status, share capital and flags for bankruptcy or liquidation.",
         "This guide shows how to read that official open data API in bulk: enrich a list of org numbers, match company names to org numbers, or build a lead list such as \"IT companies in Oslo with 10 to 200 employees and an email address\" or \"every AS registered in Bergen since last Monday\". No API key or login is needed."],
  steps=["For lookups, paste org numbers or company names into <code>companies</code>, one per line. <code>923609016</code>, <code>923 609 016</code> and <code>NO923609016MVA</code> all work, and the mod-11 check digit is validated first, so typos come back as free rows.",
         "For a lead list, leave <code>companies</code> empty and set filters: <code>naceCodes</code> (prefixes work, e.g. <code>62</code> for IT services), <code>municipalities</code> (names like <code>Oslo</code> or 4-digit numbers), <code>postalCodes</code>, <code>legalForms</code>, <code>minEmployees</code>/<code>maxEmployees</code>, and <code>registeredFrom</code> for fresh companies.",
         "Turn on <code>withEmailOnly</code> to keep only companies with a registered email (skipped rows are free), and <code>includeRoles</code> if you need the CEO, chair, board and auditor (names and roles only, no birth dates).",
         "Run it and export the dataset as CSV or Excel. For a weekly feed of new companies, save the input as a task with <code>registeredFrom</code> set to last week and add a <i>Schedule</i>."],
  faq=[("Is there a free API for Norwegian company data?","Yes. Brønnøysundregistrene publishes the Enhetsregisteret open data API with no key required, under the Norwegian Licence for Open Government Data (NLOD) 2.0, which allows commercial reuse with attribution. This actor calls it politely (a few requests per second with backoff) and returns flat rows."),
       ("How do I get a list of all companies in a Norwegian industry or municipality?","Set <code>naceCodes</code> and <code>municipalities</code> and run without <code>companies</code>. The register serves at most 10,000 results per search, so for bigger lists split by municipality or NACE code. The <code>matchTotal</code> field shows the full count for market sizing."),
       ("Can I find newly registered companies in Norway?","Yes. Set <code>registeredFrom</code> (and optionally <code>registeredTo</code>) together with a municipality or industry filter, and turn off <code>sortByEmployees</code> since new companies usually have none yet. Accountants, banks, insurers and SaaS sales teams use this as a weekly lead feed."),
       ("Is it GDPR compliant?","Register data can include names and work emails of people. If you use it for marketing you are the data controller, so check your legal basis and honour opt-outs. Roles are returned without birth dates.")]),
"sec-edgar-filings-scraper": dict(
  slug="sec-edgar-api-download-10-k-8-k-filings-csv",
  ptitle="SEC EDGAR API: Download 10-K, 10-Q, 8-K and Form 4 Filings by Ticker to CSV",
  h1="How to download SEC filings (10-K, 10-Q, 8-K, Form 4) by ticker and search EDGAR full text",
  desc="Turn a list of tickers or CIKs into a table of SEC filings with direct document links, or search the full text of EDGAR filings since 2001. Official SEC EDGAR APIs, $0.50 per 1,000 filings; unknown tickers and empty searches are free.",
  kw=["sec edgar api python","download 10-k filings by ticker","8-k filings feed","edgar full text search api","sec filings to csv"],
  short="SEC filings by ticker or CIK (10-K, 10-Q, 8-K, Form 4, S-1 and more) with document links, plus EDGAR full-text search, from the official SEC EDGAR APIs.",
  price="$0.0005 per filing ($0.50 per 1,000); unknown tickers, companies with no matching filings, empty searches and duplicates are free",
  input={"companies": ["AAPL", "MSFT", "NVDA"], "formTypes": ["10-K", "10-Q"], "dateFrom": "2024-10-01", "maxFilingsPerCompany": 20},
  intro=["The SEC publishes every filing for free, but the EDGAR website shows one company at a time, the JSON APIs need a CIK instead of a ticker, and full-text search is a separate service with its own format. Building a watchlist feed of 8-Ks or a table of the last two years of 10-Qs for 50 companies means stitching all of that together.",
         "This guide shows how to get one clean row per filing from the official SEC EDGAR APIs: company, CIK, form, filing and report date, accession number, 8-K items as a list, SIC industry, and direct links to the main document and the filing index. The same run can also search the full text of every filing since 2001 for phrases like \"going concern\" or \"cybersecurity incident\". No API key is needed."],
  steps=["Add tickers (<code>AAPL</code>, <code>BRK-B</code>) or CIKs to <code>companies</code>. Tickers are resolved with the SEC's own ticker list, and unknown ones come back as free rows.",
         "Pick <code>formTypes</code> (empty means all forms) and an optional <code>dateFrom</code>. Turn on older filings if you need history beyond the latest ~1,000 filings per company.",
         "For a topic search, set <code>fullTextQuery</code> (e.g. <code>\"supply chain\" tariff</code>) with form and date filters instead of, or next to, companies.",
         "Run it and export as CSV or Excel. For a daily feed of new filings for your watchlist, add a <i>Schedule</i> with <code>dateFrom</code> set to yesterday."],
  faq=[("Does the SEC have a free API for EDGAR filings?","Yes. The SEC runs free JSON APIs on data.sec.gov and a full-text search service, with a fair-use limit of 10 requests per second and a declared User-Agent. This actor stays well under that limit and returns flat rows instead of raw JSON."),
       ("How do I get only earnings releases or executive changes from 8-K filings?","Set <code>formTypes</code> to <code>[\"8-K\"]</code> and filter the <code>items</code> column: 2.02 is results of operations (earnings), 5.02 is officer and director changes, 1.01 is a material agreement."),
       ("Can I feed the filings into an LLM or RAG pipeline?","Yes. Each row has <code>documentUrl</code> and <code>filingIndexUrl</code>, so you can fetch the main document or exhibits you need. The actor itself returns metadata and links, not the full documents."),
       ("What does it cost?","$0.0005 per filing returned ($0.50 per 1,000), cheaper on higher Apify plans. A filing found by two searches is charged once.")]),
 "npi-registry-lookup": dict(
  slug="npi-lookup-api-bulk-npi-validation-provider-list",
  ptitle="NPI Lookup API: Bulk NPI Validation and US Healthcare Provider Lists to CSV",
  h1="How to validate NPI numbers in bulk and build US healthcare provider lists from NPPES",
  desc="Validate a list of NPI numbers or pull every dentist, cardiologist or pharmacy in a city, state or ZIP from the official CMS NPPES NPI Registry API. CSV export, $0.80 per 1,000 providers; invalid and unknown NPIs are free.",
  kw=["npi lookup api","bulk npi validation","nppes npi registry export","list of dentists by zip code","healthcare provider database csv"],
  short="Bulk NPI validation and US healthcare provider lists by specialty, city, state or ZIP, from the official CMS NPPES NPI Registry.",
  price="$0.0008 per provider record ($0.80 per 1,000); invalid, unknown or deactivated NPIs, empty searches, filtered and duplicate providers are free",
  input={"taxonomyDescription": "Dentist", "entityType": "individual", "cities": ["Austin", "Dallas"], "states": ["TX"], "primaryTaxonomyOnly": True, "maxRecords": 500},
  intro=["Every US healthcare provider that bills insurance has a 10-digit National Provider Identifier (NPI) in the NPPES registry run by CMS. Credentialing teams check NPIs, billing teams clean them up in claims data, and healthcare sales teams use the registry to find every practice of a given specialty in their territory. The public search page shows one provider at a time and caps results.",
         "This guide shows how to use the free NPPES NPI Registry API in bulk: validate thousands of NPIs (the check digit is verified locally first), or build a provider list by specialty and location with flat spreadsheet columns for name, credential, primary specialty, license, practice address and phone."],
  steps=["To validate or enrich, paste NPI numbers into <code>npis</code>, one per line. Numbers with a wrong check digit, unknown or deactivated NPIs come back as free <code>found: false</code> rows.",
         "To build a list, set <code>taxonomyDescription</code> (e.g. <code>Dentist</code>, <code>Nurse Practitioner</code>, <code>cardio*</code>) and combine it with <code>cities</code>, <code>states</code> or ZIP codes. Each city and state pair runs as its own search, up to the NPPES limit of 1,200 results per search.",
         "Turn on <code>primaryTaxonomyOnly</code> to keep real specialists (NPPES also matches secondary specialties), and set <code>entityType</code> to individuals or organizations.",
         "Run it and export the dataset as CSV or Excel, or send it to Google Sheets from the Integrations tab."],
  faq=[("Is there a free API for NPI lookups?","Yes. CMS runs the NPPES NPI Registry API with no key. The data is public by law (FOIA-disclosable), free to reuse, and US government work. This actor adds check-digit validation, paging, deduplication and flat columns."),
       ("How do I get a list of all dentists or pharmacies in a ZIP code?","Set the specialty and the ZIP codes, or use a raw NPPES search with <code>taxonomy_description</code> and <code>postal_code</code>. For a whole state, split by city or ZIP, since NPPES returns at most 1,200 providers per search."),
       ("Does an active NPI prove a provider is licensed?","No. An NPI is an identifier, not a license check. Use the license number and state in the output to verify with the state board."),
       ("What does it cost?","$0.0008 per provider found ($0.80 per 1,000). Rows with <code>found: false</code>, filtered-out providers and duplicates are not charged.")]),
 "uk-companies-house-lookup": dict(
  slug="companies-house-api-bulk-uk-company-lookup",
  ptitle="Companies House API Bulk Lookup: UK Company Profiles, Officers and PSC to CSV",
  h1="How to look up hundreds of UK companies on Companies House at once (profile, officers, PSC)",
  desc="Bulk UK company lookup by company number or name with the official Companies House API: status, registered office, SIC codes, due dates, officers and persons with significant control. $2 per 1,000 profiles; not-found rows are free.",
  kw=["companies house api bulk lookup","uk company number lookup","companies house officers export","psc register lookup","kyb uk company check"],
  short="UK company profiles by number or name from the official Companies House API, with officers and persons with significant control on the same row.",
  price="$0.002 per company profile found ($2 per 1,000), officers and PSC included; invalid numbers and names with no match are free",
  input={"companyNumbers": ["00445790", "00000006"], "companyNames": ["Tesco"], "includeOfficers": False, "includePersonsWithSignificantControl": False, "maxResultsPerName": 1, "maxCompanies": 100},
  intro=["Supplier onboarding, KYB checks and CRM clean-up all start with the same question: is this UK company real, active and up to date with its filings, and who runs and owns it? The Companies House website answers it one company at a time, and its terms ask people not to bulk-scrape the website.",
         "This guide shows how to use the official Companies House Public Data API instead, with your own free API key, to check hundreds of companies in one run: status, type, incorporation date, registered office, SIC codes, liquidation and charges flags, next accounts and confirmation statement due dates, and optionally officers and persons with significant control (PSC)."],
  steps=["Get a free API key at the <a href=\"https://developer.company-information.service.gov.uk/\">Companies House developer hub</a> and put it in <code>apiKey</code>. Without a key the actor only serves a small demo.",
         "Add company numbers to <code>companyNumbers</code> (Scottish <code>SC</code>, Northern Irish <code>NI</code> and LLP <code>OC</code> prefixes work) and/or names to <code>companyNames</code>. Set <code>maxResultsPerName</code> to 1 when you only want the best match.",
         "Turn on <code>includeOfficers</code> and <code>includePersonsWithSignificantControl</code> if you need directors and owners. They are nested on the same row at no extra charge.",
         "Run it and export the dataset as CSV or Excel. Re-run it monthly as a task to catch status changes and overdue accounts."],
  faq=[("Is the Companies House API free?","Yes. The Public Data API is free with a key from the developer hub and is limited to 600 requests per key per 5 minutes. The actor throttles itself under that limit and retries politely."),
       ("Can I reuse Companies House data commercially?","Companies House does not restrict how public register information is used. Officer and PSC names are personal data, so check your GDPR legal basis before using them for marketing."),
       ("How do I check if a UK company is overdue with its accounts?","Look at <code>accountsNextDue</code> and <code>confirmationStatementNextDue</code> in the output and compare them with today's date. <code>companyStatus</code>, <code>hasBeenLiquidated</code> and <code>hasCharges</code> cover the other basic red flags."),
       ("What does it cost?","$0.002 per company profile found ($2 per 1,000). Officers and PSC are included in that price. Invalid numbers and names without a match return free rows with the reason.")]),
 "finland-company-search": dict(
  slug="y-tunnus-lookup-finnish-company-list-ytj-api",
  ptitle="Y-tunnus Lookup API: Finnish Company Data and B2B Lead Lists from YTJ to CSV",
  h1="How to look up Finnish companies by Y-tunnus and build B2B lead lists from the YTJ register",
  desc="Bulk Y-tunnus (business ID) and name lookup plus Finnish B2B lists by industry, city, company form and registration date from the official PRH YTJ open data API, with website and VAT status. $1 per 1,000 companies; invalid, no-match and filtered rows are free.",
  kw=["y-tunnus lookup api","ytj api export","finnish company database csv","list of companies in finland by industry","new companies registered in finland"],
  short="Finnish company data by business ID (Y-tunnus) or name, and lead lists by industry, city, postal code, company form and registration date, from the official YTJ register.",
  price="$0.001 per company ($1 per 1,000); invalid business IDs, no-match searches, duplicates and filtered rows are free",
  input={"companies": ["0112038-9", "FI23365096", "Kone"]},
  intro=["Every Finnish company has a business ID (Y-tunnus) in YTJ, the business information system run by the Finnish Patent and Registration Office (PRH) and the Tax Administration. It tells you the official name, company form, main line of business, addresses, website, registration date and whether the company is in the VAT, employer and prepayment registers or in bankruptcy or liquidation.",
         "This guide shows how to read the YTJ open data API in bulk: enrich a CRM list of business IDs, match names to business IDs, or build a lead list such as \"IT companies in Tampere and Oulu that are VAT-registered employers with a website\" or \"every new limited company registered this month\". No API key or login is needed."],
  steps=["For lookups, paste business IDs or names into <code>companies</code>. <code>0112038-9</code>, <code>01120389</code> and the VAT form <code>FI01120389</code> all work, and the check digit is validated first, so typos come back as free rows.",
         "For a lead list, leave <code>companies</code> empty and set <code>industryCodes</code> (TOL prefixes, e.g. <code>62</code> for IT), <code>cities</code> (Finnish post office names), postal codes, <code>companyForms</code> (e.g. <code>OY</code>) and <code>registeredFrom</code>, with a <code>maxResults</code> cap.",
         "Turn on <code>vatRegisteredOnly</code>, <code>employerOnly</code> or <code>withWebsiteOnly</code> to keep only real, active businesses. Skipped rows are free.",
         "Run it and export the dataset as CSV or Excel. For a weekly feed of new companies, save the input as a task with <code>registeredFrom</code> and add a <i>Schedule</i>."],
  faq=[("Is there a free API for Finnish company data?","Yes. PRH publishes the YTJ open data API with no key, under the Creative Commons Attribution 4.0 licence, which allows commercial reuse with attribution. This actor calls it politely and returns flat rows."),
       ("How do I get a list of all companies in a Finnish industry or city?","Set <code>industryCodes</code> and <code>cities</code> and run without <code>companies</code>. Only the company's main line of business counts, and <code>matchTotal</code> shows the full count of a search for market sizing."),
       ("Does it include emails or phone numbers?","No. The public register has no emails, phones, employee counts or financial statements. Many companies list a website, so you can pass those websites to a contact extractor."),
       ("What does it cost?","$0.001 per company returned ($1 per 1,000). Invalid business IDs, names with no match, duplicates and rows skipped by your filters are not charged.")]),
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
 dict(slug="free-tender-alerts-ted-sam-gov-contracts-finder", actor="us-uk-tenders-scraper",
  ptitle="Free Tender Alerts: TED (EU) + SAM.gov (US) + Contracts Finder (UK) in One Sheet",
  h1="How to get EU, US and UK tender alerts in one Google Sheet (TED, SAM.gov, Contracts Finder)",
  desc="Combine daily alerts for new public tenders from TED (EU), SAM.gov (US federal) and UK Contracts Finder into one Google Sheet, filtered by keyword, CPV or NAICS code. Official APIs only, $2.50 per 1,000 notices, already-seen notices free.",
  intro=["If you sell to governments in more than one market, you end up checking three portals every morning: TED for the EU, SAM.gov for US federal buyers and Contracts Finder for the UK. Commercial tender alert services that cover all three usually cost hundreds per year, yet all three sources publish official open APIs.",
         "This tutorial sets up two scheduled runs, one for TED and one for SAM.gov plus Contracts Finder, that return only new notices matching your keywords and append them to the same Google Sheet. Both tools share the core columns (<code>noticeId</code>, <code>title</code>, <code>buyerName</code>, <code>buyerCountry</code>, <code>publicationDate</code>, <code>deadlineDate</code>, <code>isOpen</code>, <code>estimatedValue</code>, <code>procedureType</code>, <code>noticeUrl</code>), so the sheet reads as one list."],
  input={"sources": ["sam.gov", "contracts-finder"], "keywords": ["cybersecurity"], "publishedWithinDays": 1, "maxResults": 200, "samApiKey": "YOUR_SAM_PUBLIC_API_KEY", "onlyNew": True, "stateKey": "cyber-us-uk"},
  steps=["US and UK: open the <a href=\"https://apify.com/tinyrex/us-uk-tenders-scraper\">SAM.gov &amp; UK Contracts Finder Tenders Scraper</a>, select both sources, paste your free SAM.gov public API key (Account Details on sam.gov) and add your keywords. Contracts Finder alone works without any key.",
         "EU: open the <a href=\"https://apify.com/tinyrex/ted-tenders-scraper\">TED Tenders Scraper</a> with the same keywords, plus CPV codes (e.g. <code>72000000</code> for IT services) and buyer countries if you want to narrow it. Example: <code>{\"keywords\": [\"cybersecurity\"], \"cpvCodes\": [\"72000000\"], \"publishedWithinDays\": 1, \"onlyNew\": true, \"stateKey\": \"cyber-eu\"}</code>.",
         "In both, turn on <code>onlyNew</code> and give each saved search its own <code>stateKey</code>, so every run returns only notices you have not seen yet (skipped notices are free). Save each input as a task and add a daily Schedule.",
         "On each task's <i>Integrations</i> tab, append the rows to the same Google Sheet (Apify's Google Sheets Import &amp; Export actor, Make, Zapier or n8n). Map TED's <code>estimatedValueCurrency</code> to the <code>currency</code> column; the other core columns have the same names. Add a Slack or email step if you want a ping when new rows arrive.",
         "@SHEETS"],
  faq=[("Are TED, SAM.gov and Contracts Finder data free to reuse?","Yes. TED is EU open data from the Publications Office of the EU, reusable with attribution. Contracts Finder is published under the UK Open Government Licence v3.0. SAM.gov opportunity data is US government information; you only need a free public API key to call the API."),
       ("Do I need a SAM.gov API key?","Only for the US source. Create a free SAM.gov account, open Account Details and generate a public API key. TED and Contracts Finder need no key."),
       ("What does a daily three-market alert cost?","Both tools charge $0.0025 per new notice ($2.50 per 1,000). A focused keyword search typically returns a few dozen new notices a day, so a month of alerts usually stays within the free monthly credit of the Apify free plan. Runs that find nothing new cost only the start fee."),
       ("Can I filter by CPV or NAICS code instead of keywords?","Yes. TED takes CPV codes (with sub-codes included by default), SAM.gov takes a NAICS code, and UK notices carry their CPV code in <code>cpvOrNaics</code>, so you can also filter in the sheet.")]),
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
        g = dict(G[n]); inp = g.pop("input", None) or json.loads(m[0])  # explicit input when the README's first JSON block is sample output
        res.append(dict(name=n, title=d["title"], input=inp, sample=trim(sample[0] if isinstance(sample, list) else sample), **g))
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
<footer>TinyRex Data Tools. Guides and examples for <a href="https://apify.com/tinyrex">TinyRex actors on Apify</a>. Only public data; respect each site's terms. Copy-paste Python, Node.js and curl code in <a href="https://github.com/emirmrkaljevic/tinyrex-examples">tinyrex-examples</a>. Source on <a href="https://github.com/emirmrkaljevic/tinyrex-data-tools">GitHub</a>.</footer></body></html>"""

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

def index(actors, tuts=(), cps=()):
    cards = "".join(f'<div class="card"><h3><a href="{a["slug"]}/">{E(a["title"].split(" - ")[0])}</a></h3><p>{E(a["short"])}</p><p class="mut">{E(a["price"])}</p><p><a href="{a["slug"]}/">Guide</a> · <a href="{STORE}{a["name"]}">Apify Store</a></p></div>' for a in actors)
    body = f"""<h1>Practical guides for pulling clean data from the web</h1>
<p>TinyRex builds small, cheap, API-first data tools on <a href="https://apify.com/tinyrex">Apify</a>: bulk tech stack lookup, job postings from ATS and remote job boards, e-commerce product catalogs, RSS feeds, website sitemaps, EU public tenders and EU funding calls. Every tool returns clean JSON/CSV, charges only per delivered result, and works from Python, JavaScript, plain HTTP, no-code tools and AI agents (via the Apify MCP server).</p>
<p>Each guide below has a working example input, real sample output and copy-paste code.</p>
<div class="cards">{cards}</div>
{('<h2>Tutorials</h2><ul>' + ''.join(f'<li><a href="{t["slug"]}/">{E(t["h1"])}</a></li>' for t in tuts) + '</ul>') if tuts else ''}
{('<h2>Data products</h2><ul>' + ''.join(f'<li><a href="{p["slug"]}/">{E(p["h1"])}</a> — free preview + weekly Excel on Gumroad</li>' for p in PRODUCTS) + '</ul>') if PRODUCTS else ''}
{('<p>Open IT tenders this week by country: ' + ' · '.join(f'<a href="{c["slug"]}/">{E(c["country"])}</a>' for c in cps) + '</p>') if cps else ''}
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
    cps = country_pages()
    w("index.html", index(actors, tuts, cps)); w("style.css", CSS); w(".nojekyll", "")
    for a in actors:
        w(f"{a['slug']}/index.html", guide(a, actors))
    for t in tuts:
        w(f"{t['slug']}/index.html", tutorial(t, by[t["actor"]], actors))
    for prod in PRODUCTS:
        html_ = render_product_page(prod, by, OUT, page, STORE, TODAY, E)
        if cps:
            html_ = html_.replace("<h2>Sources and licence</h2>", "<h2>Open IT tenders this week by country</h2><p>"
                + " · ".join(f'<a href="../{c["slug"]}/">{E(c["country"])} ({len(c["rows"])})</a>' for c in cps)
                + "</p>\n<h2>Sources and licence</h2>", 1)
        w(f"{prod['slug']}/index.html", html_)
    for cp in cps:
        w(f"{cp['slug']}/index.html", render_country_page(cp, cps, page, TODAY, E))
    urls = ([f"{BASE}/"]
            + [f"{BASE}/{a['slug']}/" for a in actors]
            + [f"{BASE}/{t['slug']}/" for t in tuts]
            + [f"{BASE}/{prod['slug']}/" for prod in PRODUCTS]
            + [f"{BASE}/{cp['slug']}/" for cp in cps]
            + [f"{BASE}/data/{PREVIEW_CSV_NAME}"])
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    w("404.html", page("", "Page not found | TinyRex Data Tools", "Page not found",
                       '<h1>Page not found</h1><p><a href="./">Back to all guides</a></p>')
               .replace('href="style.css"', f'href="{BASE}/style.css"'))
    pages = [{"name": a["name"], "slug": a["slug"], "url": f"{BASE}/{a['slug']}/"} for a in actors]
    pages += [{"name": prod["slug"], "slug": prod["slug"], "url": f"{BASE}/{prod['slug']}/", "type": "product"} for prod in PRODUCTS]
    pages += [{"name": cp["slug"], "slug": cp["slug"], "url": f"{BASE}/{cp['slug']}/", "type": "country-tenders"} for cp in cps]
    json.dump(pages, open(os.path.join(ROOT, "pages.json"), "w"), indent=1)
    print("built", len(actors), "guides:", [a["slug"] for a in actors],
          "tutorials:", [t["slug"] for t in tuts], "products:", [prod["slug"] for prod in PRODUCTS])

if __name__ == "__main__":
    main()
