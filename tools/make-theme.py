#!/usr/bin/env python3
"""Builds a theme folder ready for CleanYourTV's tools/theme.sh: the shape (themes/<name>) on top of the
base dock (theme/config.json), plus this TV's remote keys.
Usage: tools/make-theme.py <zakhrafa|masjid-layl|awqat|plain> <out-folder> [brand-example-config.json]"""
import json, os, shutil, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, out = sys.argv[1], sys.argv[2]
config = json.load(open(f"{root}/theme/config.json", encoding="utf8"))
shutil.rmtree(out, ignore_errors=True)
if name == "plain":
    os.makedirs(out)
else:
    shutil.copytree(f"{root}/themes/{name}", out)
    config.update(json.load(open(f"{root}/themes/{name}/config.json", encoding="utf8")))
if len(sys.argv) > 3:
    brand = json.load(open(sys.argv[3], encoding="utf8"))
    for key in ("live_tv_package", "settings_key_keycodes", "settings_key_panel", "app_keys"):
        if key in brand:
            config[key] = brand[key]
json.dump(config, open(f"{out}/config.json", "w", encoding="utf8"), ensure_ascii=False, indent=2)
print(out)
