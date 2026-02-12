// ============================================================
// QID5 — Stage 3, Outcome Screen (Feedback/Results)
// ============================================================
// UPDATED: STIM array updated to 10 pairs matching Stage 2.
// Logic is unchanged — it already reads from embedded data.
// ============================================================

Qualtrics.SurveyEngine.addOnReady(function () {
  "use strict";
  var q = this, $ = window.jQuery;
  var start = Date.now();

  var qc = q.getQuestionContainer();
  var container = q.getQuestionTextContainer ? q.getQuestionTextContainer() : qc;

  var textInput = qc.querySelector('input[type="text"], input.InputText, textarea');
  if (textInput) textInput.style.display = 'none';

  // UI nodes
  var endImg   = container.querySelector('#endorser_img');
  var endMeta  = container.querySelector('#endorser_meta');
  var selIDEl  = container.querySelector('#selected_id');
  var eFill    = container.querySelector('#e_fill');
  var eReading = container.querySelector('#e_reading');

  // Result-first UI
  var yourAmt    = container.querySelector('#your_amount');
  var yourReason = container.querySelector('#your_reason');
  var endOutcome = container.querySelector('#endorser_outcome_pill');

  // Stake & payouts
  var stakeFill  = container.querySelector('#stake_fill');
  var stakeText  = container.querySelector('#stake_text');
  var payCorrectEl   = container.querySelector('#pay_correct');
  var payIncorrectEl = container.querySelector('#pay_incorrect');
  var payBoxCorrect  = container.querySelector('#pay_box_correct');
  var payBoxIncorrect= container.querySelector('#pay_box_incorrect');
  var tagCorrect     = container.querySelector('#tag_happened_correct');
  var tagIncorrect   = container.querySelector('#tag_happened_incorrect');

  // Icons
  var ICON = {
    "Woman": "https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_rPkPsDPTOJEHbxS",
    "Man":   "https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_2XVqkTCg6PGauA7"
  };

  function interpEndorser(v){
    v = Number(v);
    if (v === 50) return "Endorser was unsure";
    if (v < 50)  return (v <= 15) ? "Endorser was very confident in Candidate A" : "Endorser leaned toward Candidate A";
    return (v >= 85) ? "Endorser was very confident in Candidate B" : "Endorser leaned toward Candidate B";
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

  function populate(){
    // Header cards
    endImg.src = (endorserGender === "Woman") ? ICON.Woman : ICON.Man;
    endImg.alt = "Endorser icon";
    endMeta.textContent = "ID " + endorserId;

    selIDEl.textContent = selectedId;
    eFill.style.width = eVal + "%";
    eReading.textContent = eVal + " \u2014 " + interpEndorser(eVal);

    // Compute payouts
    stake = Math.max(0, Math.min(100, stake));
    var payCorrect   = (2 * (stake/100));
    var payIncorrect = (2 * (1 - stake/100));
    var realized     = isCorrect ? payCorrect : payIncorrect;

    // Result-first banner
    yourAmt.textContent = "$" + realized.toFixed(2);
    yourReason.textContent = "You staked " + stake + "% and the endorser was " + (isCorrect ? "correct." : "incorrect.");
    endOutcome.textContent = isCorrect ? "Endorser: Correct" : "Endorser: Incorrect";
    endOutcome.classList.toggle('ok',  isCorrect);
    endOutcome.classList.toggle('bad', !isCorrect);

    // Stake bar & comparison boxes
    stakeFill.style.width = stake + "%";
    stakeText.textContent = "You staked " + stake + "% of your $2 bonus on this endorsement.";

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

  $(document).off('click.s3Outcome','#NextButton').on('click.s3Outcome','#NextButton',saveResponse);
  if (typeof q.addOnUnload === 'function'){ q.addOnUnload(saveResponse); }
  else { window.addEventListener('beforeunload', saveResponse); }

  populate();
});
