#!/bin/bash
# Builds the five shortcut apps (Kahf, Baqarah, morning and evening adhkar, ruqyah) and installs them on the TV.
# The Kahf app also carries the reminders, the adhan and the phone message page, so it gets the overlay
# and usage-access permissions and is started once.
# Usage: tools/install-noor.sh <tv-ip>
set -e
D="$1:5555"; [ -n "$1" ] || { echo "usage: $0 <tv-ip>"; exit 1; }
cd "$(dirname "$0")/../noor-app"
./gradlew -q assembleRelease
for f in kahf baqara sabah masa ruqya; do
  adb -s "$D" install -r "app/build/outputs/apk/$f/release/app-$f-release.apk" >/dev/null && echo "✅ $f"
done
adb -s "$D" shell appops set app.noortv.kahf SYSTEM_ALERT_WINDOW allow
adb -s "$D" shell appops set app.noortv.kahf GET_USAGE_STATS allow
adb -s "$D" shell am broadcast -n app.noortv.kahf/app.noortv.Reminder >/dev/null
echo "Phone page: http://$1:8080"
