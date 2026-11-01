"""Validate the self-contained public site using only Python's standard library."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
errors = []


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.urls = []
        self.h1_count = 0
        self.project_count = 0
        self.lang = None
        self.viewport = False
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = "width=device-width" in attrs.get("content", "")
        if tag == "h1":
            self.h1_count += 1
        if "project-card" in attrs.get("class", "").split():
            self.project_count += 1
        for key in ("href", "src"):
            if key in attrs:
                self.urls.append(attrs[key])
        if attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", "").split():
            errors.append(f"New-tab link lacks noopener: {attrs.get('href')}")
        if tag == "img" and "alt" not in attrs:
            errors.append("Image lacks alternative text")

    def handle_data(self, data):
        self.text.append(data)


parser = SiteParser()
html = (SITE / "index.html").read_text(encoding="utf-8")
parser.feed(html)
for identifier, count in Counter(parser.ids).items():
    if count > 1:
        errors.append(f"Duplicate id: {identifier}")
for required in ("main", "about", "projects", "experience", "credentials", "contact"):
    if required not in parser.ids:
        errors.append(f"Missing required section: {required}")
if parser.lang != "zh-Hant" or not parser.viewport:
    errors.append("Missing Traditional Chinese language or responsive viewport")
if parser.h1_count != 1:
    errors.append(f"Expected one h1, found {parser.h1_count}")
if parser.project_count != 4:
    errors.append(f"Expected four curated projects, found {parser.project_count}")

linked_pdfs = set()
for url in parser.urls:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        continue
    if not parsed.path:
        if parsed.fragment and unquote(parsed.fragment) not in parser.ids:
            errors.append(f"Broken anchor: {url}")
        continue
    if parsed.path.startswith("/"):
        errors.append(f"Root-relative link would break project Pages hosting: {url}")
        continue
    target = (SITE / unquote(parsed.path)).resolve()
    if not target.is_relative_to(SITE.resolve()):
        errors.append(f"Link escapes the public site: {url}")
    elif not target.is_file():
        errors.append(f"Missing linked file: {url}")
    if target.suffix == ".pdf":
        linked_pdfs.add(target)

pdfs = set((SITE / "assets/documents").glob("*.pdf"))
if len(pdfs) != 16:
    errors.append(f"Expected 16 public PDF files, found {len(pdfs)}")
for pdf in pdfs:
    if pdf.resolve() not in linked_pdfs:
        errors.append(f"PDF has no website entry: {pdf.name}")
    with pdf.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            errors.append(f"Invalid PDF header: {pdf.name}")

for file in SITE.rglob("*"):
    if not file.is_file():
        continue
    if file.suffix not in {".html", ".css", ".js", ".svg", ".pdf"} and file.name != ".nojekyll":
        errors.append(f"Unexpected public file: {file.relative_to(SITE)}")
    if any(word in file.name.lower() for word in ("履歷", "resume", "credential-token", ".env")):
        errors.append(f"Private file in public site: {file.name}")

visible_text = " ".join(parser.text)
for private_phrase in ("家庭背景", "我的父親", "我的母親"):
    if private_phrase in visible_text:
        errors.append("Private reference content found in public HTML")
if re.search(r"09\d{2}[- ]?\d{3}[- ]?\d{3}", visible_text):
    errors.append("A personal mobile phone number appears in public HTML")
if "mailto:leezr34@gmail.com" not in parser.urls:
    errors.append("Missing working contact email")
if errors:
    print("Site validation failed:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
print(f"PASS: {parser.project_count} projects, {len(pdfs)} linked PDFs, {len(parser.ids)} unique IDs.")
print("PASS: local links, anchors, public file allowlist, contact and required sections.")

