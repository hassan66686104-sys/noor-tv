#!/usr/bin/env python3
"""Adds the Noor line to the CleanYourTV launcher: Hijri date, weather and the next prayer under the clock,
«جمعة مباركة» on Friday and «الأيام البيض» on the 13th to 15th. Also points the prayer-times addon at your city.

    python3 apply.py <cleanyourtv folder> <lat> <lon> <aladhan method> "<city name>"

Safe to run twice. Afterwards: build and install the launcher (launcher/build-and-install.sh) and the
prayer-times addon, then turn on shamsi_date in the theme (that is the line Noor writes into).
"""
import pathlib
import re
import sys

if len(sys.argv) != 6:
    sys.exit(__doc__)
root, lat, lon, method, city = pathlib.Path(sys.argv[1]), *sys.argv[2:]
float(lat), float(lon), int(method)  # fail early on a typo
here = pathlib.Path(__file__).resolve().parent
src = root / "launcher/app/src/main"


def patch(path, old, new, done_marker):
    text = path.read_text(encoding="utf-8")
    if done_marker in text:
        return
    if old not in text:
        sys.exit(f"Could not find the spot to change in {path} - the launcher changed upstream; patch it by hand.")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


noor = (here / "Noor.java").read_text(encoding="utf-8")
noor = noor.replace("@LAT@", lat).replace("@LON@", lon).replace("@METHOD@", method)
(src / "java/com/gathin/tvhome/Noor.java").write_text(noor, encoding="utf-8")

patch(src / "AndroidManifest.xml",
      '    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />',
      '    <uses-permission android:name="android.permission.INTERNET" />\n'
      '    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />',
      'android.permission.INTERNET')

patch(src / "java/com/gathin/tvhome/MainActivity.java",
      "        if (shamsi) shamsiDate.setText(Shamsi.today(getResources()));",
      "        String noorGreeting = Noor.greeting();\n"
      "        if (noorGreeting != null && festiveGreeting.isEmpty()) greeting.setText(noorGreeting);\n"
      "        if (shamsi) {\n"
      "            shamsiDate.setText(Noor.line());\n"
      "            shamsiDate.setTextColor(Noor.whiteDay() ? 0xFFFFE08A : 0xE6FFFFFF);\n"
      "        }",
      "Noor.line()")

layout = src / "res/layout/activity_main.xml"
text = layout.read_text(encoding="utf-8")
m = re.search(r'android:id="@\+id/shamsiDate".*?/>', text, re.S)
if not m:
    sys.exit(f"Could not find shamsiDate in {layout}")
block = m.group(0)
if 'android:maxLines="2"' not in block:
    new = block.replace('android:singleLine="true"', 'android:maxLines="2"\n                            android:lineSpacingExtra="4dp"')
    layout.write_text(text.replace(block, new), encoding="utf-8")

cfg = root / "addons/prayer-times/app/src/main/res/values/config.xml"
text = cfg.read_text(encoding="utf-8")
for name, value in (("latitude", lat), ("longitude", lon), ("place", city), ("method", method)):
    text = re.sub(rf'(<string name="{name}"[^>]*>)[^<]*(</string>)', rf"\g<1>{value}\g<2>", text)
text = re.sub(r'(<bool name="reminders">)\w+(</bool>)', r"\g<1>true\g<2>", text)
cfg.write_text(text, encoding="utf-8")
print("Noor patch applied:", city, lat, lon, "method", method)
