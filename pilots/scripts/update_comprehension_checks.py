"""
Update comprehension check questions on Qualtrics survey SV_9Fj2oJ5lxuFUXAy.

Steps:
1. Update QID71 with new CQ1 question (task question)
2. Create new CQ5 question (comparison question)
3. Update comp_check block to remove QID66, add new question
4. Update QID68 scoring JS
5. Update QID69 correction JS
6. Update survey flow branch thresholds for 5 questions
"""

import os
import json
import sys
import requests
from dotenv import load_dotenv

# Load API credentials
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
API_KEY = os.environ['QUALTRICS_API_KEY']
BASE_URL = 'https://wharton.yul1.qualtrics.com'
SURVEY_ID = 'SV_9Fj2oJ5lxuFUXAy'

HEADERS = {
    'X-API-TOKEN': API_KEY,
    'Content-Type': 'application/json',
}

def api_get(path):
    url = f'{BASE_URL}/API/v3{path}'
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def api_put(path, data):
    url = f'{BASE_URL}/API/v3{path}'
    r = requests.put(url, headers=HEADERS, json=data)
    if not r.ok:
        print(f"  PUT error {r.status_code}: {r.text}")
    r.raise_for_status()
    return r.json()

def api_post(path, data):
    url = f'{BASE_URL}/API/v3{path}'
    r = requests.post(url, headers=HEADERS, json=data)
    if not r.ok:
        print(f"  POST error {r.status_code}: {r.text}")
    r.raise_for_status()
    return r.json()

# Track results for summary
results = {}

# ============================================================
# STEP 1: Update QID71 with new CQ1 question
# ============================================================
print("=" * 60)
print("STEP 1: Update QID71 with new CQ1 question")
print("=" * 60)

try:
    # GET current definition
    q71 = api_get(f'/survey-definitions/{SURVEY_ID}/questions/QID71')['result']
    print(f"  Got QID71: {q71.get('QuestionDescription', '?')}")

    # Update fields
    q71['QuestionText'] = "What task(s) must the endorsed candidate score higher on for the prediction to be counted as correct?"
    q71['QuestionText_Unsafe'] = q71['QuestionText']
    q71['Choices'] = {
        "1": {"Display": "Knowledge quiz and word-search puzzle"},
        "2": {"Display": "Logical-reasoning task"},
        "3": {"Display": "All three tasks combined"},
        "4": {"Display": "Any single task of the endorser\u2019s choosing"}
    }
    q71['ChoiceOrder'] = ["1", "2", "3", "4"]
    q71['NextChoiceId'] = 5
    q71['Validation'] = {"Settings": {"ForceResponse": "ON", "Type": "None"}}
    q71['Randomization'] = {"Advanced": None, "TotalRandSubset": "", "Type": "All"}
    q71['DataExportTag'] = "CQ1"

    # PUT back
    api_put(f'/survey-definitions/{SURVEY_ID}/questions/QID71', q71)
    print("  SUCCESS: QID71 updated with new CQ1 question")
    results['step1'] = 'SUCCESS'
except Exception as e:
    print(f"  FAILED: {e}")
    results['step1'] = f'FAILED: {e}'

# ============================================================
# STEP 2: Create new CQ5 question
# ============================================================
print()
print("=" * 60)
print("STEP 2: Create new CQ5 question")
print("=" * 60)

new_qid = None
try:
    new_q = {
        "QuestionText": "Who is the endorsed candidate compared against to determine whether the prediction was correct?",
        "QuestionText_Unsafe": "Who is the endorsed candidate compared against to determine whether the prediction was correct?",
        "QuestionType": "MC",
        "Selector": "SAVR",
        "SubSelector": "TX",
        "Configuration": {
            "QuestionDescriptionOption": "UseText"
        },
        "Choices": {
            "1": {"Display": "A randomly selected candidate from the remaining pool"},
            "2": {"Display": "The next highest-scoring candidate overall"},
            "3": {"Display": "The candidate ranked immediately below them"},
            "4": {"Display": "The average score of all other candidates"}
        },
        "ChoiceOrder": ["1", "2", "3", "4"],
        "Validation": {"Settings": {"ForceResponse": "ON", "Type": "None"}},
        "Randomization": {"Advanced": None, "TotalRandSubset": "", "Type": "All"},
        "DataExportTag": "CQ5",
        "Language": []
    }

    resp = api_post(f'/survey-definitions/{SURVEY_ID}/questions', new_q)
    new_qid = resp['result']['QuestionID']
    print(f"  SUCCESS: Created new question {new_qid}")
    results['step2'] = f'SUCCESS: {new_qid}'
except Exception as e:
    print(f"  FAILED: {e}")
    results['step2'] = f'FAILED: {e}'

if new_qid is None:
    print("\n  Cannot proceed with steps 3-5 without new QID. Exiting.")
    sys.exit(1)

# ============================================================
# STEP 3: Update comp_check block
# ============================================================
print()
print("=" * 60)
print("STEP 3: Update comp_check block (remove QID66, add new question)")
print("=" * 60)

try:
    block = api_get(f'/survey-definitions/{SURVEY_ID}/blocks/BL_3K3qygfHM9HbVZQ')['result']
    print(f"  Got block: {block.get('Description', '?')}")
    print(f"  Current elements: {[e['QuestionID'] for e in block['BlockElements'] if e['Type'] == 'Question']}")

    # New block order: QID67, QID71, NEW_QID, QID60, QID61, QID62
    block['BlockElements'] = [
        {"Type": "Question", "QuestionID": "QID67"},
        {"Type": "Question", "QuestionID": "QID71"},
        {"Type": "Question", "QuestionID": new_qid},
        {"Type": "Question", "QuestionID": "QID60"},
        {"Type": "Question", "QuestionID": "QID61"},
        {"Type": "Question", "QuestionID": "QID62"},
    ]

    api_put(f'/survey-definitions/{SURVEY_ID}/blocks/BL_3K3qygfHM9HbVZQ', block)
    new_order = [e['QuestionID'] for e in block['BlockElements']]
    print(f"  SUCCESS: Block updated. New order: {new_order}")
    results['step3'] = f'SUCCESS: {new_order}'
except Exception as e:
    print(f"  FAILED: {e}")
    results['step3'] = f'FAILED: {e}'

# ============================================================
# STEP 4: Update QID68 scoring JS
# ============================================================
print()
print("=" * 60)
print("STEP 4: Update QID68 scoring JS")
print("=" * 60)

try:
    q68 = api_get(f'/survey-definitions/{SURVEY_ID}/questions/QID68')['result']
    print(f"  Got QID68: {q68.get('QuestionDescription', '?')}")

    new_js = f'''Qualtrics.SurveyEngine.addOnload(function() {{
    var cq1 = "${{q://QID71/SelectedChoicesRecode}}";
    var cq2 = "${{q://QID60/SelectedChoicesRecode}}";
    var cq3 = "${{q://QID61/SelectedChoicesRecode}}";
    var cq4 = "${{q://QID62/SelectedChoicesRecode}}";
    var cq5 = "${{q://{new_qid}/SelectedChoicesRecode}}";

    var score = 0;
    if (cq1 === "2") score++;
    if (cq2 === "2") score++;
    if (cq3 === "2") score++;
    if (cq4 === "3") score++;
    if (cq5 === "1") score++;

    Qualtrics.SurveyEngine.setEmbeddedData("cq_score", String(score));
    Qualtrics.SurveyEngine.setEmbeddedData("cq1_wrong", cq1 !== "2" ? "1" : "0");
    Qualtrics.SurveyEngine.setEmbeddedData("cq2_wrong", cq2 !== "2" ? "1" : "0");
    Qualtrics.SurveyEngine.setEmbeddedData("cq3_wrong", cq3 !== "2" ? "1" : "0");
    Qualtrics.SurveyEngine.setEmbeddedData("cq4_wrong", cq4 !== "3" ? "1" : "0");
    Qualtrics.SurveyEngine.setEmbeddedData("cq5_wrong", cq5 !== "1" ? "1" : "0");

    this.clickNextButton();
}});'''

    q68['QuestionJS'] = new_js
    api_put(f'/survey-definitions/{SURVEY_ID}/questions/QID68', q68)
    print(f"  SUCCESS: QID68 scoring JS updated (now references QID71, QID60, QID61, QID62, {new_qid})")
    results['step4'] = 'SUCCESS'
except Exception as e:
    print(f"  FAILED: {e}")
    results['step4'] = f'FAILED: {e}'

# ============================================================
# STEP 5: Update QID69 correction JS and display logic
# ============================================================
print()
print("=" * 60)
print("STEP 5: Update QID69 correction JS and display logic")
print("=" * 60)

try:
    q69 = api_get(f'/survey-definitions/{SURVEY_ID}/questions/QID69')['result']
    print(f"  Got QID69: {q69.get('QuestionDescription', '?')}")

    new_correction_js = '''Qualtrics.SurveyEngine.addOnReady(function() {
    var container = document.getElementById("correction-items");
    if (!container) return;

    var items = [];

    if (Qualtrics.SurveyEngine.getEmbeddedData("cq1_wrong") === "1") {
        items.push({
            q: "What task(s) must the endorsed candidate score higher on for the prediction to be counted as correct?",
            a: "Logical-reasoning task",
            why: "Endorsers saw the candidates\\u2019 knowledge-quiz and word-search scores, but accuracy is judged by a different task\\u2014the logical-reasoning task\\u2014that neither the endorser nor the evaluator ever sees."
        });
    }
    if (Qualtrics.SurveyEngine.getEmbeddedData("cq5_wrong") === "1") {
        items.push({
            q: "Who is the endorsed candidate compared against to determine whether the prediction was correct?",
            a: "A randomly selected candidate from the remaining pool",
            why: "The endorsed candidate\\u2019s logical-reasoning score is compared against one randomly selected candidate from the remaining pool\\u2014not the next highest scorer or the group average."
        });
    }
    if (Qualtrics.SurveyEngine.getEmbeddedData("cq2_wrong") === "1") {
        items.push({
            q: "How much do you start with for each decision?",
            a: "$0.50",
            why: "You begin each decision with a bank of $0.50. Your wager determines how much of that bank you put at risk."
        });
    }
    if (Qualtrics.SurveyEngine.getEmbeddedData("cq3_wrong") === "1") {
        items.push({
            q: "You wager 50%. The endorser was right. What do you earn?",
            a: "$0.75",
            why: "Payout when correct = $0.50 + $0.50 \\u00d7 (wager/100). At 50% wager: $0.50 + $0.50 \\u00d7 0.50 = $0.75."
        });
    }
    if (Qualtrics.SurveyEngine.getEmbeddedData("cq4_wrong") === "1") {
        items.push({
            q: "How is your total bonus calculated?",
            a: "The sum of both decisions",
            why: "Your total bonus equals the sum of your earnings from both evaluation decisions."
        });
    }

    var html = "";
    for (var i = 0; i < items.length; i++) {
        html += '<div class="correction-item">';
        html += '<div class="q-label">Question: ' + items[i].q + '</div>';
        html += '<div class="correct-answer">Correct answer: ' + items[i].a + '</div>';
        html += '<div class="explanation">' + items[i].why + '</div>';
        html += '</div>';
    }

    container.innerHTML = html;
});'''

    q69['QuestionJS'] = new_correction_js

    # Update display logic: show correction when cq_score = 4 (exactly 1 wrong out of 5)
    q69['DisplayLogic'] = {
        "0": {
            "0": {
                "LogicType": "EmbeddedField",
                "LeftOperand": "cq_score",
                "Operator": "EqualTo",
                "RightOperand": "4",
                "Type": "Expression",
                "Description": "If cq_score = 4 (exactly 1 wrong out of 5)"
            },
            "Type": "If"
        },
        "Type": "BooleanExpression",
        "inPage": False
    }

    api_put(f'/survey-definitions/{SURVEY_ID}/questions/QID69', q69)
    print("  SUCCESS: QID69 correction JS updated, display logic changed to cq_score = 4")
    results['step5'] = 'SUCCESS'
except Exception as e:
    print(f"  FAILED: {e}")
    results['step5'] = f'FAILED: {e}'

# ============================================================
# STEP 6: Update survey flow branch thresholds
# ============================================================
print()
print("=" * 60)
print("STEP 6: Update survey flow branch thresholds")
print("=" * 60)

try:
    flow_resp = api_get(f'/survey-definitions/{SURVEY_ID}/flow')
    flow = flow_resp['result']
    print(f"  Got survey flow ({len(flow.get('Flow', []))} top-level elements)")

    # Find the cq_gate branch and update it
    # Currently screens out if cq_score <= 2 (i.e., 0, 1, or 2)
    # With 5 questions, screen out if cq_score <= 3 (i.e., 0, 1, 2, or 3)
    updated = False
    for element in flow.get('Flow', []):
        if element.get('FlowID') == 'FL_cq_gate':
            print(f"  Found FL_cq_gate branch")
            # Update to screen out 0, 1, 2, 3 (2+ wrong out of 5)
            element['Description'] = 'Screen out if 2+ CQs wrong (score <= 3)'
            element['BranchLogic'] = {
                "0": {
                    "0": {
                        "LogicType": "EmbeddedField",
                        "LeftOperand": "cq_score",
                        "Operator": "EqualTo",
                        "RightOperand": "0",
                        "Type": "Expression",
                        "Description": "cq_score = 0"
                    },
                    "1": {
                        "LogicType": "EmbeddedField",
                        "LeftOperand": "cq_score",
                        "Operator": "EqualTo",
                        "RightOperand": "1",
                        "Type": "Expression",
                        "Description": "Or cq_score = 1",
                        "Conjuction": "Or"
                    },
                    "2": {
                        "LogicType": "EmbeddedField",
                        "LeftOperand": "cq_score",
                        "Operator": "EqualTo",
                        "RightOperand": "2",
                        "Type": "Expression",
                        "Description": "Or cq_score = 2",
                        "Conjuction": "Or"
                    },
                    "3": {
                        "LogicType": "EmbeddedField",
                        "LeftOperand": "cq_score",
                        "Operator": "EqualTo",
                        "RightOperand": "3",
                        "Type": "Expression",
                        "Description": "Or cq_score = 3",
                        "Conjuction": "Or"
                    },
                    "Type": "If"
                },
                "Type": "BooleanExpression"
            }
            updated = True
            break

    if not updated:
        print("  WARNING: FL_cq_gate not found in flow. Searching all elements...")
        # Search recursively
        def find_and_update_branch(elements):
            for el in elements:
                if el.get('FlowID') == 'FL_cq_gate':
                    el['Description'] = 'Screen out if 2+ CQs wrong (score <= 3)'
                    el['BranchLogic']['0']['3'] = {
                        "LogicType": "EmbeddedField",
                        "LeftOperand": "cq_score",
                        "Operator": "EqualTo",
                        "RightOperand": "3",
                        "Type": "Expression",
                        "Description": "Or cq_score = 3",
                        "Conjuction": "Or"
                    }
                    return True
                if 'Flow' in el:
                    if find_and_update_branch(el['Flow']):
                        return True
            return False
        updated = find_and_update_branch(flow.get('Flow', []))

    if updated:
        api_put(f'/survey-definitions/{SURVEY_ID}/flow', flow)
        print("  SUCCESS: Flow updated — screen-out now triggers for cq_score <= 3 (0, 1, 2, or 3)")
        results['step6'] = 'SUCCESS'
    else:
        print("  FAILED: Could not find FL_cq_gate branch in flow")
        results['step6'] = 'FAILED: FL_cq_gate not found'
except Exception as e:
    print(f"  FAILED: {e}")
    results['step6'] = f'FAILED: {e}'

# ============================================================
# SUMMARY
# ============================================================
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  New QID created:     {new_qid}")
print(f"  Step 1 (QID71 CQ1):  {results.get('step1', 'SKIPPED')}")
print(f"  Step 2 (New CQ5):    {results.get('step2', 'SKIPPED')}")
print(f"  Step 3 (Block):      {results.get('step3', 'SKIPPED')}")
print(f"  Step 4 (QID68 JS):   {results.get('step4', 'SKIPPED')}")
print(f"  Step 5 (QID69 JS):   {results.get('step5', 'SKIPPED')}")
print(f"  Step 6 (Flow):       {results.get('step6', 'SKIPPED')}")
print()
print("  Block order: QID67 (intro) -> QID71 (CQ1) -> {} (CQ5) -> QID60 (CQ2) -> QID61 (CQ3) -> QID62 (CQ4)".format(new_qid))
print()
print("  Scoring thresholds (5 questions):")
print("    - Screen out:  cq_score <= 3  (2+ wrong)")
print("    - Correction:  cq_score = 4   (exactly 1 wrong)")
print("    - Pass:        cq_score = 5   (all correct)")
print()
print("  Correct answers:")
print("    CQ1 (QID71): Choice 2 — Logical-reasoning task")
print("    CQ5 ({}):  Choice 1 — A randomly selected candidate".format(new_qid))
print("    CQ2 (QID60): Choice 2 — $0.50")
print("    CQ3 (QID61): Choice 2 — $0.75")
print("    CQ4 (QID62): Choice 3 — The sum of both decisions")
