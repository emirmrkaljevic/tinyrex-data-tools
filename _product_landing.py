"""Product landing pages + static asset restore for the TinyRex guide site."""
import csv
import json
import os
import shutil
import urllib.request

ACT = "/workspace/zarada/actors"
INDEXNOW_KEY = "8dd125fabb85f1a3eeea6180838b441b"
PREVIEW_CSV_SRC = "/workspace/zarada/data-products/eu-it-tenders-grants-weekly/issues/2026-10-09/free-preview-20-tenders-2026-10-09.csv"
PREVIEW_CSV_NAME = "eu-it-tenders-free-preview.csv"

PRODUCTS = [
    dict(
        slug="eu-it-tenders-grants-weekly",
        ptitle="Free Preview: Weekly EU IT Tenders & Digital Grants Excel/CSV",
        h1="Free preview: weekly EU IT tenders + digital grants as Excel/CSV",
        desc=(
            "Download a free 20-row preview of open EU IT/software tenders with English titles, "
            "then subscribe for the full weekly Excel (TED tenders + EU digital grants) at $19/mo "
            "or buy a single issue for $9."
        ),
        preview_csv="data/eu-it-tenders-free-preview.csv",
        membership="https://emirmk.gumroad.com/l/eu-it-tenders-weekly",
        single="https://emirmk.gumroad.com/l/eu-it-tenders-issue",
    ),
]


def restore_static(out_dir):
    """Re-copy assets that rmtree(docs) would otherwise drop (CSV preview, logos, IndexNow key)."""
    data_dir = os.path.join(out_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    if os.path.exists(PREVIEW_CSV_SRC):
        shutil.copy2(PREVIEW_CSV_SRC, os.path.join(data_dir, PREVIEW_CSV_NAME))
    logos_dir = os.path.join(out_dir, "logos")
    os.makedirs(logos_dir, exist_ok=True)
    if os.path.isdir(ACT):
        for name in sorted(os.listdir(ACT)):
            src = os.path.join(ACT, name, "logo.png")
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(logos_dir, f"{name}.png"))
    with open(os.path.join(out_dir, f"{INDEXNOW_KEY}.txt"), "w") as f:
        f.write(INDEXNOW_KEY)


def extra_public_actors(token):
    """Map of public actor name -> minimal dict for related links (including those without a guide)."""
    req = urllib.request.Request(
        "https://api.apify.com/v2/acts?my=1&limit=100",
        headers={"Authorization": f"Bearer {token}"},
    )
    out = {}
    for it in json.load(urllib.request.urlopen(req))["data"]["items"]:
        if it.get("isPublic"):
            out[it["name"]] = {
                "name": it["name"],
                "slug": None,
                "title": it.get("title") or it["name"],
            }
    return out


def render_product_page(p, actors_by_name, out_dir, page_fn, store, today, escape):
    """Build HTML for one PRODUCT landing page using the site's page() helper."""
    E = escape
    preview_path = os.path.join(out_dir, p["preview_csv"])
    sample_rows = []
    if os.path.exists(preview_path):
        with open(preview_path, encoding="utf-8-sig", newline="") as f:
            sample_rows = list(csv.DictReader(f))[:5]

    def money(v):
        try:
            return f"{float(str(v).replace(',', '')):,.0f}"
        except Exception:
            return v or "—"

    rows_html = ""
    if sample_rows:
        trs = []
        for r in sample_rows:
            title = (r.get("Title (English)") or "")[:90]
            buyer = (r.get("Buyer (public body)") or "")[:50]
            trs.append(
                "<tr>"
                f"<td>{E(r.get('Deadline') or '')}</td>"
                f"<td>{E(r.get('Country') or '')}</td>"
                f"<td>{E(title)}</td>"
                f"<td>{E(buyer)}</td>"
                f"<td>{E(money(r.get('Estimated value (EUR, approx.)')))}</td>"
                "</tr>"
            )
        rows_html = (
            "<h2>Sample rows from the free preview</h2>"
            '<table class="sample"><thead><tr>'
            "<th>Deadline</th><th>Country</th><th>Title (English)</th>"
            "<th>Buyer</th><th>Est. value (EUR)</th>"
            "</tr></thead>"
            f"<tbody>{''.join(trs)}</tbody></table>"
            f'<p class="mut">Showing 5 of 20 free preview rows. '
            f'<a href="../{E(p["preview_csv"])}">Download the full free preview CSV</a>.</p>'
        )

    related = []
    for name, label in [
        ("ted-tenders-scraper", "TED EU Tenders Scraper"),
        ("eu-grants-scraper", "EU Grants Scraper"),
        ("us-uk-tenders-scraper", "SAM.gov & UK Contracts Finder Tenders Scraper"),
    ]:
        a = actors_by_name.get(name)
        if a and a.get("slug"):
            related.append(
                f'<li><a href="../{E(a["slug"])}/">{E(label)}</a> · '
                f'<a href="{store}{name}">Apify Store</a></li>'
            )
        else:
            related.append(f'<li><a href="{store}{name}">{E(label)}</a> on Apify Store</li>')
    related_html = "<ul>" + "".join(related) + "</ul>"

    body = f"""<h1>{E(p['h1'])}</h1>
<p class="mut">Updated {today} · Weekly Excel/CSV data product · Built from public TED + EU Funding &amp; Tenders data</p>
<p>Every week: open public <strong>IT and software tenders</strong> from TED across Europe, plus open and upcoming <strong>EU digital grant calls</strong> (Horizon Europe, Digital Europe and more) — English titles, deadlines, values and direct links, in one Excel file (plus CSV).</p>
<p>Stop checking TED and the Funding &amp; Tenders Portal by hand. Get the filtered, English-ready file every Monday.</p>
<p>
<a class="cta row" href="../{E(p['preview_csv'])}">Download free 20-row preview CSV →</a>
<a class="cta row" href="{E(p['membership'])}">Subscribe $19/mo or $149/yr →</a>
<a class="cta sec row" href="{E(p['single'])}">Buy this week's issue $9 →</a>
</p>
<div class="pricebox">
<h2 style="margin-top:0">Get the full weekly file</h2>
<ul>
<li><strong>Membership</strong> — <a href="{E(p['membership'])}">$19/month or $149/year</a>: every Monday's Excel + CSV in your Gumroad library (cancel anytime).</li>
<li><strong>Single issue</strong> — <a href="{E(p['single'])}">$9</a>: buy only this week's file.</li>
<li><strong>Free preview</strong> — <a href="../{E(p['preview_csv'])}">20 open IT tenders as CSV</a> (same columns as the paid file).</li>
</ul>
</div>
<h2>What's in the full file</h2>
<ul>
<li><strong>IT &amp; software tenders</strong> (CPV 72 + 48): English title, original title, buyer, country, CPV, estimated value (and approx. EUR), deadline, days left, TED notice + documents links.</li>
<li><strong>EU digital grant calls</strong>: programme, deadlines, topic budget, EU contribution per project, real open/forthcoming status, portal link.</li>
<li><strong>Summary sheet</strong>: tenders by country/CPV and grants by programme.</li>
</ul>
{rows_html}
<h2>Sources and licence</h2>
<p>Tender rows come from <a href="https://ted.europa.eu">TED (Tenders Electronic Daily)</a>, © European Union, reuse under <a href="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32011D0833">Commission Decision 2011/833/EU</a>. Grant rows come from the <a href="https://ec.europa.eu/info/funding-tenders/opportunities/portal/">EU Funding &amp; Tenders Portal</a> (reuse under the same Decision / CC BY where applicable). This product is <strong>not affiliated with</strong> the European Union, the Publications Office or the European Commission. Always verify the official notice before bidding or applying. English titles that were not published in English may be machine-translated; the original title is kept in the file.</p>
<h2>Related Apify actors</h2>
<p>Prefer to pull the raw data yourself on a schedule? Use these TinyRex actors on Apify:</p>
{related_html}
<p>
<a class="cta row" href="../{E(p['preview_csv'])}">Free preview CSV</a>
<a class="cta row" href="{E(p['membership'])}">Subscribe on Gumroad</a>
<a class="cta sec row" href="{E(p['single'])}">Single issue $9</a>
</p>"""
    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "EU IT Tenders & Grants Weekly",
        "description": p["desc"],
        "brand": {"@type": "Brand", "name": "TinyRex"},
        "offers": [
            {"@type": "Offer", "price": "19.00", "priceCurrency": "USD", "url": p["membership"], "description": "Monthly membership"},
            {"@type": "Offer", "price": "149.00", "priceCurrency": "USD", "url": p["membership"], "description": "Yearly membership"},
            {"@type": "Offer", "price": "9.00", "priceCurrency": "USD", "url": p["single"], "description": "Single weekly issue"},
        ],
    }
    return page_fn(f"{p['slug']}/", p["ptitle"], p["desc"], body, ld)
