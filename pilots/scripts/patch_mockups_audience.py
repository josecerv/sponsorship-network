"""Pass 13 (2026-08-21): add the "audience" frame to the Stage 3 mockups in new_mockups.html and re-render them.

    python pilots/scripts/patch_mockups_audience.py [strings.json]

Idempotent on the structure (re-running only updates the strings). strings.json keys (defaults = architect drafts; Sol's
final strings from tmp/codex_pass13_write/out/ui_strings.md replace them):
  U1 header line (independent reviewer), U2 connector label, U3 candidate-card label, U4 placement title (template with
  {pct} and {amt}), U5a result sentence when the candidate scored higher (template {pct}), U6 representative amount label.
Structure added to s3_r1_man / s3_r1_woman / s3_r2_man / s3_outcome_man: a grey header line above the title, a
connector column (arrow + label) between the representative card and the candidate card, a violet border + top label on
the candidate card. Renders with Playwright Firefox via render_mockup_shots.py and backs up the previous PNGs.
"""
import os, re, sys, json, shutil, subprocess
os.chdir(r"C:\Users\jcerv\Jose\sponsorship-network")
HTML = r"pilots/output/instruction_simplification/new_mockups.html"
MOCK = r"pilots/output/instruction_simplification/mockups"
DEFAULTS = {
    "U1": "You are an independent reviewer. You belong to no organization.",
    "U2": "backs",
    "U3": "Backed by the Atlas representative",
    "U4": "The representative placed {pct}% of their $0.50 behind this candidate. How much of your $0.50 do you place behind their call?",
    "U5a": "You placed {pct}% behind the representative\u2019s call, and the Atlas candidate scored higher. You keep this amount.",
    "U6": "Amount placed by representative",
}
S = dict(DEFAULTS)
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    S.update(json.load(open(sys.argv[1], encoding="utf-8")))
for k, v in S.items():
    assert "\u2014" not in v and "'" not in v and '"' not in v, (k, v)

h = open(HTML, encoding="utf-8").read()
if "/* audience frame */" not in h:
    shutil.copy(HTML, HTML + ".bak_2026-08-21_pre_pass13")
    css = """
  /* audience frame */
  .obs-line { color: #6B7280; font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 8px; }
  .grid4 { display: grid; grid-template-columns: 1fr 56px 1.08fr 1.08fr; gap: 14px; align-items: stretch; }
  .connector { display: flex; flex-direction: column; align-items: center; justify-content: center; color: #7C3AED; }
  .connector .arrow { font-size: 34px; font-weight: 800; line-height: 1; }
  .connector .lbl { font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; margin-top: 4px; }
  .mid-card.backed { border: 2px solid #7C3AED; }
  .backed-lbl { font-size: 12px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: #7C3AED; }
</style>"""
    h = h.replace("</style>", css, 1)

def patch_section(h, sid):
    s = h.index(f'<section class="shot" id="{sid}">'); e = h.index("</section>", s)
    sec = h[s:e]
    # header line (replace if present)
    sec = re.sub(r'<div class="obs-line">[^<]*</div>\n    ', "", sec)
    sec = sec.replace('<h1 class="title">', f'<div class="obs-line">{S["U1"]}</div>\n    <h1 class="title">', 1)
    # grid + connector + candidate label
    sec = sec.replace('<div class="grid3">', '<div class="grid4">')
    sec = re.sub(r'<div class="connector">.*?</div>\s*</div>\s*', "", sec, flags=re.S)
    sec = sec.replace('<div class="mid-card backed"><div class="backed-lbl">', '<div class="mid-card">')
    sec = re.sub(r'<div class="mid-card">(?:[^<]*</div>)?', '<div class="mid-card">', sec, count=1)
    sec = sec.replace('<div class="mid-card">',
                      f'<div class="connector"><div class="arrow">\u2192</div><div class="lbl">{S["U2"]}</div></div>\n      '
                      f'<div class="mid-card backed"><div class="backed-lbl">{S["U3"]}</div>', 1)
    # representative amount label
    sec = re.sub(r'<div class="lbl">(Amount placed by representative|[^<]*)</div>\n        <div class="conf-track">',
                 f'<div class="lbl">{S["U6"]}</div>\n        <div class="conf-track">', sec, count=1)
    # placement title with this section's representative percentage
    m = re.search(r'<div class="conf-text">(\d+)% \(\$(\d\.\d\d) of \$0\.50\)</div>', sec)
    pct, amt = m.group(1), m.group(2)
    sec = re.sub(r'<div class="block-card">\s*<h2>[^<]*</h2>',
                 f'<div class="block-card">\n      <h2>{S["U4"].format(pct=pct, amt=amt)}</h2>', sec, count=1)
    # result band sentence (outcome screen)
    sec = re.sub(r'<div class="b-txt">[^<]*</div>', f'<div class="b-txt">{S["U5a"].format(pct=50)}</div>', sec, count=1)
    return h[:s] + sec + h[e:]

for sid in ("s3_r1_man", "s3_r1_woman", "s3_r2_man", "s3_outcome_man"):
    h = patch_section(h, sid)
open(HTML, "w", encoding="utf-8", newline="\n").write(h)
vis = re.sub(r'src="data:[^"]+"', "", h)
assert vis.count('class="obs-line"') == 4 and vis.count('class="connector"') == 4 and vis.count('mid-card backed') == 4, "structure count"
assert "of 3" not in vis and "Review 1" not in vis
print("html patched; strings:", json.dumps(S, ensure_ascii=False)[:300])

bk = os.path.join(MOCK, "_prev_2026-08-21_pass12"); os.makedirs(bk, exist_ok=True)
for f in ("s3_r1_man.png", "s3_r1_woman.png", "s3_outcome_man.png", "s3_r2_man.png"):
    if not os.path.exists(os.path.join(bk, f)): shutil.copy(os.path.join(MOCK, f), os.path.join(bk, f))
ids = "s3_r1_man,s3_r1_woman,s3_outcome_man,s3_r2_man"
r = subprocess.run([sys.executable, "pilots/scripts/render_mockup_shots.py", os.path.abspath(HTML), os.path.abspath(MOCK), ids], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr[-400:] if r.returncode else "")
