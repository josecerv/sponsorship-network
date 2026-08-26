"""Compare a Codex (or any) rewrite of the Stage 2 / Stage 3 markdown with its input, page by page.

    python pilots/scripts/md_fidelity_check.py <workdir>     # expects <workdir>/in/Stage-2.md, in/Stage-3.md, out/Stage-2.md, out/Stage-3.md

Reports: '# ' structure lines (must be identical, same order), leftover ##/### headings, straight quotes, em dashes,
and per-page differences in dollar figures / percentages / bare numbers / bracket notes / key phrases. Expected, benign
"losses" are de-duplicated repeats; anything else needs reading. Also grep the output for "Page \\d" by hand: Codex once
wrote a doc-internal page reference into participant text.
"""
import re, os, sys
from collections import Counter

D = sys.argv[1] if len(sys.argv) > 1 else None
if not D:
    sys.exit(__doc__)
ALLOWED_SUB = {"## INFORMED CONSENT", "## INTERNAL — MAN PROFILE CONDITION", "## INTERNAL — WOMAN PROFILE CONDITION",
               "### WORD SEARCH TASK", "### GENERAL KNOWLEDGE TASK", "### LOGICAL REASONING TASK"}
KEY = ["only", "never", "no ties", "at random", "at least one", "same order", "$1.00 scale", "regardless", "does not affect",
       "hypothetical", "study-assigned", "profile icon", "another organization", "review slots", "selected at random",
       "after the reviewer study", "three decisions", "three reviews", "two other tasks", "logical-reasoning",
       "general knowledge", "word search", "Unknown", "percentile", "best reflects your judgment"]


def sections(path):
    out, cur = [], None
    for ln in open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n"):
        m = re.match(r"^# (.+?)\s*$", ln)
        if m:
            cur = [m.group(1), []]; out.append(cur)
        elif cur: cur[1].append(ln)
    return out


def feats(lines):
    t = "\n".join(lines)
    return {
        "dollars": sorted(re.findall(r"\$\d+\.\d\d", t)),
        "percents": sorted(re.findall(r"\d+%", t)),
        "numbers": sorted(set(re.findall(r"(?<![\$\d.])\b\d+\b(?!%|\.\d)", t))),
        "notes": sorted(re.findall(r"^\*?\[[^\]]+\]\*?$", t, flags=re.M)),
        "keys": sorted(k for k in KEY if k.lower() in t.lower()),
    }


for stage in ("Stage-2", "Stage-3"):
    pa, pb = os.path.join(D, "in", stage + ".md"), os.path.join(D, "out", stage + ".md")
    if not (os.path.exists(pa) and os.path.exists(pb)):
        print(f"\n================ {stage}: missing in/ or out/ file"); continue
    a, b = sections(pa), sections(pb)
    print(f"\n================ {stage}: in {len(a)} sections, out {len(b)} sections")
    ta, tb = [s[0] for s in a], [s[0] for s in b]
    print("  '# ' lines identical+ordered:", ta == tb)
    if ta != tb:
        print("   in :", ta); print("   out:", tb)
    outtxt = open(pb, encoding="utf-8").read()
    subs = [l for l in outtxt.split("\n") if re.match(r"^#{2,3} ", l) and l.strip() not in ALLOWED_SUB]
    print("  leftover sub-headings:", len(subs), subs[:10])
    print("  straight ' :", outtxt.count("'"), "  straight \" :", outtxt.count('"'), "  em dashes:", outtxt.count("—"),
          "(allowed only inside the two INTERNAL lines:", sum(1 for l in outtxt.split('\n') if l.strip() in ALLOWED_SUB and '—' in l), ")")
    print("  'Page n' references in out:", re.findall(r"\bPage \d[^\n]{0,40}", outtxt))
    wa = len(re.findall(r"\w+", "\n".join("\n".join(s[1]) for s in a))); wb = len(re.findall(r"\w+", "\n".join("\n".join(s[1]) for s in b)))
    print(f"  words: {wa} -> {wb}")
    db = dict(b)
    for title, lines in a:
        if title not in db:
            print(f"  !! section missing in out: {title}"); continue
        fa, fb = feats(lines), feats(db[title])
        diffs = []
        for k in ("dollars", "percents", "numbers", "notes", "keys"):
            if k == "numbers":
                lost = sorted(set(fa[k]) - set(fb[k])); new = sorted(set(fb[k]) - set(fa[k]))
            else:
                ca, cb = Counter(fa[k]), Counter(fb[k])
                lost = list((ca - cb).elements()); new = list((cb - ca).elements())
            if lost or new: diffs.append(f"{k}: lost {lost} new {new}")
        print(f"  [{title}] " + ("OK" if not diffs else " | ".join(diffs)))
