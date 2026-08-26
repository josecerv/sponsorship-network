"""Build the pass-15 proposal page (HTML artifact): redline of live doc text vs the pass-15 draft, the choice-page
mechanism demo, open calls, provenance.

    PYTHONIOENCODING=utf-8 python pilots/scripts/build_pass15_proposal_page.py [out.html]

Inputs (all under pilots/output/instruction_simplification/source_2026-08-26/pass15/):
  out/Stage-2.md, out/Stage-3.md   the draft (Sol wrote, Fable reviewed)
  in/live_cells_2026-08-26.md      not used directly; live cells come from the scratch JSON dump (LIVE_JSON)
  review_summary.md                optional: provenance / review tallies block (markdown-ish, rendered as paragraphs)
No em dashes anywhere in the generated page.
"""
import difflib, html, json, os, re, sys

REPO = r"C:\Users\jcerv\Jose\sponsorship-network"
P15 = os.path.join(REPO, "pilots", "output", "instruction_simplification", "source_2026-08-26", "pass15")
LIVE_JSON = os.environ.get("LIVE_JSON", os.path.join(P15, "in", "live_cells_2026-08-26.json"))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(P15, "pass15_proposal.html")


def sections(path):
    out, cur = [], None
    for ln in open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n"):
        m = re.match(r"^# (.+?)\s*$", ln)
        if m:
            cur = [m.group(1), []]; out.append(cur)
        elif cur is not None:
            cur[1].append(ln)
    return {k: "\n".join(v).strip() for k, v in out}


def md_inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"^\*\[(.+?)\]\*$", r'<span class="note">[\1]</span>', s)
    s = re.sub(r"\*\[(.+?)\]\*", r'<span class="note">[\1]</span>', s)
    return s


def md_block(md):
    """Very small markdown: paragraphs, '- ' bullets, '---' rules, bold, *[notes]*."""
    out, para, bullets = [], [], []
    def flush():
        nonlocal para, bullets
        if para:
            brk = any(re.match(r"^\*\*([A-D]\.|\[|\d+ =|Either)", l) for l in para) or all(l.startswith("**") and l.endswith("**") for l in para)
            out.append("<p>" + ("<br>" if brk else " ").join(md_inline(l) for l in para) + "</p>"); para = []
        if bullets: out.append("<ul>" + "".join("<li>" + md_inline(b) + "</li>" for b in bullets) + "</ul>"); bullets = []
    for ln in md.split("\n"):
        if ln.strip() == "---": flush(); out.append('<hr class="thin">'); continue
        if ln.startswith("- "):
            if para: flush()
            bullets.append(ln[2:].strip()); continue
        if not ln.strip(): flush(); continue
        if bullets: flush()
        para.append(ln.strip())
    flush()
    return "\n".join(out)


def strip_md(md):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", md)
    s = re.sub(r"^\*\[(.+?)\]\*$", r"[\1]", s, flags=re.M)
    s = re.sub(r"^\s*-\s+", "", s, flags=re.M)
    s = re.sub(r"^---\s*$", "", s, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def _word_redline(old, new):
    a, b = re.findall(r"\S+|\s+", old), re.findall(r"\S+|\s+", new)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal": out.append(html.escape("".join(a[i1:i2]), quote=False))
        if op in ("delete", "replace"): out.append("<del>" + html.escape("".join(a[i1:i2]), quote=False) + "</del>")
        if op in ("insert", "replace"): out.append("<ins>" + html.escape("".join(b[j1:j2]), quote=False) + "</ins>")
    return "".join(out)


PARA = "\n\n"


def _sents(s):
    """Sentences (with trailing space) plus paragraph markers."""
    toks = []
    for i, para in enumerate(s.split(PARA)):
        if i: toks.append(PARA)
        toks += [x for x in re.findall(r"[^.!?]*[.!?]+[\"”)]*\s*|[^.!?]+$", para) if x]
    return toks


def redline(old, new):
    """Sentence-level diff; word-level only inside sentence pairs that are mostly the same. Paragraph breaks kept."""
    a, b = _sents(old), _sents(new)
    sm = difflib.SequenceMatcher(None, [x.strip() for x in a], [x.strip() for x in b], autojunk=False)
    out = ["<p>"]
    def emit(tokens, tag=None):
        for t in tokens:
            if t == PARA: out.append("</p><p>"); continue
            e = html.escape(t, quote=False)
            out.append(f"<{tag}>{e}</{tag}>" if tag else e)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal": emit(a[i1:i2])
        elif op == "delete": emit(a[i1:i2], "del")
        elif op == "insert": emit(b[j1:j2], "ins")
        else:
            A, B = a[i1:i2], b[j1:j2]
            similar = len(A) == len(B) and all(x == y == PARA or (x != PARA and y != PARA and difflib.SequenceMatcher(None, x, y).ratio() > 0.6) for x, y in zip(A, B))
            if similar:
                for x, y in zip(A, B):
                    if x == PARA: out.append("</p><p>")
                    else: out.append(_word_redline(x, y))
            else:
                emit(A, "del"); emit(B, "ins")
    out.append("</p>")
    return "".join(out).replace("<p></p>", "")


def live_page_text(live, key):
    """Drop the bold label line (first line) of a live cell and return the participant text."""
    t = live[key]
    lines = t.split("\n")
    return "\n".join(lines[1:]).strip()


live = json.load(open(LIVE_JSON, encoding="utf-8"))
DRAFT = os.environ.get("DRAFT_DIR", os.path.join(os.path.dirname(P15), "pass18", "final"))
s2 = sections(os.path.join(DRAFT, "Stage-2.md"))
s3 = sections(os.path.join(DRAFT, "Stage-3.md"))

# ---- pairs: (title, live text, draft md, note)
STAGE2 = [
    ("Page 1: Your role", live_page_text(live, "STAGE 2|2|0"), s2["PAGE 1: YOUR ROLE"],
     "Your Aug 26 notes applied: one organization with an identity (a talent organization that puts its candidates forward and depends on you to speak for them), onboarding tone, the evaluation stated plainly. Sol’s two alternative identity paragraphs are in pass18/out/Page1_variants.md."),
    ("Page 3: Making your decisions", live_page_text(live, "STAGE 2|5|0"), s2["PAGE 3: MAKING YOUR DECISIONS"],
     "The amount gets its meaning (a confidence signal reviewers will see) before the pay rule; the rule and the three bullets are unchanged; one sentence on what accuracy buys."),
    ("Page 4: Your payment", live_page_text(live, "STAGE 2|6|0"), s2["PAGE 4: YOUR PAYMENT"],
     "Your Aug 25 paragraph is the base. One clause changed: \u201ccandidate you endorsed\u201d to \u201ccandidate you referred\u201d, and \u201cwanted to review afterward\u201d to \u201csaid they would want to review\u201d (a stated answer, literally true)."),
]
STAGE3 = [
    ("Page 1: Your role", live_page_text(live, "STAGE 3|2|0"), s3["PAGE 1: YOUR ROLE"],
     "Simplified to match Stage 2: no world sentence, no “belong to no organization” line; the representative knew reviewers would see some of their decisions (you cut a version of this in pass 14; your call)."),
    ("Page 2: Making your reviews", live_page_text(live, "STAGE 3|3|0"), s3["PAGE 2: MAKING YOUR REVIEWS"],
     "Pay rule unchanged. The last paragraph is the light telegraph: one choice about the final review, explained when reached, and one question about the representative."),
    ("Page 6: Later reviews", live_page_text(live, "STAGE 3|8|0"), s3["PAGE 6: LATER REVIEWS"],
     "The end-of-reviews line now closes the reviews with this representative; the total moves to after the final review."),
    ("Page 6B: Choose your final representative (new)", "", s3["PAGE 6B: CHOOSE YOUR FINAL REPRESENTATIVE"],
     "New page, rewritten twice after your notes: one job (the slider); the cost comes out of their own review earnings (no separate $0.15); no price list and no check item in the text, the screen shows the exact cost; one draw; one sentence that it does not touch the representative\u2019s bonus."),
    ("Page 6C: Final review (new)", "", s3["PAGE 6C: FINAL REVIEW"],
     "One real review with the drawn representative, its own $0.50, result shown, then the total."),
    ("Page 7: Two questions about the representative and [Atlas/Vertex]", live_page_text(live, "STAGE 3|9|0"), s3["PAGE 7: TWO QUESTIONS ABOUT THE REPRESENTATIVE AND [ATLAS/VERTEX]"],
     "Restored to your approved text: both 0-10 items, both paid to the representative. With the organization question off Page 6B, the organization item carries the spillover DV again."),
]


def pair_html(title, old, new_md, note, anchor):
    new_plain = strip_md(new_md)
    if old:
        body = f"""
      <div class="cols">
        <div class="col"><div class="collabel">Doc before this apply (after your Aug 25 edits)</div><div class="doc">{md_block(html.escape(old, quote=False).replace('&lt;','<').replace('&gt;','>')) if False else ''.join('<p>'+html.escape(p, quote=False)+'</p>' for p in old.split(chr(10)+chr(10)) if p.strip())}</div></div>
        <div class="col"><div class="collabel">Now in the doc (pass 18)</div><div class="doc">{md_block(new_md)}</div></div>
      </div>
      <details class="redline"><summary>Show as redline</summary><div class="doc">{redline(old, new_plain)}</div></details>"""
    else:
        body = f"""<div class="cols one"><div class="col"><div class="collabel">Now in the doc (pass 18) (new page)</div><div class="doc">{md_block(new_md)}</div></div></div>"""
    return f"""
    <section class="page" id="{anchor}">
      <h3>{html.escape(title)}</h3>
      <p class="why">{note}</p>
      {body}
    </section>"""


review_md = ""
rp = os.path.join(P15, "review_summary.md")
if os.path.exists(rp):
    review_md = open(rp, encoding="utf-8").read()

CSS = """
:root{
  --paper:#F7F8FA; --ink:#1A2232; --ink-2:#4A5568; --ink-3:#7B8794; --rule:#D9DEE7; --card:#FFFFFF;
  --accent:#23408F; --accent-ink:#FFFFFF; --mark:#FFF1B8; --mark-ink:#5A4300; --del:#F5DADA; --del-ink:#7A2E2E;
  --ins:#E3F1E1; --ins-ink:#1F5A2A; --mono-bg:#EEF1F6; --warn:#B7791F;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --paper:#12161E; --ink:#E6E9F0; --ink-2:#B4BCCB; --ink-3:#7F8A9E; --rule:#2A3242; --card:#1A2029;
  --accent:#8FA8F2; --accent-ink:#0E1420; --mark:#4A3D10; --mark-ink:#FFE58A; --del:#4A2323; --del-ink:#F3B5B5;
  --ins:#1F3A25; --ins-ink:#BFE8C6; --mono-bg:#222A36; --warn:#E2B04A; } }
:root[data-theme="dark"]{
  --paper:#12161E; --ink:#E6E9F0; --ink-2:#B4BCCB; --ink-3:#7F8A9E; --rule:#2A3242; --card:#1A2029;
  --accent:#8FA8F2; --accent-ink:#0E1420; --mark:#4A3D10; --mark-ink:#FFE58A; --del:#4A2323; --del-ink:#F3B5B5;
  --ins:#1F3A25; --ins-ink:#BFE8C6; --mono-bg:#222A36; --warn:#E2B04A; }
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.55;font-size:16px}
main{max-width:1080px;margin:0 auto;padding:32px 24px 96px}
h1,h2,h3{font-family:"Fraunces","Iowan Old Style",Georgia,serif;text-wrap:balance;margin:0}
h1{font-size:2.4rem;font-weight:600;letter-spacing:-.01em;line-height:1.1}
h2{font-size:1.6rem;font-weight:600;margin:64px 0 12px;padding-top:16px;border-top:2px solid var(--accent)}
h3{font-size:1.2rem;font-weight:600;margin:32px 0 6px}
p{margin:0 0 12px;max-width:72ch}
.lede{font-size:1.1rem;color:var(--ink-2);max-width:70ch}
.eyebrow{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
.state{display:inline-block;background:var(--mark);color:var(--mark-ink);padding:2px 10px;border-radius:3px;font-weight:600;font-size:.85rem;letter-spacing:.02em}
nav.toc{display:flex;flex-wrap:wrap;gap:8px 18px;margin:24px 0 0;font-size:.9rem}
nav.toc a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--rule)}
a{color:var(--accent)}
.asks{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:16px}
.ask{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:18px 20px}
.ask .k{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.75rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-bottom:6px}
.ask blockquote{margin:0 0 10px;padding-left:12px;border-left:3px solid var(--mark);color:var(--ink-2);font-style:italic;font-size:.95rem}
.ask p{font-size:.95rem;margin-bottom:6px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:10px}
.cols.one{grid-template-columns:1fr}
@media (max-width:820px){.cols{grid-template-columns:1fr}}
.col{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:16px 18px;min-width:0}
.collabel{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--rule)}
.doc{font-family:"Source Serif 4","Iowan Old Style",Georgia,serif;font-size:1.02rem;line-height:1.5}
.doc p{max-width:none;margin-bottom:10px}
.doc ul{margin:0 0 10px 20px;padding:0}
.doc li{margin-bottom:4px}
.doc .note{color:var(--ink-3);font-style:italic;font-size:.9em}
.doc hr.thin{border:0;border-top:1px solid var(--rule);margin:10px 0}
.why{color:var(--ink-2);font-size:.95rem;max-width:80ch}
del{background:var(--del);color:var(--del-ink);text-decoration:line-through;text-decoration-thickness:1px;padding:0 1px}
ins{background:var(--ins);color:var(--ins-ink);text-decoration:none;padding:0 1px}
details.redline{margin-top:10px}
details.redline summary{cursor:pointer;color:var(--accent);font-size:.9rem}
details.redline .doc{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:16px 18px;margin-top:8px}
.demo{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:20px 22px;margin:16px 0}
.demo .q{font-family:"Source Serif 4",Georgia,serif;font-size:1.05rem;margin-bottom:12px}
.demo input[type=range]{width:100%;accent-color:var(--accent)}
.demo .ends{display:flex;justify-content:space-between;font-size:.85rem;color:var(--ink-3)}
.demo .live{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:1rem;margin-top:10px;background:var(--mono-bg);padding:10px 12px;border-radius:4px}
.demo .live b{color:var(--accent)}
table{border-collapse:collapse;font-variant-numeric:tabular-nums;font-size:.92rem;margin:12px 0}
th,td{padding:6px 12px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);font-weight:500}
.tablewrap{overflow-x:auto}
ol.calls{padding-left:22px;max-width:80ch}
ol.calls li{margin-bottom:10px}
ol.calls .d{color:var(--ink-3);font-size:.9rem}
.warnbox{border-left:3px solid var(--warn);padding:8px 14px;background:var(--card);border-radius:0 6px 6px 0;margin:12px 0;max-width:80ch}
.prov p{font-size:.95rem;color:var(--ink-2)}
code{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.85em;background:var(--mono-bg);padding:1px 5px;border-radius:3px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap">'

DEMO_JS = """
<script>
(function(){
  var price={0:15,10:10,20:6,30:3,40:1,50:0,60:1,70:3,80:6,90:10,100:15};
  var r=document.getElementById('chance'), out=document.getElementById('live');
  function fmt(c){return '$0.'+(c<10?'0':'')+c;}
  function upd(){var q=+r.value, c=price[q];
    var who = q===50 ? 'a coin flip decides' : (q>50 ? 'chance this representative' : 'chance a different representative');
    out.innerHTML='Chance this representative: <b>'+q+'%</b>. Cost from your review earnings: <b>'+fmt(c)+'</b>.' + (q===50?' (free; a coin flip decides)':'');}
  r.addEventListener('input',upd); upd();
})();
</script>
"""


def build():
    asks = f"""
    <div class="asks">
      <div class="ask"><div class="k">Ask A, Stage 2 onboarding</div>
        <blockquote>maybe we say that we are a temp agency, and there's two organizations in this world; you work at vertex, and your decisions will be under scrutiny; make it feel a bit more like onboarding</blockquote>
        <p>Stage 2 Page 1 is now a short onboarding in your words: welcome, you have been assigned to [Vertex/Atlas], your role as its representative, and, plainly, that an independent reviewer in a separate study will review your decisions and decide how far to follow them. One organization only; the comparison candidate is simply from another organization, as in the live doc.</p></div>
      <div class="ask"><div class="k">Ask B, referral framing</div>
        <blockquote>placing a bet on the candidate is a measure of confidence... a higher amount of .50 is supposed to indicate your level of confidence in that person... if they are accurate, they get some benefit from that accuracy</blockquote>
        <p>Stage 2 Page 3 now gives the amount its meaning before the pay rule (how strongly you vouch; it is your confidence and reviewers see it; your own pay rises or falls with it) and closes with what accuracy buys. The rule and the three bullets are untouched. Verbs: refer, referral, vouch for, back. Nouns unchanged: representative, independent reviewer.</p></div>
      <div class="ask"><div class="k">Ask C, incentivize the ask</div>
        <blockquote>randomly pair you with a random other referrer or, if you like this particular referrer... you can pay money to increase the likelihood that they're the one we show you</blockquote>
        <p>A new Stage 3 page after the same-representative reviews: a chance slider (free at 50%; moving away costs a little from their own review earnings, more the further they go, $0.15 at the ends), one draw, one real final review. The chance sets only the reviewer's own assignment, never the representative's bonus. Your two 0-10 items stay as they are and keep paying the representative. Details below.</p></div>
    </div>"""

    mech = f"""
    <p class="lede">The literal version, a price that buys chance in a straight line, does not work: expected value is then linear in the amount, so a reviewer who thinks in expected value either pays nothing or everything, and everything is never worth it at these stakes. A price that rises faster the further you move makes the best setting interior, and the chosen chance becomes a readout of how much more (or less) this representative is worth to the reviewer than a random one. The slider works both ways, so a reviewer who has lost money following someone can pay to avoid them. That is the loss side of social capital, which a one-sided pay-to-keep item would censor at zero.</p>
    <div class="demo">
      <div class="q">For your final review, how likely do you want it to be that the decision comes from this same representative?</div>
      <input id="chance" type="range" min="0" max="100" step="10" value="50" aria-label="Chance this representative">
      <div class="ends"><span>0%: certainly a different representative</span><span>50%: coin flip, free</span><span>100%: certainly this representative</span></div>
      <div class="live" id="live"></div>
    </div>
    <div class="tablewrap"><table>
      <tr><th>Slider</th><th>Cost (from review earnings)</th><th>A risk-neutral reviewer lands here when this representative is worth, per review, at least</th></tr>
      <tr><td>50%</td><td>$0.00</td><td>about the same as a random one</td></tr>
      <tr><td>60% or 40%</td><td>$0.01</td><td>$0.10 more (or less)</td></tr>
      <tr><td>70% or 30%</td><td>$0.03</td><td>$0.20 more (or less)</td></tr>
      <tr><td>80% or 20%</td><td>$0.06</td><td>$0.30 more (or less)</td></tr>
      <tr><td>90% or 10%</td><td>$0.10</td><td>$0.40 more (or less)</td></tr>
      <tr><td>100% or 0%</td><td>$0.15</td><td>$0.50 more (or less)</td></tr>
    </table></div>
    <p>Where the stakes come from: a review is worth about max($0.50, p) to a reviewer who believes the backed candidate wins with probability p, so a representative who has looked good is worth roughly $0.75 to $0.85 per review, a random one $0.55 to $0.65, and a representative who has looked bad $0.50. The value gap is therefore about minus $0.15 to plus $0.30, which this table spreads over 40% to 80%. The dollar amounts are small by construction; the measure is the comparison across the gender arms. Expect heaping at 50 and on round numbers; the analysis plan carries a two-part model beside the linear one. Per your note the cost now comes out of the reviewer's own review earnings rather than a separate $0.15: this reads as a real loss, which likely means more reviewers stay at 50 (a build rule keeps the price from exceeding what they have earned; the text does not need to mention it). The price list and the check item are out of the instructions; the screen shows the exact cost of each setting.</p>
    <div class="warnbox"><p><b>Why the chance does not pay the representative.</b> If it did, a reviewer's wish to reward a representative they like would be added to their belief in that representative's calls, and the two cannot be separated in the data. A gender-linked wish (warmth, paternalism) would sit exactly on the hypothesis. The review panel called this unanimously. The representative's bonus keeps its audience sources, the win-gated placement and the two stated 0-10 items, so your Stage 2 sentence "up to $2.00" stays true.</p></div>
    <p>Placement in the flow: the choice comes after the last same-representative review, not before it, so every reviewer still gives the full series of placements that carries the primary DV; the final review is one extra real review (about a minute, up to $0.50 more per reviewer). The organization question that pass 15 put on this page is gone (it was the second job that made the page confusing); the two 0-10 items on Page 7 carry the representative-level and organization-level verdicts as before.</p>"""

    s2html = "".join(pair_html(t, o, n, w, f"s2-{i}") for i, (t, o, n, w) in enumerate(STAGE2))
    s3html = "".join(pair_html(t, o, n, w, f"s3-{i}") for i, (t, o, n, w) in enumerate(STAGE3))

    calls = """
    <ol class="calls">
      <li><b>Chance pays the representative?</b> <span class="d">Default: no. The chance sets only the reviewer's own final review; the stated 0-10 item pays.</span></li>
      <li><b>Price table.</b> <span class="d">Default: one cent more per step (0, 1, 3, 6, 10, 15 cents), paid from the reviewer's own review earnings per your note; shown on the screen, not in the instructions.</span></li>
      <li><b>How much to telegraph before the reviews.</b> <span class="d">Default: light ("one choice about your final review, explained when you reach it"), so reviewers do not place differently on the rounds that carry the primary DV. Fuller two-sentence variant is in Sol's notes.</span></li>
      <li><b>Organization spillover.</b> <span class="d">Settled by your Aug 26 note: Page 6B has one job; the paid 0-10 organization item on Page 7 carries the spillover DV as in the live doc.</span></li>
      <li><b>Organization descriptor on Stage 2 Page 1.</b> <span class="d">Sol chose one plain phrase for "an organization that ..."; his notes give an alternative. Pick one.</span></li>
      <li><b>"Representative" or "referrer".</b> <span class="d">Default: keep representative as the noun (it carries the organization and is in every screen and item) and use refer / referral / vouch as the verbs. Sol listed every sentence that would change under the rename.</span></li>
      <li><b>"The representative knew that independent reviewers would see the referrals" (Stage 3 Page 1).</b> <span class="d">You cut the earlier version in pass 14. The new framing argues for it; the draft has it in.</span></li>
      <li><b>Stage 2 comprehension item 4.</b> <span class="d">Its correct option ("one reviewed decision and one of its reviewers, both chosen at random") is no longer stated anywhere since your Aug 25 edit removed the reviewer clause from Page 4. Either restore "and one of its reviewers" or reword the option to "one of my reviewed decisions, picked at random".</span></li>
      <li><b>IRB and Prolific listing.</b> <span class="d">One extra paid review, and a choice that can cost part of the review earnings, are protocol changes.</span></li>
    </ol>"""

    prov = md_block(review_md) if review_md else "<p>Review results pending.</p>"

    page = f"""<title>Referral Draft, Pass 15</title>
{FONTS}
<style>{CSS}</style>
<main>
  <div class="eyebrow">Sponsor network, Stage 2 + Stage 3, design doc draft</div>
  <h1>Onboarding, referral framing, and an incentivized ask</h1>
  <p class="lede" style="margin-top:12px"><span class="state">Applied to the doc, Aug 26</span> &nbsp; The text on the right is now in the Google Doc (pass 18: passes 15-17 plus the organizational identity on Stage 2 Page 1); the surveys are untouched. The left column is the doc as it was before this apply (which already includes your and your advisor's Aug 25 edits), the mechanism behind the new choice page, and the calls only you can make.</p>
  <nav class="toc"><a href="#asks">The three asks</a><a href="#mech">The choice page mechanism</a><a href="#s2">Stage 2 pages</a><a href="#s3">Stage 3 pages</a><a href="#calls">Open calls</a><a href="#prov">Who did what</a></nav>

  <h2 id="asks">The three asks, and what the draft does with each</h2>
  {asks}

  <h2 id="mech">The choice page mechanism</h2>
  {mech}

  <h2 id="s2">Stage 2 pages (representatives)</h2>
  <p class="lede">Page 2 (the candidates) is byte-identical and not shown. Left: the live doc. Right: the draft. "Show as redline" gives the word-level diff.</p>
  {s2html}

  <h2 id="s3">Stage 3 pages (independent reviewers)</h2>
  <p class="lede">The five pre-review comprehension items are unchanged; per your note there is no check on the choice page. The review and result screens are mockups and unchanged.</p>
  {s3html}

  <h2 id="calls">Open calls (yours to make)</h2>
  {calls}

  <h2 id="prov">Who did what</h2>
  <div class="prov">{prov}</div>
</main>
{DEMO_JS}
"""
    open(OUT, "w", encoding="utf-8").write(page)
    assert "\u2014" not in page, "em dash in generated page"
    print("wrote", OUT, len(page), "chars")


if __name__ == "__main__":
    build()
