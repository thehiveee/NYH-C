# New York Cooling & Heating Services

Marketing site for New York Cooling & Heating Services — HVAC, boilers, ducts and
plumbing across the five boroughs.

## What's here

| Path | What it is |
| --- | --- |
| `index.html` | The site. One self-contained static page — no build step, no dependencies. |
| `src/NYCoolingHeating.dc.html` | Design source. The artboard this page is generated from. |
| `src/convert.py` | Regenerates `index.html` from the artboard. Python 3, no dependencies. |

`index.html` is the only file a web server needs. It can be opened directly in a
browser or dropped on any static host.

### Deploying with GitHub Pages

Settings → Pages → Source: *Deploy from a branch*, branch `main`, folder `/ (root)`.

## The design source

`src/NYCoolingHeating.dc.html` is a Design Component artboard. It is **not** a
working web page on its own: it expects a canvas runtime (`support.js`), and it
uses `{{...}}` template holes, `<sc-for>` loops and `<sc-if>` conditionals that a
browser does not understand. It is kept here as the editable original.

`index.html` is that file with the holes resolved to real values, the loops
expanded to literal markup and the component logic rewritten as plain JavaScript.

**Edit one or the other, not both.** If the artboard changes, regenerate the page
rather than hand-editing it, or the two will drift apart:

```sh
python3 src/convert.py src/NYCoolingHeating.dc.html index.html
```

## Design notes

- **Palette.** Charcoal `#1C1C1F`, crimson `#D81F2A`, white, warm grey `#F5F3F0`,
  plus a steel blue `#2F6C8F` used for the cooling side of the heating/cooling split.
- **Type.** Barlow Condensed for display, Barlow for body, both from Google Fonts.
- **Dark mode.** Colours are CSS custom properties on `:root`, overridden under
  `prefers-color-scheme: dark` and under `[data-theme="dark"]`. Sections that are
  dark by design stay dark in both themes.
- **Responsive.** Breakpoints at 860px, 400px and 360px. At 860px multi-column
  grids collapse to one column, display type scales down, the page gutter drops
  to 16px, the comparison table restacks as cards, and the header becomes a
  wordmark with a disclosure menu beside it. The two narrower breakpoints shrink
  the menu button to its icon and then the wordmark, so the header stays on one
  row down to 320px.
- **Accessibility.** Real `<button>`, `<a>` and `<label>` elements throughout, the
  comparison is a proper `<table>` with scoped headers, icon-only controls carry
  `aria-label`, and animation is disabled under `prefers-reduced-motion`.

## Still to fill in

Placeholders are written in `[SQUARE BRACKETS]` so they are easy to grep for:

- `[X.X]` average rating and `[number]` of reviews
- Three `[REAL GOOGLE REVIEW ...]` quotes, with `[Name]`, `[Neighborhood]`, `[Service]`
- `[Office hours]` and `[License no.]` in the footer
- `[OFFER — e.g. $XX off your first service call]` in the exit pop-up
- Every `[PHOTO ...]`, `[BEFORE / AFTER ...]` and similar image placeholder

The contact form and the pop-up are markup only — neither is wired to a backend,
so submissions currently go nowhere.
