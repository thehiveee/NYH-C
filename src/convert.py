#!/usr/bin/env python3
"""Convert the Design Component artboard (.dc.html) into a standalone static page."""
import re
import sys

SRC, DEST = sys.argv[1], sys.argv[2]

HOLES = {
    "dark": "#1C1C1F",
    "primary": "#D81F2A",
    "secondary": "#2F6C8F",
    "primaryOnLight": "#93151D",
    "primaryOnDark": "#E2575F",
    "secondaryOnLight": "#1D4359",
    "secondaryOnDark": "#82A7BC",
    "ringColor": "rgba(216, 31, 42, .3)",
    "phone": "(516) 517-0005",
    "name": "New York Cooling &amp; Heating Services",
}

# id, label, icon path, selected fg, selected bg, selected ring, submit label
OPTIONS = [
    ("cool", "Not cooling",
     "M12 2.6v18.8M3.9 7.3l16.2 9.4M3.9 16.7l16.2-9.4",
     "#1D4359", "#EAF0F4", "#2F6C8F", "Get my free AC estimate"),
    ("heat", "No heat",
     "M12 2.7c.6 4 3 5.6 4.4 7.6a6.9 6.9 0 1 1-11.5 4.6c0-3 1.7-4.8 2.8-6.3.3 1.9 1.1 2.8 2.1 3.2-.6-3.6.3-7.1 2.2-9.1z",
     "#93151D", "#FBE9EA", "#D81F2A", "Get my free heating estimate"),
    ("install", "Install or replace",
     "M4.5 7h15a1.5 1.5 0 0 1 1.5 1.5v7a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 15.5v-7A1.5 1.5 0 0 1 4.5 7zM6 11h12M6 14h12",
     "var(--ink)", "var(--tint-neutral)", "var(--ink)", "Book an install consultation"),
    ("plumb", "Boiler or plumbing",
     "M8 3.5v6a4 4 0 0 0 4 4 4 4 0 0 1 4 4v3M5 3.5h6M13 20.5h6",
     "var(--ink)", "var(--tint-neutral)", "var(--ink)", "Get my free plumbing estimate"),
]

BTN_STYLE = (
    "min-height: 52px; padding: 15px 16px; display: flex; align-items: center; gap: 10px; "
    "border: 0; margin: 0; text-align: left; font-family: inherit; font-weight: 600; "
    "font-size: 15.5px; cursor: pointer; transition: background .18s ease, color .18s ease, "
    "box-shadow .18s ease; color: %s; background: %s; box-shadow: %s"
)

src = open(SRC, encoding="utf-8").read()

# 1. Pull the helmet contents out for the <head>.
helmet = re.search(r"<helmet>(.*?)</helmet>", src, re.S)
head_extra = helmet.group(1).strip("\n")
src = src.replace(helmet.group(0), "")

# 2. Drop the canvas runtime hook and the component logic block.
src = src.replace('<script src="./support.js"></script>', "")
src = re.sub(r'<script type="text/x-dc".*?</script>', "", src, flags=re.S)

# 3. Expand <sc-for> into literal buttons.
buttons = []
for i, (oid, label, icon, fg, bg, ring, _sub) in enumerate(OPTIONS):
    on = i == 0
    buttons.append(
        '              <button type="button" data-issue="%s" aria-pressed="%s" style="%s">\n'
        '                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
        'style="flex: none; width: 18px; height: 18px"><path d="%s"></path></svg>\n'
        "                <span>%s</span>\n"
        "              </button>"
        % (
            oid,
            "true" if on else "false",
            BTN_STYLE % (fg if on else "var(--ink-soft)",
                         bg if on else "var(--surface)",
                         ("inset 0 0 0 2px " + ring) if on else "none"),
            icon,
            label,
        )
    )
src = re.sub(r"<sc-for\b.*?</sc-for>", "\n".join(buttons), src, flags=re.S)

# 4. <sc-if> popup -> a real element driven by script.
src = re.sub(r'<sc-if value="\{\{showPopup\}\}"[^>]*>',
             '<div id="popup" style="display: none">', src)
src = src.replace("</sc-if>", "</div>")
src = src.replace('onClick="{{closePopup}}"', 'onclick="closePopup()"')

# 5. The submit button needs an id so script can retitle it.
src = src.replace(">{{submitLabel}}</button>",
                  ' id="submitBtn">%s</button>' % OPTIONS[0][6], 1)
src = re.sub(r'(<button type="button" style="width: 100%; padding: 19px 24px;[^"]*")'
             r' id="submitBtn"', r'\1 id="submitBtn"', src)

# 6. Remaining holes -> literals. The helmet is substituted too: it carries the
#    <style> block, which uses holes for brand colours.
for key, val in HOLES.items():
    src = src.replace("{{%s}}" % key, val)
    head_extra = head_extra.replace("{{%s}}" % key, val)

leftover = re.findall(r"\{\{[^}]*\}\}", src + head_extra)
if leftover:
    sys.exit("unresolved holes: %s" % sorted(set(leftover)))

# 7. Unwrap the component body.
body = re.search(r"<x-dc>(.*?)</x-dc>", src, re.S).group(1).strip("\n")

SCRIPT = """
<script>
(function () {
  var LOOKS = {
    cool:    { fg: '#1D4359',     bg: '#EAF0F4',             ring: '#2F6C8F',   label: 'Get my free AC estimate' },
    heat:    { fg: '#93151D',     bg: '#FBE9EA',             ring: '#D81F2A',   label: 'Get my free heating estimate' },
    install: { fg: 'var(--ink)',  bg: 'var(--tint-neutral)', ring: 'var(--ink)', label: 'Book an install consultation' },
    plumb:   { fg: 'var(--ink)',  bg: 'var(--tint-neutral)', ring: 'var(--ink)', label: 'Get my free plumbing estimate' }
  };
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-issue]'));
  var submit = document.getElementById('submitBtn');

  function select(id) {
    buttons.forEach(function (b) {
      var on = b.getAttribute('data-issue') === id;
      var look = LOOKS[b.getAttribute('data-issue')];
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.style.color = on ? look.fg : 'var(--ink-soft)';
      b.style.background = on ? look.bg : 'var(--surface)';
      b.style.boxShadow = on ? 'inset 0 0 0 2px ' + look.ring : 'none';
    });
    if (submit && LOOKS[id]) submit.textContent = LOOKS[id].label;
  }
  buttons.forEach(function (b) {
    b.addEventListener('click', function () { select(b.getAttribute('data-issue')); });
  });

  // Phone menu: collapse it once a link inside has been followed.
  var mob = document.querySelector('.mobnav');
  if (mob) {
    mob.addEventListener('click', function (e) {
      var link = e.target.closest ? e.target.closest('.mobnav-panel a') : null;
      if (link) mob.removeAttribute('open');
    });
  }

  var popup = document.getElementById('popup');
  var dismissed = false;
  function seen() {
    try { return window.sessionStorage.getItem('nycool-popup-seen') === '1'; } catch (e) { return false; }
  }
  function markSeen() {
    try { window.sessionStorage.setItem('nycool-popup-seen', '1'); } catch (e) {}
  }
  window.closePopup = function () {
    dismissed = true;
    if (popup) popup.style.display = 'none';
  };
  document.addEventListener('mouseout', function (e) {
    if (!popup || dismissed || seen()) return;
    if (e.relatedTarget || e.toElement) return;
    if (e.clientY > 10) return;
    markSeen();
    popup.style.display = 'grid';
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') window.closePopup();
  });
})();
</script>
"""

doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>New York Cooling &amp; Heating Services — HVAC, Boilers &amp; Plumbing in NYC</title>
<meta name="description" content="24/7 HVAC, boiler and plumbing service across the five boroughs. Flat-rate pricing agreed before work starts, no overtime charge, NATE and EPA certified technicians.">
%s
</head>
<body>
%s
%s
</body>
</html>
""" % (head_extra, body, SCRIPT.strip("\n"))

open(DEST, "w", encoding="utf-8").write(doc)
print("wrote %s (%d bytes)" % (DEST, len(doc)))
