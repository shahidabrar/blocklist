name: Build Blocklist

on:
  workflow_dispatch:
  schedule:
    - cron: "0 2 * * *"

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install + Build
        run: |
          pip install requests
          rm -f final.txt final.gz final.txt.gz
          python build.py
          wc -l final.txt
          ls -lh final.*

      - name: Push to root
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add -f final.txt final.gz final.txt.gz
          git diff --cached --quiet || git commit -m "Update $(date -u +%Y-%m-%d) - $(wc -l < final.txt) domains"
          git push
