import re
from django.test import Client

c = Client(SERVER_NAME="127.0.0.1")
r = c.get("/", HTTP_HOST="127.0.0.1")
html = r.content.decode("utf-8")

# Find the featured articles section
m = re.search(r"<!--\s*featured.*?-->|Insight ใหม่", html)

# Locate the section
i = html.find("Insight")
if i == -1:
    print("NO Insight section found")
else:
    section = html[i:i + 5000]

    # Extract <h3> titles
    print("=== Featured Articles section content ===\n")
    titles = re.findall(r'<h3[^>]*>(.*?)</h3>', section)
    for t in titles[:5]:
        print(f"  • {t.strip()}")
    print()

    # Cover images referenced
    covers = re.findall(r'background-image:url\([\'"]?([^\'")]+)[\'"]?\)', section)
    print(f"Cover images in section: {len(covers)}")
    for c in covers[:5]:
        print(f"  - {c}")
    print()

    # Categories shown
    cats = re.findall(r'text-uppercase[^>]*>(.*?)</small>', section)
    print(f"Category labels: {[c.strip() for c in cats[:5]]}")
