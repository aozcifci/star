#!/usr/bin/env python3
"""Build the EPUB 3 package for 'Milo and the Volcano Inside' (Milo's Pocket Powers, Book 1)."""
import os
import shutil
import zipfile

ASSETS = "/opt/cursor/artifacts/assets"
OUT = "/workspace/milo-and-the-volcano-inside.epub"

XHTML_HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="../css/style.css"/>
</head>
<body>
"""
XHTML_FOOT = "</body>\n</html>\n"

CSS = """
body { margin: 0; padding: 0; background: #F7F0E3; font-family: "Georgia", "Times New Roman", serif; color: #2E4057; }
.page { text-align: center; padding: 1em; }
.page img { max-width: 100%; height: auto; border-radius: 6px; }
.story { font-size: 1.25em; line-height: 1.6; margin: 0.8em auto 0 auto; max-width: 30em; text-align: center; }
.story .shout { font-weight: bold; letter-spacing: 0.05em; }
h1, h2 { font-family: "Georgia", serif; color: #E85D4A; text-align: center; }
h1 { font-size: 1.9em; margin: 0.6em 0 0.2em 0; }
h2 { font-size: 1.4em; }
.subtitle { text-align: center; color: #2E4057; font-style: italic; margin-top: 0; }
.rhyme { font-size: 1.3em; line-height: 1.8; font-style: italic; text-align: center; margin-top: 0.8em; }
.slogan { font-weight: bold; font-style: normal; color: #E85D4A; }
.backmatter { max-width: 32em; margin: 0 auto; padding: 1.5em; font-size: 1.05em; line-height: 1.6; }
.backmatter li { margin-bottom: 0.6em; }
.badge-note { text-align: center; font-style: italic; color: #8a7f6a; }
.copyright { font-size: 0.85em; color: #8a7f6a; text-align: center; margin-top: 2em; }
"""

def img_page(fname, title, img, paragraphs, cls="story"):
    body = f'<div class="page"><img src="../images/{img}" alt="{title}"/>\n'
    for p in paragraphs:
        body += f'<p class="{cls}">{p}</p>\n'
    body += "</div>\n"
    return fname, XHTML_HEAD.format(title=title) + body + XHTML_FOOT

pages = []

# Cover
pages.append(("cover.xhtml", XHTML_HEAD.format(title="Cover")
    + '<div class="page"><img src="../images/book1-cover.png" alt="Milo and the Volcano Inside — cover"/></div>\n'
    + XHTML_FOOT))

# Title page
pages.append(("title.xhtml", XHTML_HEAD.format(title="Title Page")
    + '<div class="page">'
    + '<h1>Milo and the Volcano Inside</h1>'
    + '<p class="subtitle">Milo&#8217;s Pocket Powers &#8226; Book 1</p>'
    + '<p class="subtitle">Little tricks for BIG feelings!</p>'
    + '<img src="../images/book1-p01-title.png" alt="Milo&#8217;s red sneakers next to Pia&#8217;s tiny shoes by the front door"/>'
    + '<p class="copyright">Text and illustrations &#169; 2026. All rights reserved.</p>'
    + '</div>\n' + XHTML_FOOT))

story = [
    ("p02.xhtml", "Milo", "book1-p02-03-intro.png",
     ["This is Milo. Milo loves three things: building towers, racing his toy cars, and his little sister Pia&#8230; <em>most</em> of the time."]),
    ("p04.xhtml", "The Tallest Tower", "book1-p04-05-pride.png",
     ["Today, Milo built the tallest tower EVER. Taller than the chair! Taller than the lamp! Almost as tall as Milo himself."]),
    ("p06.xhtml", "Crash", "book1-p06-07-crash.png",
     ["Then&#8230; <span class=\"shout\">CRASH!</span> Pia wanted to hug the tower. Towers do not like hugs."]),
    ("p08.xhtml", "Something Hot", "book1-p08-09-rising.png",
     ["Something hot woke up in Milo&#8217;s tummy. It bubbled. It rumbled. It rose up, up, up &#8212; like a volcano."]),
    ("p10.xhtml", "The Eruption", "book1-p10-11-eruption.png",
     ["<span class=\"shout\">&#8220;PIAAAAA!&#8221;</span> Milo roared. He stomped his feet. He squeezed his fists. His face turned red as a fire truck."]),
    ("p12.xhtml", "Stubborn Volcano", "book1-p12-13-failed.png",
     ["Milo tried to squish the volcano down. But squishing made it bigger.",
      "He tried yelling into his pillow. But the volcano just yelled back."]),
    ("p14.xhtml", "All Alone", "book1-p14-15-lowpoint.png",
     ["Pia started to cry. Mom looked tired. And Milo felt hot and prickly and all alone."]),
    ("p16.xhtml", "Grandpa Joe", "book1-p16-17-grandpa.png",
     ["That&#8217;s when Grandpa Joe peeked in. &#8220;Whoa! A volcano!&#8221; he said. &#8220;Good thing I keep a Pocket Power just for volcanoes.&#8221;"]),
    ("p18.xhtml", "The Balloon Breath", "book1-p18-19-teaching.png",
     ["&#8220;It&#8217;s called the Balloon Breath. Breathe in through your nose &#8212; fill the balloon. Blow out through your mouth &#8212; sloooowly let it fly.&#8221;"]),
    ("p20.xhtml", "Try Again", "book1-p20-21-firsttry.png",
     ["Milo tried. Sniff&#8230; whoooosh. The volcano still grumbled.",
      "&#8220;Volcanoes are stubborn,&#8221; said Grandpa Joe. &#8220;Try again.&#8221;"]),
    ("p22.xhtml", "Smaller and Smaller", "book1-p22-23-itworks.png",
     ["Sniff&#8230; whoooooooosh. The hot feeling got smaller.",
      "Sniff&#8230; whooooooooooosh. Smaller. And smaller. Until the volcano was just a warm little pebble."]),
    ("p24.xhtml", "Together", "book1-p24-25-repair.png",
     ["Milo looked at the blocks. He looked at Pia&#8217;s wet cheeks.",
      "&#8220;You didn&#8217;t mean it,&#8221; he said. &#8220;Want to build one together?&#8221;"]),
    ("p26.xhtml", "The Best Tower Ever", "book1-p26-27-victory.png",
     ["They built a new tower. It was crooked. It was wobbly. It was the BEST tower ever &#8212; because they built it together."]),
]
for f, t, i, ps in story:
    pages.append(img_page(f, t, i, ps))

# Rhyming closer
pages.append(("p28.xhtml", XHTML_HEAD.format(title="Little Tricks for Big Feelings")
    + '<div class="page"><img src="../images/book1-p28-29-closer.png" alt="Milo winks at the reader holding the Balloon Breath badge"/>'
    + '<p class="rhyme">When the volcano wakes and starts to blow,<br/>'
    + 'fill your balloon and let it go.<br/>'
    + 'Big feelings come, big feelings pass &#8212;<br/>'
    + '<span class="slogan">Little tricks for BIG feelings!</span></p></div>\n'
    + XHTML_FOOT))

# For Grown-Ups
pages.append(("p30.xhtml", XHTML_HEAD.format(title="For Grown-Ups")
    + '<div class="backmatter"><h2>For Grown-Ups: Taming Volcanoes Together</h2>'
    + '<p><strong>Talk together:</strong></p><ul>'
    + '<li>&#8220;Where do you feel anger in your body?&#8221;</li>'
    + '<li>&#8220;What does <em>your</em> volcano feel like &#8212; hot, bubbly, loud?&#8221;</li>'
    + '<li>&#8220;What made Milo&#8217;s volcano shrink?&#8221;</li></ul>'
    + '<p><strong>Three tips for coaching the Balloon Breath:</strong></p><ol>'
    + '<li>Practice when everyone is <em>calm</em>, so the Balloon Breath feels familiar during a real storm.</li>'
    + '<li>Name the feeling first (&#8220;You&#8217;re really angry &#8212; your volcano is awake&#8221;), teach second.</li>'
    + '<li>Model it: let your child see <em>you</em> use the Balloon Breath when you&#8217;re frustrated.</li></ol>'
    + '</div>\n' + XHTML_FOOT))

# Activity page
pages.append(("p31.xhtml", XHTML_HEAD.format(title="Activity Page")
    + '<div class="backmatter"><h2>Your Turn!</h2>'
    + '<p><strong>1. Draw YOUR volcano!</strong> What color is it? Is it big or small? Where does it live in your body? Grab paper and crayons and draw it.</p>'
    + '<p><strong>2. The Balloon Breath, step by step:</strong></p><ol>'
    + '<li>Breathe in slowly through your <strong>nose</strong> &#8212; fill the balloon.</li>'
    + '<li>Feel your tummy grow round like a balloon.</li>'
    + '<li>Blow out sloooowly through your <strong>mouth</strong> &#8212; let the balloon fly!</li>'
    + '<li>Do it three times. Is your volcano smaller?</li></ol>'
    + '</div>\n' + XHTML_FOOT))

# Series page
pages.append(("p32.xhtml", XHTML_HEAD.format(title="More Pocket Powers")
    + '<div class="backmatter"><h2>Milo has more Pocket Powers!</h2>'
    + '<p class="badge-note">You unlocked: <strong>The Balloon Breath</strong> &#127880;</p>'
    + '<p>Coming next: <em>Milo and the Worry Cloud</em> (Book 2), where Nana Rose shares a Pocket Power for worries.</p>'
    + '<p class="badge-note">Collect all the Pocket Powers!</p>'
    + '<p class="rhyme"><span class="slogan">Little tricks for BIG feelings!</span></p>'
    + '</div>\n' + XHTML_FOOT))

images = [
    "book1-cover.png", "book1-p01-title.png", "book1-p02-03-intro.png",
    "book1-p04-05-pride.png", "book1-p06-07-crash.png", "book1-p08-09-rising.png",
    "book1-p10-11-eruption.png", "book1-p12-13-failed.png", "book1-p14-15-lowpoint.png",
    "book1-p16-17-grandpa.png", "book1-p18-19-teaching.png", "book1-p20-21-firsttry.png",
    "book1-p22-23-itworks.png", "book1-p24-25-repair.png", "book1-p26-27-victory.png",
    "book1-p28-29-closer.png",
]

manifest_items, spine_items = [], []
for f, _ in pages:
    pid = f.replace(".xhtml", "")
    props = ' properties="svg"' if False else ""
    manifest_items.append(f'<item id="{pid}" href="xhtml/{f}" media-type="application/xhtml+xml"{props}/>')
    spine_items.append(f'<itemref idref="{pid}"/>')
for img in images:
    iid = img.replace(".png", "").replace("-", "_")
    cover_prop = ' properties="cover-image"' if img == "book1-cover.png" else ""
    manifest_items.append(f'<item id="{iid}" href="images/{img}" media-type="image/png"{cover_prop}/>')

OPF = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:7f2c9a44-b1e6-4f7d-9c3a-4d8e21f6b0a5</dc:identifier>
    <dc:title>Milo and the Volcano Inside</dc:title>
    <dc:creator>Milo's Pocket Powers</dc:creator>
    <dc:language>en</dc:language>
    <dc:description>When Pia knocks down Milo's tallest tower EVER, something hot wakes up in his tummy. Grandpa Joe teaches him the Balloon Breath — a real calming technique for kids ages 3-7. Book 1 of the Milo's Pocket Powers series. Little tricks for BIG feelings!</dc:description>
    <dc:subject>Anger management for children</dc:subject>
    <meta property="dcterms:modified">2026-08-03T16:00:00Z</meta>
    <meta property="belongs-to-collection" id="series">Milo's Pocket Powers</meta>
    <meta refines="#series" property="collection-type">series</meta>
    <meta refines="#series" property="group-position">1</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="css" href="css/style.css" media-type="text/css"/>
    {chr(10).join('    ' + m for m in manifest_items)}
  </manifest>
  <spine>
    {chr(10).join('    ' + s for s in spine_items)}
  </spine>
</package>
"""

NAV = XHTML_HEAD.format(title="Contents").replace('href="../css/', 'href="css/') + """
<nav epub:type="toc" id="toc">
  <h1>Contents</h1>
  <ol>
    <li><a href="xhtml/cover.xhtml">Cover</a></li>
    <li><a href="xhtml/title.xhtml">Title Page</a></li>
    <li><a href="xhtml/p02.xhtml">The Story</a></li>
    <li><a href="xhtml/p28.xhtml">Little Tricks for BIG Feelings</a></li>
    <li><a href="xhtml/p30.xhtml">For Grown-Ups</a></li>
    <li><a href="xhtml/p31.xhtml">Activity Page</a></li>
    <li><a href="xhtml/p32.xhtml">More Pocket Powers</a></li>
  </ol>
</nav>
""" + XHTML_FOOT

CONTAINER = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

build = "/tmp/epub-build"
shutil.rmtree(build, ignore_errors=True)
os.makedirs(f"{build}/META-INF")
os.makedirs(f"{build}/OEBPS/xhtml")
os.makedirs(f"{build}/OEBPS/images")
os.makedirs(f"{build}/OEBPS/css")

open(f"{build}/mimetype", "w").write("application/epub+zip")
open(f"{build}/META-INF/container.xml", "w").write(CONTAINER)
open(f"{build}/OEBPS/content.opf", "w").write(OPF)
open(f"{build}/OEBPS/nav.xhtml", "w").write(NAV)
open(f"{build}/OEBPS/css/style.css", "w").write(CSS)
for f, content in pages:
    open(f"{build}/OEBPS/xhtml/{f}", "w").write(content)
for img in images:
    shutil.copy(os.path.join(ASSETS, img), f"{build}/OEBPS/images/{img}")

if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w") as z:
    z.write(f"{build}/mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
    for root, _, files in os.walk(build):
        for f in sorted(files):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, build)
            if rel == "mimetype":
                continue
            z.write(full, rel, compress_type=zipfile.ZIP_DEFLATED)

print(f"Built {OUT} ({os.path.getsize(OUT) / 1024 / 1024:.1f} MB)")
