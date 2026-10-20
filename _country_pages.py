"""Weekly 'Open IT tenders in <country> this week' SEO pages (D1b).
Built from the latest EU IT Tenders & Grants Weekly issue (TED open data), top 5 countries by tender count.
Each page shows the highest-value open tenders as a teaser and links the free preview + Gumroad product."""
import csv
import datetime
import glob
import json
import os
import re
from collections import Counter

ISSUES = "/workspace/zarada/data-products/eu-it-tenders-grants-weekly/issues"
TOP_N_COUNTRIES = 5
SHOW_ROWS = 10
PRODUCT_SLUG = "eu-it-tenders-grants-weekly"
MEMBERSHIP = "https://emirmk.gumroad.com/l/eu-it-tenders-weekly"
SINGLE = "https://emirmk.gumroad.com/l/eu-it-tenders-issue"
STORE = "https://apify.com/tinyrex/"


def latest_issue():
    dirs = sorted(d for d in glob.glob(os.path.join(ISSUES, "*")) if re.search(r"\d{4}-\d{2}-\d{2}$", d))
    for d in reversed(dirs):
        date = os.path.basename(d)
        f = os.path.join(d, f"eu-it-tenders-{date}.csv")
        if os.path.exists(f):
            return date, f
    return None, None


def latest_preview_csv():
    for d in sorted(glob.glob(os.path.join(ISSUES, "*")), reverse=True):
        hits = glob.glob(os.path.join(d, "free-preview-20-tenders-*.csv"))
        if hits:
            return hits[0]
    return None


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _eur(v):
    try:
        return float(str(v).replace(",", ""))
    except Exception:
        return None


def country_pages():
    """Return list of dicts: slug, country, rows (open on build day), issue date."""
    issue, path = latest_issue()
    if not path:
        return []
    today = datetime.date.today()
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    def is_open(r):
        try:
            return datetime.date.fromisoformat(r["Deadline"][:10]) >= today
        except Exception:
            return False
    # Pick countries from the whole issue so the page set (and URLs) stays stable all week;
    # only the rows shown are limited to tenders still open on build day.
    top = [c for c, _ in Counter(r["Country"] for r in rows if r.get("Country")).most_common(TOP_N_COUNTRIES)]
    rows = [r for r in rows if is_open(r)]
    out = []
    for c in top:
        out.append(dict(slug=f"open-it-tenders-{slugify(c)}-this-week", country=c,
                        rows=[r for r in rows if r["Country"] == c], issue=issue))
    return out


def render_country_page(cp, all_pages, page_fn, today, E):
    c, rows, issue = cp["country"], cp["rows"], cp["issue"]
    n = len(rows)
    vals = sorted(v for v in (_eur(r.get("Estimated value (EUR, approx.)")) for r in rows) if v)
    median = vals[len(vals) // 2] if vals else None
    total = sum(vals) if vals else 0
    cities = [x for x, _ in Counter(r["Buyer city"] for r in rows if r.get("Buyer city")).most_common(5)]
    cpvs = Counter(r["CPV label"] for r in rows if r.get("CPV label")).most_common(4)
    closing7 = sum(1 for r in rows if (datetime.date.fromisoformat(r["Deadline"][:10]) - datetime.date.today()).days <= 7)
    show = sorted(rows, key=lambda r: -(_eur(r.get("Estimated value (EUR, approx.)")) or 0))[:SHOW_ROWS]

    def money(v):
        v = _eur(v)
        return f"€{v:,.0f}" if v else "not stated"

    trs = "".join(
        "<tr>"
        f"<td>{E(r['Deadline'][:10])}</td>"
        f"<td><a href=\"{E(r['TED notice'])}\" rel=\"nofollow\">{E((r.get('Title (English)') or '')[:110])}</a></td>"
        f"<td>{E((r.get('Buyer (public body)') or '')[:60])}{(', ' + E(r['Buyer city'])) if r.get('Buyer city') else ''}</td>"
        f"<td>{E(money(r.get('Estimated value (EUR, approx.)')))}</td>"
        "</tr>" for r in show)
    cpv_html = "".join(f"<li>{E(l)}: {k}</li>" for l, k in cpvs)
    others = [p for p in all_pages if p["slug"] != cp["slug"]]
    others_html = " · ".join(f'<a href="../{E(p["slug"])}/">{E(p["country"])}</a>' for p in others)
    title = f"Open IT & Software Tenders in {c} This Week ({n} on TED)"
    desc = (f"{n} open public IT and software tenders in {c} from TED (CPV 72 + 48), published in the week to {issue}: "
            f"English titles, buyers, deadlines and values. Free preview CSV, full weekly Excel for all EU countries.")
    body = f"""<h1>Open IT and software tenders in {E(c)} this week</h1>
<p class="mut">Updated {today} · from the {issue} issue · source: TED (Tenders Electronic Daily), CPV 72 (IT services) + 48 (software)</p>
<p>Public buyers in <strong>{E(c)}</strong> published <strong>{n} IT and software tenders</strong> on TED in the seven days to {issue} that are still open today{f", {closing7} of them closing within 7 days" if closing7 else ""}. {f"Where a value is published, the median contract is about <strong>€{median:,.0f}</strong> and the total is roughly <strong>€{total:,.0f}</strong>." if median else ""} Titles are shown in English (machine-translated where the buyer did not publish one).</p>
<p>
<a class="cta row" href="../{PRODUCT_SLUG}/">Free 20-row EU preview →</a>
<a class="cta row" href="{MEMBERSHIP}">Every country, every Monday: $19/mo →</a>
<a class="cta sec row" href="{SINGLE}">This week's full file $9 →</a>
</p>
<h2>The {len(show)} largest open IT tenders in {E(c)}</h2>
<table class="sample"><thead><tr><th>Deadline</th><th>Title (English)</th><th>Buyer</th><th>Est. value</th></tr></thead><tbody>{trs}</tbody></table>
<p class="mut">Showing {len(show)} of {n} open tenders in {E(c)}. The full weekly Excel has all of them, plus about 30 other European countries, with CPV, procedure, lots, short English description, documents and submission links.</p>
<h2>What buyers in {E(c)} are asking for</h2>
<ul>{cpv_html}</ul>
{f"<p>Most active buyer locations this week: {E(', '.join(cities))}.</p>" if cities else ""}
<h2>Get all {E(c)} IT tenders every Monday</h2>
<div class="pricebox">
<ul>
<li><strong>Membership</strong>: <a href="{MEMBERSHIP}">$19/month or $149/year</a>. Each Monday you get an Excel + CSV of every open EU IT/software tender (English titles, values, deadlines, links) and the open EU digital grant calls.</li>
<li><strong>Single issue</strong>: <a href="{SINGLE}">$9</a> for this week's file only.</li>
<li><strong>Free</strong>: the <a href="../{PRODUCT_SLUG}/">20-row preview</a> with the same columns.</li>
</ul>
</div>
<h2>Do it yourself with the API</h2>
<p>Prefer raw data on your own schedule? The <a href="{STORE}ted-tenders-scraper">TED EU Tenders Scraper</a> on Apify returns the same notices as JSON/CSV. Filter it by country and CPV code, and run it daily or weekly. See the <a href="../ted-tenders-api-export/">TED tenders export guide</a>.</p>
<h2>Other countries this week</h2>
<p>{others_html}</p>
<h2>Source and licence</h2>
<p>Data from <a href="https://ted.europa.eu">TED</a>, © European Union, reused under <a href="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32011D0833">Commission Decision 2011/833/EU</a>. Not affiliated with the European Union or the Publications Office. Values are converted to EUR at ECB reference rates and are approximate. Always check the official notice before bidding.</p>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": title, "description": desc,
          "creator": {"@type": "Organization", "name": "TinyRex"},
          "isBasedOn": "https://ted.europa.eu", "temporalCoverage": issue,
          "spatialCoverage": {"@type": "Place", "name": c},
          "license": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32011D0833"}
    return page_fn(f"{cp['slug']}/", title, desc, body, ld)
