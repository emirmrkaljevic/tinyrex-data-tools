#!/usr/bin/env bash
# One-time publish of the TinyRex guide site to GitHub Pages (needs `gh auth login` as emirmrkaljevic).
set -euo pipefail
cd "$(dirname "$0")"
REPO=tinyrex-data-tools
gh repo create "$REPO" --public --source . --push \
  --description "Guides & API examples: bulk tech stack lookup (Wappalyzer alternative), Greenhouse/Workday jobs, Shopify/WooCommerce export, TED EU tenders" \
  --homepage "https://emirmrkaljevic.github.io/$REPO/"
gh api -X POST "repos/emirmrkaljevic/$REPO/pages" -f "source[branch]=main" -f "source[path]=/docs"
gh repo edit "emirmrkaljevic/$REPO" --add-topic web-scraping,scraper,apify,api,mcp,wappalyzer-alternative,builtwith-alternative,greenhouse,workday,shopify,woocommerce,ted-tenders,public-procurement,job-scraper,data-extraction,python,csv-export
echo "Site: https://emirmrkaljevic.github.io/$REPO/"
