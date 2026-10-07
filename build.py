#!/usr/bin/env python3
"""Static site generator for the TinyRex data tools guide site (GitHub Pages).
Usage: APIFY_TOKEN=... python3 build.py  -> regenerates ./docs from public tinyrex actors that have an entry in G.
To add an actor: add it to G below, rebuild, commit and push (see README "Rebuilding the site")."""
import json, os, re, html, datetime, urllib.request, shutil
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
 "dach-jobs-scraper": dict(
  slug="arbeitsagentur-jobs-api",
  ptitle="Bundesagentur für Arbeit Jobs API: Export Arbeitsagentur & EURES Jobs",
  h1="How to export jobs from the Bundesagentur für Arbeit (Arbeitsagentur) and EURES",
  desc="Export jobs from the Bundesagentur für Arbeit Jobsuche API and EURES (Germany, Austria, Switzerland, EU) to CSV/JSON with full descriptions and salary.",
  kw=["bundesagentur für arbeit jobs api","arbeitsagentur jobsuche api","arbeitsagentur scraper","eures jobs api","austria switzerland jobs dataset"],
  short="Jobs from the Bundesagentur für Arbeit (Germany) and EURES (Austria, Switzerland, EU) with full descriptions, salary and location.",
  price="$1 per 1,000 jobs with full descriptions",
  intro=["The Bundesagentur für Arbeit runs Germany's largest job database (over a million listings) and has a public Jobsuche API, but it needs specific headers, paging and a separate call per job for the description. EURES adds vacancies from Austria (AMS), Switzerland and the rest of the EU in a different format.",
         "This guide shows how to search both by keyword and location and get one normalized dataset with full descriptions, salary (when published), postal code, coordinates, working time and contract type."],
  steps=["Enter <code>keywords</code> (e.g. <code>Elektriker</code>, <code>Data Analyst</code>) and pick <code>sources</code>.",
         "Set Arbeitsagentur locations and radius, and EURES country codes (<code>at</code>, <code>ch</code>...).",
         "Export to CSV/JSON, or schedule with <code>publishedWithinDays</code> for a daily feed of new jobs."],
  faq=[("Does the Arbeitsagentur have an official jobs API?","Yes, the public Jobsuche API that powers arbeitsagentur.de. The actor uses it (and the EURES public search), so results match the official portals."),
       ("Can I get jobs in Austria and Switzerland?","Yes, through EURES, which aggregates vacancies from the AMS and other European public employment services."),
       ("Are full descriptions included?","Yes, at the same price of $1 per 1,000 jobs.")]),
}

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
.mut{color:var(--mut)}footer{margin-top:60px;padding:20px;border-top:1px solid #e3e7ec;color:var(--mut);font-size:.9rem}details{margin:6px 0}"""

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

def index(actors):
    cards = "".join(f'<div class="card"><h3><a href="{a["slug"]}/">{E(a["title"].split(" - ")[0])}</a></h3><p>{E(a["short"])}</p><p class="mut">{E(a["price"])}</p><p><a href="{a["slug"]}/">Guide</a> · <a href="{STORE}{a["name"]}">Apify Store</a></p></div>' for a in actors)
    body = f"""<h1>Practical guides for pulling clean data from the web</h1>
<p>TinyRex builds small, cheap, API-first data tools on <a href="https://apify.com/tinyrex">Apify</a>: bulk tech stack lookup, job postings from ATS and public employment services, e-commerce product catalogs and EU public tenders. Every tool returns clean JSON/CSV, charges only per delivered result, and works from Python, JavaScript, plain HTTP, no-code tools and AI agents (via the Apify MCP server).</p>
<p>Each guide below has a working example input, real sample output and copy-paste code.</p>
<div class="cards">{cards}</div>
<h2>Use any of these tools from an AI agent</h2>
<p>Connect Claude, Cursor or n8n to <code>https://mcp.apify.com?tools={','.join('tinyrex/'+a['name'] for a in actors)}</code> and the agent can call every tool above directly.</p>"""
    ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i+1, "url": f"{BASE}/{a['slug']}/", "name": a["title"]} for i, a in enumerate(actors)]}
    return page("", "TinyRex Data Tools: Web Data APIs & Scraper Guides (Jobs, E-commerce, Tenders)", "Guides with working examples for bulk tech stack lookup, Greenhouse/Workday/Arbeitsagentur job APIs, Shopify/WooCommerce product export and TED EU tenders.", body, ld)

def main():
    actors = load_actors()
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    w = lambda p, s: (os.makedirs(os.path.dirname(os.path.join(OUT, p)), exist_ok=True), open(os.path.join(OUT, p), "w").write(s))
    w("index.html", index(actors)); w("style.css", CSS); w(".nojekyll", "")
    for a in actors:
        w(f"{a['slug']}/index.html", guide(a, actors))
    urls = [f"{BASE}/"] + [f"{BASE}/{a['slug']}/" for a in actors]
    w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    w("404.html", page("", "Page not found | TinyRex Data Tools", "Page not found", '<h1>Page not found</h1><p><a href="./">Back to all guides</a></p>').replace('href="style.css"', f'href="{BASE}/style.css"'))
    json.dump([{"name": a["name"], "slug": a["slug"], "url": f"{BASE}/{a['slug']}/"} for a in actors], open(os.path.join(ROOT, "pages.json"), "w"), indent=1)
    print("built", len(actors), "guides:", [a["slug"] for a in actors])

if __name__ == "__main__":
    main()
