// ============================================================
// QID5 — Stage 3, Outcome Screen (Feedback/Results)
// ============================================================
// UPDATED: $0.50 bank scheme, strength-based endorser display
// ============================================================

Qualtrics.SurveyEngine.addOnReady(function () {
  "use strict";
  var q = this, $ = window.jQuery;
  var start = Date.now();

  var qc = q.getQuestionContainer();
  var container = q.getQuestionTextContainer ? q.getQuestionTextContainer() : qc;

  var textInput = qc.querySelector('input[type="text"], input.InputText, textarea');
  if (textInput) textInput.style.display = 'none';

  // UI nodes — use document.getElementById for reliability across Qualtrics modes
  var endImg   = document.getElementById('endorser_img');
  var endMeta  = document.getElementById('endorser_meta');
  var selIDEl  = document.getElementById('selected_id');
  var eFill    = document.getElementById('e_fill');
  var eReading = document.getElementById('e_reading');

  // Result-first UI
  var yourAmt    = document.getElementById('your_amount');
  var yourReason = document.getElementById('your_reason');
  var endOutcome = document.getElementById('endorser_outcome_pill');

  // Stake & payouts
  var stakeFill  = document.getElementById('stake_fill');
  var stakeText  = document.getElementById('stake_text');
  var payCorrectEl   = document.getElementById('pay_correct');
  var payIncorrectEl = document.getElementById('pay_incorrect');
  var payBoxCorrect  = document.getElementById('pay_box_correct');
  var payBoxIncorrect= document.getElementById('pay_box_incorrect');
  var tagCorrect     = document.getElementById('tag_happened_correct');
  var tagIncorrect   = document.getElementById('tag_happened_incorrect');

  // Icons
  var ICON = {
    "Woman": "https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_rPkPsDPTOJEHbxS",
    "Man":   "https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_2XVqkTCg6PGauA7"
  };

  // ── Helpers ──
  function endorserStrength(v) {
    return Math.abs(Number(v) - 50) * 2;
  }

  function interpStrength(s) {
    s = Number(s);
    if (s <= 5) return "unsure";
    if (s <= 33) return "low confidence";
    if (s <= 66) return "moderately confident";
    return "very confident";
  }

  // Safe numeric read (preserves 0)
  function readNumberED(key, fallback){
    var raw = Qualtrics.SurveyEngine.getEmbeddedData(key);
    if (raw === null || raw === undefined || raw === "") return fallback;
    var num = Number(raw);
    return isNaN(num) ? fallback : num;
  }

  // Read Q1 data from embedded data (all set by QID3)
  var endorserId     = Qualtrics.SurveyEngine.getEmbeddedData('endorser_id') || 'XXXXXX';
  var endorserGender = Qualtrics.SurveyEngine.getEmbeddedData('endorser_gender') || 'Man';
  var selectedId     = Qualtrics.SurveyEngine.getEmbeddedData('stage3_q1_selected_id') || 'Unknown';
  var selectedSide   = Qualtrics.SurveyEngine.getEmbeddedData('stage3_q1_selected_label'); // 'A'/'B'
  var truthSide      = Qualtrics.SurveyEngine.getEmbeddedData('stage3_q1_truth');          // 'A'/'B'
  var eVal           = readNumberED('endorser_slider_value_q1', 50);
  var stake          = readNumberED('stake_percent_q1',
                        readNumberED('stake_percent_q1_live', 50));

  var isCorrect = (selectedSide && truthSide) ? (selectedSide === truthSide) : false;

  // Compute endorsement strength for display
  var strength = endorserStrength(eVal);

  function populate(){
    // Header cards
    endImg.src = (endorserGender === "Woman") ? ICON.Woman : ICON.Man;
    endImg.alt = "Endorser";
    endImg.onerror = function(){ this.style.display='none'; };
    var badge = document.querySelector('#stage3-outcome .badge');
    if (badge) badge.textContent = "Endorser";
    endMeta.textContent = "ID " + endorserId;

    selIDEl.textContent = selectedId;

    // Endorser confidence bar (strength-based)
    eFill.style.width = strength + "%";
    eReading.setAttribute('aria-label', 'Endorsement strength: ' + strength + '%, ' + interpStrength(strength));
    eReading.textContent = strength + "% \u2014 " + interpStrength(strength);

    // Compute payouts ($0.50 bank scheme)
    stake = Math.max(0, Math.min(100, stake));
    var payCorrect   = 0.50 + 0.50 * (stake/100);
    var payIncorrect = 0.50 - 0.50 * (stake/100);
    var realized     = isCorrect ? payCorrect : payIncorrect;

    // Result-first banner
    yourAmt.textContent = "$" + realized.toFixed(2);
    yourReason.textContent = "You wagered " + stake + "% and the endorser was " + (isCorrect ? "correct." : "incorrect.");
    endOutcome.textContent = isCorrect ? "Endorser: Correct" : "Endorser: Incorrect";
    endOutcome.classList.toggle('ok',  isCorrect);
    endOutcome.classList.toggle('bad', !isCorrect);

    // Stake bar & comparison boxes
    stakeFill.style.width = stake + "%";
    stakeText.textContent = "You wagered " + stake + "% of your $0.50 bank on this endorsement.";

    payCorrectEl.textContent   = "$" + payCorrect.toFixed(2);
    payIncorrectEl.textContent = "$" + payIncorrect.toFixed(2);

    if (isCorrect){
      payBoxCorrect.classList.add('hit');
      tagCorrect.style.display = 'inline-block';
      tagIncorrect.style.display = 'none';
    } else {
      payBoxIncorrect.classList.add('hit');
      tagIncorrect.style.display = 'inline-block';
      tagCorrect.style.display = 'none';
    }

    // Persist realized outcome for analysis
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_is_correct', isCorrect ? '1' : '0');
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_actual_bonus', realized.toFixed(2));
  }

  var saved = false;
  function saveResponse(){
    if (saved) return; saved = true;
    Qualtrics.SurveyEngine.setEmbeddedData('rt_ms_stage3_outcome', Date.now() - start);
    if (textInput) textInput.value = isCorrect ? 'correct' : 'incorrect';
  }

  populate();

  var nextBtn = document.getElementById('NextButton');
  if (nextBtn) nextBtn.addEventListener('click', saveResponse, true);
  if (typeof q.addOnUnload === 'function') { q.addOnUnload(function(){ saveResponse(); }); }
  else { window.addEventListener('beforeunload', saveResponse); }
});
