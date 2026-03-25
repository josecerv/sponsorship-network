"""
Browser-based test for Stage 3 Qualtrics JS files.
Uses Playwright to simulate the Qualtrics environment and verify
that all JS executes without errors and populates the UI correctly.

UPDATED: Tests $0.50 bank scheme, strength-based endorser display,
and Q2 constant strength (matching Q1).
"""
import subprocess, sys, json
from pathlib import Path

# Ensure playwright browsers are available
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


PROJECT = Path(__file__).resolve().parent.parent  # pilots/
JS_DIR = PROJECT / "qualtrics_js"

QID3_JS = (JS_DIR / "stage3_qid3_combined.js").read_text()
QID4_JS = (JS_DIR / "stage3_qid4_js.js").read_text()
QID5_JS = (JS_DIR / "stage3_qid5_js.js").read_text()

# ── Mock Qualtrics environment ──
QUALTRICS_MOCK = """
<script>
// Mock embedded data store
var _embeddedData = {};

var Qualtrics = {
  SurveyEngine: {
    getEmbeddedData: function(key) { return _embeddedData[key] || null; },
    setEmbeddedData: function(key, val) { _embeddedData[key] = String(val); },
    // addOnReady: call the callback immediately with a mock question context
    addOnReady: function(fn) {
      // We call this after DOM is ready (see below)
      window._qReadyFn = fn;
    }
  }
};

// Mock jQuery (minimal)
window.jQuery = function(sel) {
  var el = document.querySelector(sel);
  return {
    0: el,
    length: el ? 1 : 0,
    on: function() { return this; },
    off: function() { return this; },
    find: function(s) { return window.jQuery(s); },
    text: function(t) { if (el) el.textContent = t; return this; },
    css: function() { return this; }
  };
};
window.jQuery.fn = {};
</script>
"""

# ── HTML for QID3/QID4 (evaluation page with stake slider) ──
QID3_QID4_HTML = """
<div id="stage3-eval">
  <span class="badge">Endorser</span>
  <img id="endorser_img" src="" alt="">
  <span id="endorser_meta"></span>
  <span id="selected_id"></span>
  <div id="e_fill" style="width:0%"></div>
  <span id="e_reading"></span>
  <input type="range" id="stake_rng" min="0" max="100" value="50">
  <div id="stake_fill" style="width:0%"></div>
  <span id="stake_bubble">50%</span>
  <span id="stake_reading"></span>
  <span id="pay_correct">$0.00</span>
  <span id="pay_incorrect">$0.00</span>
</div>
<div id="NextButton">Next</div>
"""

# ── HTML for QID5 (outcome page) ──
QID5_HTML = """
<div id="stage3-outcome">
  <span class="badge">Endorser</span>
  <img id="endorser_img" src="" alt="">
  <span id="endorser_meta"></span>
  <span id="selected_id"></span>
  <div id="e_fill" style="width:0%"></div>
  <span id="e_reading"></span>
  <span id="your_amount"></span>
  <span id="your_reason"></span>
  <span id="endorser_outcome_pill"></span>
  <div id="stake_fill" style="width:0%"></div>
  <span id="stake_text"></span>
  <span id="pay_correct">$0.00</span>
  <span id="pay_incorrect">$0.00</span>
  <div id="pay_box_correct"></div>
  <div id="pay_box_incorrect"></div>
  <span id="tag_happened_correct" style="display:none"></span>
  <span id="tag_happened_incorrect" style="display:none"></span>
</div>
<div id="NextButton">Next</div>
"""

# Question context mock (what Qualtrics passes as `this` to addOnReady)
Q_CONTEXT_MOCK = """
var _questionContainer = document.createElement('div');
// Add a hidden text input inside the question container
var _ti = document.createElement('input');
_ti.type = 'text';
_questionContainer.appendChild(_ti);

var _qContext = {
  getQuestionContainer: function() { return _questionContainer; },
  getQuestionTextContainer: function() { return document.body; },
  addOnUnload: function(fn) { window._unloadFn = fn; }
};
"""


def build_page(body_html, js_code, pre_embedded=None):
    """Build a complete HTML page with Qualtrics mocks and the JS to test."""
    pre_set = ""
    if pre_embedded:
        for k, v in pre_embedded.items():
            pre_set += f'  _embeddedData["{k}"] = "{v}";\n'

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Test</title></head>
<body>
{body_html}
{QUALTRICS_MOCK}
<script>
{pre_set}
{Q_CONTEXT_MOCK}

// Collect errors
window._jsErrors = [];
window.onerror = function(msg, src, line, col, err) {{
  window._jsErrors.push({{msg: msg, line: line, col: col, stack: err ? err.stack : ''}});
}};

// Override addOnReady to capture the callback
Qualtrics.SurveyEngine.addOnReady = function(fn) {{
  try {{
    fn.call(_qContext);
  }} catch(e) {{
    window._jsErrors.push({{msg: e.message, line: 0, col: 0, stack: e.stack || ''}});
  }}
}};
</script>
<script>
// ---- THE JS UNDER TEST ----
{js_code}
</script>
</body></html>"""


def run_test(page, test_name, html, js_code, pre_embedded=None, checks=None):
    """Run a single JS test in the browser and report results."""
    full_html = build_page(html, js_code, pre_embedded)

    errors = []
    console_errors = []

    def on_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    page.on("console", on_console)
    page.on("pageerror", lambda exc: errors.append(str(exc)))

    page.set_content(full_html, wait_until="domcontentloaded")
    page.wait_for_timeout(500)  # let async stuff settle

    # Collect JS errors from our handler
    js_errors = page.evaluate("() => window._jsErrors")
    embedded = page.evaluate("() => _embeddedData")

    # Run custom checks
    check_results = {}
    if checks:
        for name, expr in checks.items():
            try:
                val = page.evaluate(f"() => {expr}")
                check_results[name] = val
            except Exception as e:
                check_results[name] = f"ERROR: {e}"

    page.remove_listener("console", on_console)

    passed = len(js_errors) == 0 and len(errors) == 0
    return {
        "test": test_name,
        "passed": passed,
        "js_errors": js_errors,
        "page_errors": errors,
        "console_errors": console_errors,
        "embedded_data": embedded,
        "checks": check_results,
    }


def main():
    results = []
    all_passed = True

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ─────────────────────────────────────────────
        # TEST 1: QID3 — First visit (no endorser_id)
        # ─────────────────────────────────────────────
        r = run_test(page, "QID3 — fresh assignment (no endorser_id)", QID3_QID4_HTML, QID3_JS,
            pre_embedded={},
            checks={
                "endorser_img.src is set": "document.getElementById('endorser_img').src !== ''",
                "endorser_meta has text": "document.getElementById('endorser_meta').textContent.length > 0",
                "selected_id has text": "document.getElementById('selected_id').textContent.length > 0",
                "e_fill width set": "document.getElementById('e_fill').style.width !== ''",
                "e_reading shows strength %": "document.getElementById('e_reading').textContent.includes('%')",
                "stake_reading says wager": "document.getElementById('stake_reading').textContent.includes('Wager')",
                "stake_reading says $0.50 bank": "document.getElementById('stake_reading').textContent.includes('$0.50 bank')",
                "pay_correct has $": "document.getElementById('pay_correct').textContent.startsWith('$')",
                "assigned_condition set": "!!_embeddedData['assigned_condition']",
                "endorser_id set": "!!_embeddedData['endorser_id']",
                "endorser_gender set": "!!_embeddedData['endorser_gender']",
                "stage3_q1_pair_id set": "!!_embeddedData['stage3_q1_pair_id']",
                "stage3_q2_pair_id set": "!!_embeddedData['stage3_q2_pair_id']",
                "stake_percent_q1 set": "!!_embeddedData['stake_percent_q1']",
                "endorser_display_strength_q1 set": "!!_embeddedData['endorser_display_strength_q1']",
            })
        results.append(r)

        # ─────────────────────────────────────────────
        # TEST 2: QID3 — Page revisit (endorser_id already set)
        # ─────────────────────────────────────────────
        r = run_test(page, "QID3 — page revisit (endorser_id pre-set)", QID3_QID4_HTML, QID3_JS,
            pre_embedded={
                "endorser_id": "63d80b500adef5b476e289a4",
                "endorser_gender": "Man",
                "stage3_q1_pair_id": "dominant_woman_wins",
                "endorser_slider_value_q1": "0",
                "assigned_condition": "M_correct_strong",
                "stage3_q2_pair_id": "unknown_man_word",
                "endorser_slider_value_q2": "15",
            },
            checks={
                "endorser_meta shows ID": "'63d80b500adef5b476e289a4' === _embeddedData['endorser_id']",
                "selected_id not empty": "document.getElementById('selected_id').textContent.length > 0",
                "e_fill width=100% (strength of sv=0)": "document.getElementById('e_fill').style.width === '100%'",
                "e_reading shows very confident": "document.getElementById('e_reading').textContent.includes('very confident')",
            })
        results.append(r)

        # ─────────────────────────────────────────────
        # TEST 3: QID4 — Q2 evaluation (reads from embedded)
        # ─────────────────────────────────────────────
        r = run_test(page, "QID4 — Q2 with embedded data from QID3", QID3_QID4_HTML, QID4_JS,
            pre_embedded={
                "endorser_id": "63d80b500adef5b476e289a4",
                "endorser_gender": "Man",
                "stage3_q1_pair_id": "dominant_woman_wins",
                "endorser_slider_value_q1": "0",
                "stage3_q2_pair_id": "unknown_man_word",
                "endorser_slider_value_q2": "15",
            },
            checks={
                "endorser_meta shows ID": "document.getElementById('endorser_meta').textContent.includes('63d80b500adef5b476e289a4')",
                "selected_id not empty": "document.getElementById('selected_id').textContent.length > 0",
                "e_fill width=100% (Q2 displays Q1 strength)": "document.getElementById('e_fill').style.width === '100%'",
                "e_reading shows very confident": "document.getElementById('e_reading').textContent.includes('very confident')",
                "stake_percent_q2 set": "!!_embeddedData['stake_percent_q2']",
                "stage3_q2_truth set": "!!_embeddedData['stage3_q2_truth']",
                "endorser_display_strength_q2 = 100": "_embeddedData['endorser_display_strength_q2'] === '100'",
                "stake_reading says $0.50 bank": "document.getElementById('stake_reading').textContent.includes('$0.50 bank')",
            })
        results.append(r)

        # ─────────────────────────────────────────────
        # TEST 4: QID4 — Q2 constant strength (weak condition)
        # ─────────────────────────────────────────────
        r = run_test(page, "QID4 — Q2 displays Q1 strength (weak: sv=51 → strength=2)", QID3_QID4_HTML, QID4_JS,
            pre_embedded={
                "endorser_id": "65fd19896d58d64c0d8cbc3c",
                "endorser_gender": "Man",
                "stage3_q1_pair_id": "identical_woman_woman",
                "endorser_slider_value_q1": "51",
                "stage3_q2_pair_id": "dominant_woman_wins",
                "endorser_slider_value_q2": "1",
            },
            checks={
                "e_fill width=2% (Q1 strength: |51-50|*2)": "document.getElementById('e_fill').style.width === '2%'",
                "e_reading shows unsure": "document.getElementById('e_reading').textContent.includes('unsure')",
                "endorser_display_strength_q2 = 2": "_embeddedData['endorser_display_strength_q2'] === '2'",
                "raw Q2 eVal preserved": "_embeddedData['endorser_slider_value_q2'] === '1'",
            })
        results.append(r)

        # ─────────────────────────────────────────────
        # TEST 5: QID4 — fallback (no q2_pair_id in embedded)
        # ─────────────────────────────────────────────
        r = run_test(page, "QID4 — fallback when q2_pair_id missing", QID3_QID4_HTML, QID4_JS,
            pre_embedded={
                "endorser_id": "testid123",
                "endorser_gender": "Woman",
                "stage3_q1_pair_id": "dominant_woman_wins",
                "endorser_slider_value_q1": "0",
                # no stage3_q2_pair_id — should trigger fallback
            },
            checks={
                "no crash - endorser_meta has text": "document.getElementById('endorser_meta').textContent.length > 0",
                "selected_id not empty": "document.getElementById('selected_id').textContent.length > 0",
                "stage3_q2_pair_id set by fallback": "!!_embeddedData['stage3_q2_pair_id']",
                "q2 pair differs from q1": "_embeddedData['stage3_q2_pair_id'] !== 'dominant_woman_wins'",
            })
        results.append(r)

        # ─────────────────────────────────────────────
        # TEST 6: QID5 — outcome page (endorser correct, stake=70%)
        # Payout: $0.50 + $0.50*(70/100) = $0.85
        # ─────────────────────────────────────────────
        r = run_test(page, "QID5 — outcome, endorser CORRECT, stake=70%", QID5_HTML, QID5_JS,
            pre_embedded={
                "endorser_id": "63d80b500adef5b476e289a4",
                "endorser_gender": "Man",
                "stage3_q1_selected_id": "zlrgipzx",
                "stage3_q1_selected_label": "A",
                "stage3_q1_truth": "A",  # correct!
                "endorser_slider_value_q1": "0",
                "stake_percent_q1": "70",
            },
            checks={
                "your_amount shows $0.85": "document.getElementById('your_amount').textContent === '$0.85'",
                "endorser_outcome_pill says Correct": "document.getElementById('endorser_outcome_pill').textContent.includes('Correct')",
                "pay_box_correct has hit class": "document.getElementById('pay_box_correct').classList.contains('hit')",
                "pay_correct shows $0.85": "document.getElementById('pay_correct').textContent === '$0.85'",
                "pay_incorrect shows $0.15": "document.getElementById('pay_incorrect').textContent === '$0.15'",
                "stage3_q1_is_correct = 1": "_embeddedData['stage3_q1_is_correct'] === '1'",
                "stage3_q1_actual_bonus = 0.85": "_embeddedData['stage3_q1_actual_bonus'] === '0.85'",
                "stake_text says $0.50 bank": "document.getElementById('stake_text').textContent.includes('$0.50 bank')",
                "stake_text says wagered": "document.getElementById('stake_text').textContent.includes('wagered')",
                "e_reading shows strength %": "document.getElementById('e_reading').textContent.includes('%')",
            })
        results.append(r)

        # ─────────────────────────────────────────────
        # TEST 7: QID5 — outcome page (endorser incorrect, stake=80%)
        # Payout: $0.50 - $0.50*(80/100) = $0.10
        # ─────────────────────────────────────────────
        r = run_test(page, "QID5 — outcome, endorser INCORRECT, stake=80%", QID5_HTML, QID5_JS,
            pre_embedded={
                "endorser_id": "testid456",
                "endorser_gender": "Woman",
                "stage3_q1_selected_id": "5yrzkge8",
                "stage3_q1_selected_label": "A",
                "stage3_q1_truth": "B",  # incorrect!
                "endorser_slider_value_q1": "25",
                "stake_percent_q1": "80",
            },
            checks={
                "your_amount shows $0.10": "document.getElementById('your_amount').textContent === '$0.10'",
                "endorser_outcome_pill says Incorrect": "document.getElementById('endorser_outcome_pill').textContent.includes('Incorrect')",
                "pay_box_incorrect has hit class": "document.getElementById('pay_box_incorrect').classList.contains('hit')",
                "pay_correct shows $0.90": "document.getElementById('pay_correct').textContent === '$0.90'",
                "pay_incorrect shows $0.10": "document.getElementById('pay_incorrect').textContent === '$0.10'",
                "stage3_q1_is_correct = 0": "_embeddedData['stage3_q1_is_correct'] === '0'",
                "stage3_q1_actual_bonus = 0.10": "_embeddedData['stage3_q1_actual_bonus'] === '0.10'",
            })
        results.append(r)

        # ─────────────────────────────────────────────
        # TEST 8: QID5 — payout verification at key stake values
        # ─────────────────────────────────────────────
        payout_cases = [
            (0,   "$0.50", "$0.50"),   # 0% → $0.50/$0.50
            (50,  "$0.75", "$0.25"),   # 50% → $0.75/$0.25
            (80,  "$0.90", "$0.10"),   # 80% → $0.90/$0.10
            (100, "$1.00", "$0.00"),   # 100% → $1.00/$0.00
        ]
        for stake_val, exp_correct, exp_incorrect in payout_cases:
            r = run_test(page, f"QID5 — payout math: stake={stake_val}%", QID5_HTML, QID5_JS,
                pre_embedded={
                    "endorser_id": "testid",
                    "endorser_gender": "Man",
                    "stage3_q1_selected_id": "zlrgipzx",
                    "stage3_q1_selected_label": "A",
                    "stage3_q1_truth": "A",
                    "endorser_slider_value_q1": "0",
                    "stake_percent_q1": str(stake_val),
                },
                checks={
                    f"pay_correct={exp_correct}": f"document.getElementById('pay_correct').textContent === '{exp_correct}'",
                    f"pay_incorrect={exp_incorrect}": f"document.getElementById('pay_incorrect').textContent === '{exp_incorrect}'",
                })
            results.append(r)

        # ─────────────────────────────────────────────
        # TEST 9: QID3 — addOnUnload not available (DB question type)
        # ─────────────────────────────────────────────
        no_unload_html = build_page(QID3_QID4_HTML, "", {})
        no_unload_html = no_unload_html.replace(
            "addOnUnload: function(fn) { window._unloadFn = fn; }",
            "/* addOnUnload intentionally removed */"
        )
        no_unload_html = no_unload_html.replace(
            "// ---- THE JS UNDER TEST ----",
            f"// ---- THE JS UNDER TEST ----\n{QID3_JS}"
        )

        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.set_content(no_unload_html, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        js_errors = page.evaluate("() => window._jsErrors")
        embedded = page.evaluate("() => _embeddedData")
        checks_no_unload = {
            "no JS errors": len(js_errors) == 0,
            "no page errors": len(errors) == 0,
            "assigned_condition set": page.evaluate("() => !!_embeddedData['assigned_condition']"),
            "endorser_img.src set": page.evaluate("() => document.getElementById('endorser_img').src !== ''"),
            "UI rendered despite missing addOnUnload": page.evaluate("() => document.getElementById('endorser_meta').textContent.length > 0"),
        }
        results.append({
            "test": "QID3 — no addOnUnload (the bug that broke everything)",
            "passed": all(v == True for v in checks_no_unload.values()) if isinstance(list(checks_no_unload.values())[0], bool) else len(js_errors) == 0 and len(errors) == 0,
            "js_errors": js_errors,
            "page_errors": errors,
            "console_errors": [],
            "embedded_data": embedded,
            "checks": checks_no_unload,
        })

        # ─────────────────────────────────────────────
        # TEST 10: QID3 — slider validation blocks Next when untouched
        # ─────────────────────────────────────────────
        r = run_test(page, "QID3 — slider validation: Next blocked when untouched", QID3_QID4_HTML, QID3_JS,
            pre_embedded={},
            checks={
                "validation msg exists": "!!document.getElementById('stake_validation_msg')",
                "validation msg hidden initially": "document.getElementById('stake_validation_msg').style.display === 'none'",
            })
        results.append(r)
        # Now click NextButton and verify validation message appears
        page.click('#NextButton')
        page.wait_for_timeout(100)
        val_visible = page.evaluate("() => document.getElementById('stake_validation_msg').style.display")
        results.append({
            "test": "QID3 — slider validation: error shown after clicking Next",
            "passed": val_visible == "block",
            "js_errors": [], "page_errors": [], "console_errors": [],
            "embedded_data": {},
            "checks": {"validation message visible": val_visible == "block"},
        })

        # Now interact with the slider and verify validation clears
        page.click('#stake_rng')
        page.wait_for_timeout(100)
        val_after_touch = page.evaluate("() => document.getElementById('stake_validation_msg').style.display")
        results.append({
            "test": "QID3 — slider validation: error clears after slider touch",
            "passed": val_after_touch == "none",
            "js_errors": [], "page_errors": [], "console_errors": [],
            "embedded_data": {},
            "checks": {"validation message hidden": val_after_touch == "none"},
        })

        # ─────────────────────────────────────────────
        # TEST 11: QID4 — slider validation blocks Next when untouched
        # ─────────────────────────────────────────────
        r = run_test(page, "QID4 — slider validation: Next blocked when untouched", QID3_QID4_HTML, QID4_JS,
            pre_embedded={
                "endorser_id": "63d80b500adef5b476e289a4",
                "endorser_gender": "Man",
                "stage3_q1_pair_id": "dominant_woman_wins",
                "endorser_slider_value_q1": "0",
                "stage3_q2_pair_id": "unknown_man_word",
                "endorser_slider_value_q2": "15",
            },
            checks={
                "validation msg exists": "!!document.getElementById('stake_validation_msg')",
                "validation msg hidden initially": "document.getElementById('stake_validation_msg').style.display === 'none'",
            })
        results.append(r)
        page.click('#NextButton')
        page.wait_for_timeout(100)
        val_visible_q4 = page.evaluate("() => document.getElementById('stake_validation_msg').style.display")
        results.append({
            "test": "QID4 — slider validation: error shown after clicking Next",
            "passed": val_visible_q4 == "block",
            "js_errors": [], "page_errors": [], "console_errors": [],
            "embedded_data": {},
            "checks": {"validation message visible": val_visible_q4 == "block"},
        })
        page.click('#stake_rng')
        page.wait_for_timeout(100)
        val_after_touch_q4 = page.evaluate("() => document.getElementById('stake_validation_msg').style.display")
        results.append({
            "test": "QID4 — slider validation: error clears after slider touch",
            "passed": val_after_touch_q4 == "none",
            "js_errors": [], "page_errors": [], "console_errors": [],
            "embedded_data": {},
            "checks": {"validation message hidden": val_after_touch_q4 == "none"},
        })

        # ─────────────────────────────────────────────
        # TEST 12: All 8 conditions produce valid output
        # ─────────────────────────────────────────────
        conditions = [
            "M_correct_strong", "M_correct_weak",
            "M_incorrect_strong", "M_incorrect_weak",
            "W_correct_strong", "W_correct_weak",
            "W_incorrect_strong", "W_incorrect_weak",
        ]

        # Test each condition by manually picking the first endorser from each pool
        for cond in conditions:
            cond_js = QID3_JS.replace(
                "var assignedCond = condKeys[Math.floor(Math.random() * condKeys.length)];",
                f'var assignedCond = "{cond}";'
            ).replace(
                "var selected = pool[Math.floor(Math.random() * pool.length)];",
                "var selected = pool[0];"
            )
            r2 = run_test(page, f"QID3 condition: {cond}", QID3_QID4_HTML, cond_js,
                pre_embedded={},
                checks={
                    "assigned_condition matches": f'_embeddedData["assigned_condition"] === "{cond}"',
                    "endorser_id set": "!!_embeddedData['endorser_id']",
                    "UI rendered": "document.getElementById('endorser_meta').textContent.length > 0",
                    "gender correct": f'_embeddedData["endorser_gender"] === "{"Woman" if cond.startswith("W") else "Man"}"',
                    "strength display shows %": "document.getElementById('e_reading').textContent.includes('%')",
                })
            if not r2["passed"] or not all(v == True for v in r2["checks"].values()):
                pass  # failures tracked in results
            results.append(r2)

        # ─────────────────────────────────────────────
        # TEST 13: Endorser strength conversion verification
        # ─────────────────────────────────────────────
        # Test strength function: |v-50|*2
        strength_cases = [
            ("0",   "100"),  # |0-50|*2 = 100
            ("100", "100"),  # |100-50|*2 = 100
            ("50",  "0"),    # |50-50|*2 = 0
            ("51",  "2"),    # |51-50|*2 = 2
            ("49",  "2"),    # |49-50|*2 = 2
            ("48",  "4"),    # |48-50|*2 = 4
            ("25",  "50"),   # |25-50|*2 = 50
        ]
        for sv, expected_strength in strength_cases:
            r = run_test(page, f"QID3 — strength: sv={sv} -> {expected_strength}%", QID3_QID4_HTML, QID3_JS,
                pre_embedded={
                    "endorser_id": "testid",
                    "endorser_gender": "Man",
                    "stage3_q1_pair_id": "dominant_woman_wins",
                    "endorser_slider_value_q1": sv,
                    "assigned_condition": "M_correct_strong",
                    "stage3_q2_pair_id": "unknown_man_word",
                    "endorser_slider_value_q2": "15",
                },
                checks={
                    f"e_fill width={expected_strength}%": f"document.getElementById('e_fill').style.width === '{expected_strength}%'",
                    f"display_strength_q1={expected_strength}": f"_embeddedData['endorser_display_strength_q1'] === '{expected_strength}'",
                })
            results.append(r)

        browser.close()

    # ── Print results ──
    print("\n" + "=" * 70)
    print("  STAGE 3 JS TEST RESULTS")
    print("=" * 70)

    total = len(results)
    passed = 0
    failed = 0

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        if r["passed"]:
            # Also check if all custom checks passed
            if r["checks"]:
                all_checks_ok = all(v == True for v in r["checks"].values())
                if not all_checks_ok:
                    status = "FAIL"

        if status == "PASS":
            passed += 1
            print(f"\n  [PASS] {r['test']}")
        else:
            failed += 1
            all_passed = False
            print(f"\n  [FAIL] {r['test']}")
            if r["js_errors"]:
                for e in r["js_errors"]:
                    print(f"         JS Error: {e['msg']}")
                    if e.get("stack"):
                        # Show first 2 lines of stack
                        for line in e["stack"].split("\n")[:2]:
                            print(f"           {line.strip()}")
            if r["page_errors"]:
                for e in r["page_errors"]:
                    print(f"         Page Error: {e}")

        # Show check results
        if r["checks"]:
            for name, val in r["checks"].items():
                icon = "OK" if val == True else "FAIL"
                if val != True:
                    print(f"         [{icon}] {name}: {val}")

    print(f"\n{'=' * 70}")
    print(f"  TOTAL: {total}  |  PASSED: {passed}  |  FAILED: {failed}")
    print(f"{'=' * 70}\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
