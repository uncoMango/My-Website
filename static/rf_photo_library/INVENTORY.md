# Rotten Fencepost Photo Library

A shared, reusable source-photo resource for the Rotten Fencepost brand —
not tied to any single campaign. When starting a new campaign, check this
library before asking Kahu Phil to shoot or find a new photograph.

Established 2026-08-08, from Kahu Phil's recovered `RF Photos.zip`
collection (23 files, 19 unique after removing exact duplicates).

## How this library is organized

- `sources/` — curated original photographs, EXIF-orientation-normalized
  (so they display correctly as CSS `background-image`, which does not
  reliably auto-rotate per EXIF the way `<img>` does) but otherwise
  **unmodified**: no cropping, no resizing, no compositing. These are the
  photos to reuse, and the images to re-derive new thumbnails from.
- `derivatives/` — generated presentation assets *built from* a `sources/`
  photo (e.g. a branded 16:9 video thumbnail). Never edit a derivative by
  hand; regenerate it from its source if the source or design changes.
- The original recovered ZIP/folder (`RF Photos.zip`, `RF Photos/`) is
  **not** part of this repository — it lives on Kahu Phil's own machine.
  This library is a curated *copy* of the useful subset, not the full
  unsorted collection.

## Using this library for a future campaign

1. Read the table below. Filter by what the campaign needs (Phil's face?
   fence/ranch imagery? Molokaʻi landscape?).
2. Reuse a `sources/` photo directly for a hero (set `hero_image` in
   `content.py`'s `CAMPAIGNS` entry) — check its aspect ratio first. If it
   is much taller/more square than the page's hero box is wide, set
   `"hero_fit": "contain"` on that campaign so the shared `.hero` CSS
   letterboxes it instead of center-cropping it (see Campaign 002's entry
   for a working example, and `campaign_page.html` for how it's read).
3. To build a new 16:9 video thumbnail in the established brand system
   (dark bottom gradient, small gold letter-spaced kicker reading "THE
   ROTTEN FENCEPOST", bold white title, thin gold rule), reuse the
   generation script's approach documented below rather than inventing a
   new visual treatment. Save the result into `derivatives/` and point
   the campaign's `thumbnail_image` field at it — `campaign_page.html`
   and `rotten_fencepost.html` both already prefer `thumbnail_image` when
   present and fall back to YouTube's own `hqdefault.jpg` when it isn't,
   so a campaign without a custom thumbnail yet still works.
4. Only ask Kahu Phil for a brand-new photograph if nothing in this table
   fits — do not default to reusing the same photo for every campaign
   just because it's convenient (see the 2026-08-08 work order this
   library was built for: Campaign 001 and 002 had been showing the
   *same* thumbnail, which this library exists to prevent going forward).

### Regenerating a thumbnail

The two existing thumbnails were built with a small Pillow script (not
committed — one-off at time of writing, reconstructable from this
description): 1280x720 canvas; background either `cover`-cropped (safe
for wide photos with margin, like ranch/landscape shots) or
`contain`-letterboxed on a `#1a1a1a` fill (required for photos where
cropping would cut off a person, like the horse/ukulele portrait); a
bottom gradient (0 to ~92% black opacity from ~42% height to bottom) for
text legibility; kicker text "THE ROTTEN FENCEPOST" in gold (`#c9a842`),
Arial Bold 30px, letter-spaced; title text in white, Arial Bold (92px for
one line, 68px for two), bottom-anchored; a short gold rule above the
title. Keep new thumbnails visually consistent with this system
(typography, kicker, gradient) while using a different source photo per
campaign so the series reads as related but not duplicated.

## Full inventory

Dimensions are as extracted (orientation-corrected where the source had
an EXIF rotation tag). "In library" = copied into `sources/` under a
renamed, mapped filename. Photos not copied in were reviewed but judged
not currently useful for Rotten Fencepost branding (food/garden macro
shots, an unrelated family photo, a low-quality recent selfie) — they
remain in Kahu Phil's original `RF Photos.zip` if needed later.

| Original filename | Dimensions | Subject | Phil | Horse | Fence | Cattle/ranch | Molokaʻi/landscape | ʻUkulele | In library as |
|---|---|---|---|---|---|---|---|---|---|
| CAM00002-edited.jpg | 4160×3120 | Colorado ranch, ~15 cattle grazing, distant ridge, thin wire fence crossing foreground | no | no | **yes** | **yes** | no (Colorado) | no | `sources/rf_ranch_cattle_grazing_wide.jpg` — used for Campaign 001 thumbnail |
| CAM00003.jpg | 4160×3120 | Same ranch, cattle + windmill/water-tank structure, mountains | no | no | no | **yes** | no | no | `sources/rf_ranch_cattle_windmill.jpg` — reserve |
| CAM00006.jpg | 4160×3120 (native portrait after EXIF correction) | Single cow beside large boulders, valley view | no | no | no | **yes** | no | no | `sources/rf_ranch_cow_boulders.jpg` — reserve |
| CAM00006-edited.jpg | 3120×4160 | Same scene as CAM00006.jpg, pre-cropped to portrait | no | no | no | **yes** | no | no | *not copied — redundant derivative of CAM00006.jpg* |
| CAM00042.jpg | 4160×3120 | Mother cow + newborn calf lying in snow | no | no | no | **yes** | no | no | `sources/rf_ranch_calf_snow.jpg` — reserve; strong candidate for a future "new beginnings" campaign |
| FB_IMG_1739986398654.jpg | 596×604 | Phil on horseback playing ʻukulele, sunset beach | **yes** | **yes** | no | no | possibly (unconfirmed location) | **yes** | `sources/rf_phil_horse_ukulele_beach.jpg` — used for Campaign 002 hero + thumbnail. Best-resolution copy found (was 203×206 live); still has a pre-existing white die-cut/cutout edge artifact baked into the source itself, not introduced here — flagged for Kahu Phil, a cleaner original would be a welcome future replacement |
| FB_IMG_1681971712809.jpg (+ byte-identical "(1)" copy) | 1080×1440 | Phil playing acoustic guitar, outdoor tiki/market stall | **yes** | no | no | no | no | no (guitar, not ʻukulele) | `sources/rf_phil_guitar_market_wide.jpg` — reserve speaker-portrait option |
| FB_IMG_1681971722176.jpg (+ byte-identical "(1)" copy) | 1080×1440 | Phil playing guitar, closer profile, full head clearly visible | **yes** | no | no | no | no | no | `sources/rf_phil_guitar_market_closeup.jpg` — reserve; best clean headshot in the collection |
| 20250501_103248.jpg | 2250×4000 (portrait after EXIF correction) | Phil (likely) in western shirt/hat at an outdoor event, mountains behind | likely | no | no | no | maybe | no | `sources/rf_phil_portrait_western_event.jpg` — reserve; not used here per instruction not to default to a speaker portrait |
| 0210191402.jpg | 3120×4160 (portrait after EXIF correction) | Coastal cove, palm trees, pink flowering shrubs | no | no | no | no | **yes** | no | `sources/rf_molokai_coast_palms.jpg` — reserve generic scenic backdrop |
| images-edited.jpg | 190×137 | A fence post with a decorative bird figure, field, blue sky | no | no | **yes** | no | unclear | no | *not copied* — thematically the most literal "fencepost" image in the collection, but only 190×137 and named/styled like a downloaded web reference rather than an original photo. Flagged for Kahu Phil to confirm provenance or supply a higher-resolution original if this is in fact his own photo |
| 0627180543.jpg | 4160×3120 | Dragon fruit on cactus, garden macro | no | no | no | no | no | no | *not copied* — not brand-relevant |
| 0810181112a.jpg | 4160×3120 | Taro/kalo leaf, garden macro | no | no | no | no | no | no | *not copied* |
| 0810181113e.jpg | 4160×3120 | Taro leaf, different plant | no | no | no | no | no | no | *not copied* |
| 0826181018.jpg | 4160×3120 | Bowl of stew, food photo | no | no | no | no | no | no | *not copied* |
| 0912181514a.jpg | 4000×3000 | Palm frond/coconut closeup | no | no | no | no | no | no | *not copied* |
| 20230708_070840.jpg | 4160×3120 | Bowl of cherry tomatoes | no | no | no | no | no | no | *not copied* |
| 20250723_170305.jpg | 4000×2250 | Purple orchid, home garden | no | no | no | no | no | no | *not copied* |
| 20250808_172917.jpg | 4000×2250 | Orchid closeup, garden | no | no | no | no | no | no | *not copied* |
| 20260112_064252.jpg | 3408×2556 | Recent close-up selfie, indoors, low quality/blurry | unclear | no | no | no | no | no | *not copied* — not usable quality |
| IMG_20230515_131520.jpg | 5760×4320 | Group photo, 3 people, airport/terminal setting | no (different person) | no | no | no | no | no | *not copied* — not Rotten Fencepost content |
