#!/usr/bin/env python3
"""Check if template needs update."""

import os
from datetime import datetime, timedelta

TEMPLATE_FILE = "docs/ROTA_DE_TESTES_TEMPLATE.md"
MAX_AGE_DAYS = 90

print("=" * 60)
print("TEMPLATE UPDATE CHECK")
print("=" * 60)

if not os.path.exists(TEMPLATE_FILE):
    print(f"ERROR: Template not found: {TEMPLATE_FILE}")
    exit(1)

mtime = os.path.getmtime(TEMPLATE_FILE)
last_modified = datetime.fromtimestamp(mtime)
age = datetime.now() - last_modified

print(f"Template: {TEMPLATE_FILE}")
print(f"Last modified: {last_modified.strftime('%Y-%m-%d')}")
print(f"Age: {age.days} days")
print()

if age.days > MAX_AGE_DAYS:
    print("WARNING: Template is outdated!")
    print()
    print("Run these skills to update:")
    print("  - skill('skill-scout')")
    print("  - skill('skill-stocktake')")
    print("  - skill('documentation-lookup')")
    exit(1)
else:
    print("OK: Template is up to date!")
    next_review = datetime.now() + timedelta(days=MAX_AGE_DAYS)
    print(f"Next review: {next_review.strftime('%Y-%m-%d')}")
    exit(0)
