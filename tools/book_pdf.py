"""Makes the book-page PDFs for "What Your Body Forgot" in Noto Sans (Kahu Phil's own font files in static/fonts/).

One design for the Introduction and for every chapter, so a later chapter only needs its own Word file:

    python tools/book_pdf.py chapter  <chapter.docx> <out.pdf> --number 1
    python tools/book_pdf.py intro    content_text/smoke_is_not_the_fire.json <out.pdf>

Why a browser engine: Chromium shapes text properly, so the Hawaiian okina and kahako, and the Hebrew vowel marks in the
word studies, come out right (a plain PDF library places combining marks wrongly). The running line at the top of every
page, "What Your Body Forgot, Chapter 1", is a CSS page header, so it is on every page including the first.

Needs: python-docx and playwright (with Chromium) -- tools for making the files, not part of the running website.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "static" / "fonts"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEBREW = re.compile(r"[֐-׿יִ-ﭏ]+")

CSS = """
@font-face { font-family: 'Noto Sans'; font-weight: 400; font-style: normal; src: url('%(f)s/NotoSans-Regular.ttf'); }
@font-face { font-family: 'Noto Sans'; font-weight: 700; font-style: normal; src: url('%(f)s/NotoSans-Bold.ttf'); }
@font-face { font-family: 'Noto Sans'; font-weight: 400; font-style: italic; src: url('%(f)s/NotoSans-Italic.ttf'); }
@font-face { font-family: 'Noto Sans'; font-weight: 700; font-style: italic; src: url('%(f)s/NotoSans-BoldItalic.ttf'); }
@font-face { font-family: 'Noto Sans Hebrew'; font-weight: 400; src: url('%(f)s/NotoSansHebrew-Regular.ttf'); }
@font-face { font-family: 'Noto Sans Hebrew'; font-weight: 700; src: url('%(f)s/NotoSansHebrew-Bold.ttf'); }
@page {
  size: 6in 9in; margin: 0.9in 0.8in 0.85in 0.8in;
  @top-center { content: "%(header)s"; font-family: 'Noto Sans'; font-size: 8.5pt; color: #555; letter-spacing: 0.04em; }
  @bottom-center { content: counter(page); font-family: 'Noto Sans'; font-size: 9pt; color: #555; }
}
html { font-family: 'Noto Sans', 'Noto Sans Hebrew'; font-size: 10.5pt; line-height: 1.6; color: #1b1b1b; }
body { margin: 0; }
p { margin: 0 0 0.75em; orphans: 3; widows: 3; }
h1 { font-size: 25pt; line-height: 1.2; text-align: center; margin: 0.4in 0 0.2in; }
.kicker { text-align: center; font-size: 9pt; letter-spacing: 0.18em; text-transform: uppercase; color: #8a6d1a; margin: 0.2in 0 0; font-weight: 700; }
.byline { text-align: center; color: #555; margin-bottom: 0.4in; font-style: italic; }
h2 { font-size: 14pt; margin: 1.5em 0 0.5em; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 1.2em 0 0.4em; break-after: avoid; }
.epigraph { margin: 0.3in 0.35in 0.1em; font-style: italic; text-align: center; }
.attrib { text-align: center; color: #555; margin-bottom: 0.3in; }
ul, ol { margin: 0 0 0.8em 1.2em; padding: 0; }
li { margin-bottom: 0.3em; }
.care { background: #f3efe3; border-left: 3px solid #8a6d1a; padding: 0.6em 0.9em; margin: 1em 0; break-inside: avoid; }
.hebrew { font-family: 'Noto Sans Hebrew'; direction: rtl; unicode-bidi: isolate; }
.word { text-align: center; margin: 1.2em 0 0.2em; break-after: avoid; }
.word .he { font-size: 20pt; line-height: 1.3; }
.word .tr { font-weight: 700; }
.defn { border-left: 3px solid #bbb; padding-left: 0.8em; margin: 0 0 0.9em 0.35in; break-inside: avoid; }
.line { border-bottom: 0.6pt solid #888; height: 0.34in; }
.day { font-weight: 700; margin: 0.9em 0 0; break-after: avoid; }
.glance { border-left: 3px solid #bbb; padding-left: 0.7em; margin: 0 0 0.5em 0.15in; break-inside: avoid; }
.source { font-size: 8.5pt; line-height: 1.45; margin: 0 0 0.45em 0.2in; text-indent: -0.2in; padding-left: 0.2in; }
.colophon { text-align: center; color: #555; font-size: 9pt; border-top: 0.6pt solid #888; padding-top: 0.6em; margin-top: 1.4em; }
.pb { break-before: page; }
.intro p { margin-bottom: 0.7em; }
"""


def esc(text):
    return html.escape(text, quote=False)


def mark_hebrew(escaped):
    return HEBREW.sub(lambda m: '<span class="hebrew" lang="he">' + m.group(0) + "</span>", escaped)


def runs_html(paragraph):
    out = []
    for run in paragraph.runs:
        text = mark_hebrew(esc(run.text))
        if not text:
            continue
        if run.bold:
            text = "<strong>" + text + "</strong>"
        if run.italic:
            text = "<em>" + text + "</em>"
        out.append(text)
    return "".join(out)


def list_kind(document, paragraph):
    num_pr = paragraph._p.pPr.numPr if paragraph._p.pPr is not None else None
    if num_pr is None:
        return None
    numbering = document.part.numbering_part.element
    abstract = {}
    for a in numbering.findall(W + "abstractNum"):
        abstract[a.get(W + "abstractNumId")] = a.find(W + "lvl").find(W + "numFmt").get(W + "val")
    for n in numbering.findall(W + "num"):
        if n.get(W + "numId") == str(num_pr.numId.val):
            fmt = abstract[n.find(W + "abstractNumId").get(W + "val")]
            return ("ol" if fmt == "decimal" else "ul", str(num_pr.numId.val))
    return ("ul", str(num_pr.numId.val))


def chapter_body(docx_path, number):
    import docx
    document = docx.Document(docx_path)
    paragraphs = document.paragraphs
    out, pending_list, break_next = [], None, False

    def flush_list():
        nonlocal pending_list
        if pending_list:
            tag, items = pending_list[0], pending_list[2]
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % i for i in items), tag))
            pending_list = None

    def add(markup):
        nonlocal break_next
        flush_list()
        if break_next:
            out.append('<div class="pb"></div>')
            break_next = False
        out.append(markup)

    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        i += 1
        text = p.text
        style = p.style.name
        xml = p._p.xml
        indent = p.paragraph_format.left_indent
        centered = p.alignment is not None and int(p.alignment) == 1
        bordered = "<w:pBdr>" in xml
        if "w:br w:type=\"page\"" in xml and not text.strip():
            flush_list()
            break_next = True
            continue
        if text.strip().startswith("THE ROTTEN FENCEPOST") and "CHAPTER" in text:
            continue                                   # replaced by the running header on every page
        if style == "Heading 1":
            add('<div class="kicker">Chapter %s</div><h1>%s</h1>' % (number, runs_html(p) if p.runs else esc(text)))
            continue
        if style == "Heading 2":
            add("<h2>%s</h2>" % esc(text))
            continue
        if style == "Heading 3":
            add("<h3>%s</h3>" % esc(text))
            continue
        kind = list_kind(document, p)
        if kind:
            if pending_list and pending_list[1] != kind[1]:
                flush_list()
            if not pending_list:
                pending_list = [kind[0], kind[1], []]
            pending_list[2].append(runs_html(p))
            continue
        if not text.strip():
            if bordered:
                add('<div class="line"></div>')
            continue
        if indent == 457200 and p.runs and p.runs[0].italic and not bordered:
            add('<p class="epigraph">%s</p>' % runs_html(p))
            continue
        if centered and text.startswith("—"):
            add('<p class="attrib">%s</p>' % esc(text))
            continue
        if HEBREW.search(text) and centered and not bordered:
            transliteration = paragraphs[i] if i < len(paragraphs) else None
            add('<div class="word"><div class="he hebrew" lang="he">%s</div><div class="tr">%s</div></div>'
                % (esc(text), esc(transliteration.text) if transliteration is not None else ""))
            i += 1
            continue
        if bordered and indent == 457200:
            add('<div class="defn">%s</div>' % runs_html(p))
            continue
        if bordered and indent == 152400:
            add('<div class="glance">%s</div>' % runs_html(p))
            continue
        if bordered and "<w:shd" in xml:
            add('<div class="care">%s</div>' % runs_html(p))
            continue
        if bordered and centered:
            add('<div class="colophon">%s</div>' % esc(text))
            continue
        if indent == 228600:
            add('<p class="source">%s</p>' % runs_html(p))
            continue
        if re.fullmatch(r"Day \d", text.strip()):
            add('<div class="day">%s</div>' % esc(text.strip()))
            continue
        if centered:
            add('<p style="text-align:center">%s</p>' % runs_html(p))
            continue
        add("<p>%s</p>" % runs_html(p))
    flush_list()
    return "\n".join(out)


def intro_body(json_path):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    rows = ['<div class="kicker">Introduction</div>', "<h1>%s</h1>" % esc(data["title"]),
            '<p class="byline">Kahu Phil Stephens</p>', '<div class="intro">']
    rows += ["<p>%s</p>" % esc(t) for t in data["paragraphs"]]
    rows.append("</div>")
    return "\n".join(rows)


def render_pdf(body, header, out_pdf):
    from playwright.sync_api import sync_playwright
    page_html = "<!doctype html><html lang='en'><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (
        CSS % {"f": FONTS.as_uri(), "header": header.replace('"', "'")}, body)
    out_pdf = Path(out_pdf).resolve()
    tmp = out_pdf.with_suffix(".html")
    tmp.write_text(page_html, encoding="utf-8")
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.goto(tmp.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(500)
            page.pdf(path=str(out_pdf), prefer_css_page_size=True, print_background=True)
            browser.close()
    finally:
        tmp.unlink(missing_ok=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["chapter", "intro"])
    ap.add_argument("source")
    ap.add_argument("out")
    ap.add_argument("--number", default="1")
    args = ap.parse_args(argv)
    if args.kind == "chapter":
        body = chapter_body(args.source, args.number)
        header = "What Your Body Forgot, Chapter %s" % args.number
    else:
        body = intro_body(args.source)
        header = "What Your Body Forgot, Introduction"
    render_pdf(body, header, args.out)
    print("wrote", args.out)


if __name__ == "__main__":
    sys.exit(main())
