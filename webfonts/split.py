#!/usr/bin/env python3
"""Split Source Han Sans JP OTFs into unicode-range WOFF2 chunks plus a CSS file.

The chunks are a Modified Version under the SIL OFL, and "Source" is a Reserved
Font Name, so every chunk is renamed to FAMILY. Copyright and license records
are kept unchanged.

Browsers only download the chunks whose unicode-range matches characters on
the page, so a typical Japanese page loads a few hundred KB instead of the
whole font. Every chunk stays far below Cloudflare Pages' 25 MiB file limit.

Usage: split.py <otf_dir> <site_dir>
"""

import os
import sys
from concurrent.futures import ProcessPoolExecutor

from fontTools import subset
from fontTools.ttLib import TTFont

FAMILY = "Kaku Sans JP"
PS_FAMILY = FAMILY.replace(" ", "")
CSS_FILE = "kaku-sans-jp.css"
WEIGHTS = {
    "ExtraLight": 200,
    "Light": 300,
    "Normal": 350,
    "Regular": 400,
    "Medium": 500,
    "Bold": 700,
    "Heavy": 900,
}

# Always-needed characters: Latin, punctuation, CJK symbols, kana, fullwidth forms.
CORE_RANGES = [(0x0000, 0x00FF), (0x2000, 0x206F), (0x3000, 0x30FF), (0xFF00, 0xFFEF)]
JIS1_CHUNK = 300   # JIS X 0208 level 1 kanji (most common)
JIS2_CHUNK = 500   # JIS X 0208 level 2 kanji
OTHER_CHUNK = 1000  # everything else (rare kanji, symbols, other scripts)


def jis_row(cp):
    try:
        b = chr(cp).encode("euc_jp")
    except UnicodeEncodeError:
        return None
    if len(b) == 2 and b[0] >= 0xA1:
        return b[0] - 0xA0
    return None


def jis_key(cp):
    b = chr(cp).encode("euc_jp")
    return (b[0], b[1])


def chunk(seq, size):
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def plan_chunks(codepoints):
    core, jis1, jis2, other = [], [], [], []
    for cp in sorted(codepoints):
        row = jis_row(cp)
        if any(lo <= cp <= hi for lo, hi in CORE_RANGES):
            core.append(cp)
        elif row and 16 <= row <= 47:
            jis1.append(cp)
        elif row and 48 <= row <= 84:
            jis2.append(cp)
        else:
            other.append(cp)
    # JIS X 0208 kanji are ordered by reading, which keeps related kanji together.
    jis1.sort(key=jis_key)
    jis2.sort(key=jis_key)
    return [core] + chunk(jis1, JIS1_CHUNK) + chunk(jis2, JIS2_CHUNK) + chunk(other, OTHER_CHUNK)


def unicode_range(cps):
    cps = sorted(cps)
    ranges, start, prev = [], cps[0], cps[0]
    for cp in cps[1:] + [None]:
        if cp is not None and cp == prev + 1:
            prev = cp
            continue
        ranges.append(f"U+{start:X}" if start == prev else f"U+{start:X}-{prev:X}")
        if cp is not None:
            start = prev = cp
    return ", ".join(ranges)


def rename(font):
    """Replace the Reserved Font Name in every name the font presents to users."""
    name = font["name"]
    for rec in list(name.names):
        if rec.nameID not in (1, 2, 3, 4, 6, 16, 17):
            continue
        if rec.langID != 0x409:  # localized names (源ノ角ゴシック) would keep the old name
            name.removeNames(nameID=rec.nameID, langID=rec.langID)
            continue
        value = rec.toUnicode().replace(";ADBO;", ";").replace(";ADOBE", "")
        value = value.replace("Source Han Sans JP", FAMILY).replace("SourceHanSansJP", PS_FAMILY)
        rec.string = value
    cff = font["CFF "].cff
    cff.fontNames[0] = cff.fontNames[0].replace("SourceHanSansJP", PS_FAMILY)
    top = cff.topDictIndex[0]
    top.FamilyName = top.FamilyName.replace("Source Han Sans JP", FAMILY)
    top.FullName = top.FullName.replace("Source Han Sans JP", FAMILY)
    for fd in getattr(top, "FDArray", []):
        if hasattr(fd, "FontName"):
            fd.FontName = fd.FontName.replace("SourceHanSansJP", PS_FAMILY)


def build_chunk(job):
    otf, out, cps = job
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True  # compresses better under WOFF2
    opts.name_IDs = ["*"]  # keep copyright and OFL license records
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    font = subset.load_font(otf, opts)
    subsetter = subset.Subsetter(opts)
    subsetter.populate(unicodes=cps)
    subsetter.subset(font)
    rename(font)
    subset.save_font(font, out, opts)
    return os.path.getsize(out)


def main(otf_dir, site_dir):
    jobs, css = [], []
    for weight, css_weight in WEIGHTS.items():
        otf = os.path.join(otf_dir, f"SourceHanSansJP-{weight}.otf")
        if not os.path.exists(otf):
            continue
        font = TTFont(otf, lazy=True)
        version = f"{font['head'].fontRevision:.3f}"
        chunks = plan_chunks(font.getBestCmap().keys())
        font.close()
        rel_dir = f"fonts/{PS_FAMILY}/v{version}/{weight}"
        os.makedirs(os.path.join(site_dir, rel_dir), exist_ok=True)
        for i, cps in enumerate(chunks):
            rel = f"{rel_dir}/{i:03d}.woff2"
            jobs.append((otf, os.path.join(site_dir, rel), cps))
            css.append(
                "@font-face {\n"
                f"  font-family: \"{FAMILY}\";\n"
                "  font-style: normal;\n"
                f"  font-weight: {css_weight};\n"
                "  font-display: swap;\n"
                f"  src: url(\"{rel}\") format(\"woff2\");\n"
                f"  unicode-range: {unicode_range(cps)};\n"
                "}\n"
            )
    if not jobs:
        sys.exit(f"no SourceHanSansJP-*.otf found in {otf_dir}")

    with ProcessPoolExecutor() as pool:
        total = sum(pool.map(build_chunk, jobs))

    with open(os.path.join(site_dir, CSS_FILE), "w") as f:
        f.write(f"/* {FAMILY} - modified from Source Han Sans JP (Adobe). "
                "SIL Open Font License 1.1, see LICENSE.txt */\n")
        f.write("\n".join(css))
    print(f"wrote {len(jobs)} WOFF2 chunks ({total / 1024 / 1024:.1f} MiB) to {site_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
