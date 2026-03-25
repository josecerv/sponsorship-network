// ============================================================
// QID4 — Stage 3, Q2: Second Evaluator Stake Decision
// ============================================================
// UPDATED: $0.50 bank scheme, strength-based endorser display,
// Q2 display strength held constant = Q1 strength.
// ============================================================

Qualtrics.SurveyEngine.addOnReady(function () {
  "use strict";
  var q = this, $ = window.jQuery;
  var start = Date.now();

  var qc = q.getQuestionContainer();
  var container = q.getQuestionTextContainer ? q.getQuestionTextContainer() : qc;

  var textInput = qc.querySelector('input[type="text"], input.InputText, textarea');
  if (textInput) textInput.style.display = 'none';

  // UI — use document.getElementById for reliability across Qualtrics modes
  var endImg   = document.getElementById('endorser_img');
  var endMeta  = document.getElementById('endorser_meta');
  var selIDEl  = document.getElementById('selected_id');

  var eFill    = document.getElementById('e_fill');
  var eReading = document.getElementById('e_reading');

  var sRng     = document.getElementById('stake_rng');
  var sFill    = document.getElementById('stake_fill');
  var sBubble  = document.getElementById('stake_bubble');
  var sReading = document.getElementById('stake_reading');
  var sPayC    = document.getElementById('pay_correct');
  var sPayI    = document.getElementById('pay_incorrect');

  var ICON = {
    "Woman": "https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_rPkPsDPTOJEHbxS",
    "Man":   "https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_2XVqkTCg6PGauA7"
  };
  var GENDER_STYLE = {
    "Woman": {border:"3px solid #DB2777", bg:"#FDF2F8", shadow:"0 0 0 3px #FBCFE8",
              badgeBg:"#FCE7F3", badgeColor:"#9D174D",
              cardBorder:"4px solid #EC4899", cardBg:"#FDF2F8", barColor:"#EC4899"},
    "Man":   {border:"3px solid #2563EB", bg:"#EFF6FF", shadow:"0 0 0 3px #BFDBFE",
              badgeBg:"#DBEAFE", badgeColor:"#1E40AF",
              cardBorder:"4px solid #3B82F6", cardBg:"#EFF6FF", barColor:"#3B82F6"}
  };

  // ── STIM: 10 candidate pairs matching Stage 2 exactly ──
  var STIM = [
    {pair_id:'dominant_woman_wins', category:'Dominant_WomanWins',
      A:{id:'zlrgipzx', gender:'Woman', GK:97, Word:99},
      B:{id:'wdjc417p', gender:'Man',   GK:4,  Word:6},
      truth:'A', truth_gender:'Woman'},
    {pair_id:'dominant_man_wins', category:'Dominant_ManWins',
      A:{id:'7aimr53s', gender:'Man',   GK:88, Word:86},
      B:{id:'okxou2gf', gender:'Woman', GK:4,  Word:62},
      truth:'A', truth_gender:'Man'},
    {pair_id:'misleading_woman_looks_better', category:'ObviousFails_WomanLooksBetter',
      A:{id:'5yrzkge8', gender:'Woman', GK:100, Word:92},
      B:{id:'1unc8ds8', gender:'Man',   GK:11,  Word:31},
      truth:'B', truth_gender:'Man'},
    {pair_id:'misleading_man_looks_better', category:'ObviousFails_ManLooksBetter',
      A:{id:'nuunve0a', gender:'Man',   GK:93, Word:92},
      B:{id:'i8823gif', gender:'Woman', GK:29, Word:86},
      truth:'B', truth_gender:'Woman'},
    {pair_id:'close_woman_wins', category:'Close_WomanWins',
      A:{id:'e9jz82ta', gender:'Woman', GK:76, Word:17},
      B:{id:'fyis6atg', gender:'Man',   GK:81, Word:12},
      truth:'A', truth_gender:'Woman'},
    {pair_id:'identical_woman_woman', category:'Identical_WomanWoman_Bwins',
      A:{id:'zaken6uy', gender:'Woman', GK:68, Word:72},
      B:{id:'3z86qvov', gender:'Woman', GK:68, Word:72},
      truth:'B', truth_gender:'Woman'},
    {pair_id:'unknown_woman_gk', category:'Unknown_WomanGK_ManWins',
      A:{id:'musgffcq', gender:'Man',   GK:41, Word:48},
      B:{id:'i7u34n0x', gender:'Woman', GK:"Unknown", Word:79},
      truth:'A', truth_gender:'Man'},
    {pair_id:'unknown_man_word', category:'Unknown_ManWord_ManWins',
      A:{id:'aoygoszl', gender:'Woman', GK:76, Word:2},
      B:{id:'49ki2ruu', gender:'Man',   GK:18, Word:"Unknown"},
      truth:'B', truth_gender:'Man'},
    {pair_id:'split_unknowns', category:'SplitUnknowns_ManWins',
      A:{id:'gtiak505', gender:'Woman', GK:97, Word:"Unknown"},
      B:{id:'cjivnb9m', gender:'Man',   GK:"Unknown", Word:98},
      truth:'B', truth_gender:'Man'},
    {pair_id:'man_vs_man', category:'ManVsMan_Awins',
      A:{id:'ntxkbei3', gender:'Man', GK:88, Word:62},
      B:{id:'1vrg3e4o', gender:'Man', GK:18, Word:96},
      truth:'A', truth_gender:'Man'}
  ];

  // ── Helpers ──
  function endorserStrength(v) {
    return Math.abs(Number(v) - 50) * 2;
  }

  // Map raw 0-100 strength to 10-90 display range
  function displayConfidence(rawStrength) {
    return Math.round(10 + (rawStrength / 100) * 80);
  }

  // Labels based on display confidence (10-90 scale)
  function interpStrength(d) {
    d = Number(d);
    if (d <= 14) return "unsure";
    if (d <= 36) return "low confidence";
    if (d <= 63) return "moderately confident";
    return "very confident";
  }

  // ── Reuse the SAME endorser from Q1 (already set by QID3) ──
  var endorserId = Qualtrics.SurveyEngine.getEmbeddedData('endorser_id') || 'XXXXXX';
  var endorserGender = Qualtrics.SurveyEngine.getEmbeddedData('endorser_gender') || 'Man';

  // ── Read Q2 pair and slider from embedded data (set by QID3 condition assignment) ──
  var q2PairId = Qualtrics.SurveyEngine.getEmbeddedData('stage3_q2_pair_id');
  var trial = STIM.find(function(s){ return s.pair_id === q2PairId; });

  // Fallback: if Q2 pair not found, pick a random pair excluding Q1
  if (!trial) {
    var prevPair = Qualtrics.SurveyEngine.getEmbeddedData('stage3_q1_pair_id');
    var pool = STIM.filter(function(t){ return !prevPair || t.pair_id !== prevPair; });
    trial = pool[Math.floor(Math.random() * pool.length)];
  }

  // Read Q2 endorser slider value from embedded data (raw bipolar 0-100)
  var rawEVal = Qualtrics.SurveyEngine.getEmbeddedData('endorser_slider_value_q2');
  var eVal = (rawEVal !== null && rawEVal !== undefined && rawEVal !== '')
    ? Number(rawEVal) : 50;
  if (eVal === 50) eVal = 49; // avoid neutral

  // Determine which candidate the endorser favored (from real Q2 value)
  var favoredSide = (eVal > 50) ? 'B' : 'A';
  var chosen = (favoredSide === 'A') ? trial.A : trial.B;

  // ── Q2 display strength = Q1 strength + natural variance (within tercile) ──
  var rawQ1Sv = Qualtrics.SurveyEngine.getEmbeddedData('endorser_slider_value_q1');
  var q1Sv = (rawQ1Sv !== null && rawQ1Sv !== undefined && rawQ1Sv !== '')
    ? Number(rawQ1Sv) : 50;
  var q1RawStrength = endorserStrength(q1Sv);
  var q1Display = displayConfidence(q1RawStrength);

  // Add natural variance: ±5-12 points, clamped to same tercile on 10-90 scale
  var tercileLow, tercileHigh;
  if (q1Display <= 36)      { tercileLow = 10; tercileHigh = 36; }
  else if (q1Display <= 63) { tercileLow = 37; tercileHigh = 63; }
  else                      { tercileLow = 64; tercileHigh = 90; }
  var sign = (Math.random() < 0.5) ? -1 : 1;
  var delta = sign * (5 + Math.floor(Math.random() * 8)); // ±5 to ±12
  var displayStrength = Math.max(tercileLow, Math.min(tercileHigh, q1Display + delta));

  function populate(){
    endImg.src = (endorserGender === "Woman") ? ICON.Woman : ICON.Man;
    endImg.alt = "Endorser";
    endImg.onerror = function(){ this.style.display='none'; };
    var gs = GENDER_STYLE[endorserGender] || GENDER_STYLE.Man;

    // 1. Avatar: colored border + tinted bg + glow ring
    endImg.style.border = gs.border;
    endImg.style.backgroundColor = gs.bg;
    endImg.style.boxShadow = gs.shadow;
    if (endorserGender === "Woman") endImg.style.objectPosition = "44% center";

    // 2. Badge: colored pill
    var badge = document.querySelector('#stage3-eval .badge');
    if (badge) {
      badge.textContent = "Endorser";
      badge.style.backgroundColor = gs.badgeBg;
      badge.style.color = gs.badgeColor;
      badge.style.padding = "3px 12px";
      badge.style.borderRadius = "12px";
      badge.style.fontWeight = "700";
    }

    // 3. Endorser card: colored left accent + tinted background
    var endorserCard = endImg ? endImg.closest('.card') : null;
    if (endorserCard) {
      endorserCard.style.borderLeft = gs.cardBorder;
      endorserCard.style.backgroundColor = gs.cardBg;
    }

    endMeta.textContent = "ID " + endorserId;
    selIDEl.textContent = chosen.id;

    // 4. Confidence bar: gender-colored fill (display 10-90 scale, varied from Q1)
    eFill.style.width = displayStrength + "%";
    eReading.setAttribute('aria-label', 'Endorsement strength: ' + displayStrength + '%, ' + interpStrength(displayStrength));
    eReading.textContent = displayStrength + "% \u2014 " + interpStrength(displayStrength);

    // Save Q2-specific data
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_pair_id', trial.pair_id);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_category', trial.category);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_truth', trial.truth);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_selected_label', favoredSide);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_selected_id', chosen.id);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_slider_value_q2', eVal);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_raw_strength_q1', q1RawStrength);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_display_strength_q1', q1Display);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_display_strength_q2', displayStrength);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_q2_variance_delta', displayStrength - q1Display);
  }

  function updateStake(){
    var v = Number(sRng.value);
    sBubble.textContent = v + "%";
    sBubble.style.left  = v + "%";
    sFill.style.width   = v + "%";
    sReading.textContent = "Wager " + v + "% of your $0.50 bank.";
    sPayC.textContent    = "$" + (0.50 + 0.50 * (v/100)).toFixed(2);
    sPayI.textContent    = "$" + (0.50 - 0.50 * (v/100)).toFixed(2);

    Qualtrics.SurveyEngine.setEmbeddedData('stake_percent_q2', v);

    if (textInput) textInput.value = v;
  }

  // ── Slider validation: must interact before proceeding ──
  var sliderTouched = false;
  var valMsg = document.createElement('div');
  valMsg.id = 'stake_validation_msg';
  valMsg.style.cssText = 'color:#c0392b;font-weight:600;margin:8px 0 0;display:none;text-align:center;font-size:14px;';
  valMsg.textContent = '\u26A0 Please adjust the slider to indicate your wager before continuing.';
  if (sRng.parentNode) sRng.parentNode.appendChild(valMsg);

  function markTouched(){ sliderTouched = true; valMsg.style.display = 'none'; }

  sRng.addEventListener('input', function(){ markTouched(); updateStake(); });
  sRng.addEventListener('mousedown', markTouched);
  sRng.addEventListener('touchstart', markTouched);
  sRng.addEventListener('pointerdown', markTouched);
  sRng.addEventListener('keydown', function (e) {
    var step = e.shiftKey ? 5 : 1;
    if (e.key === 'ArrowLeft'){ markTouched(); sRng.value = Math.max(0, Number(sRng.value) - step); updateStake(); e.preventDefault(); }
    if (e.key === 'ArrowRight'){ markTouched(); sRng.value = Math.min(100, Number(sRng.value) + step); updateStake(); e.preventDefault(); }
  });

  var saved = false;
  function saveResponse(){
    if (saved) return; saved = true;
    var stake = Number(sRng.value);
    Qualtrics.SurveyEngine.setEmbeddedData('stake_percent_q2', stake);
    Qualtrics.SurveyEngine.setEmbeddedData('rt_ms_stage3_q2', Date.now() - start);
    if (textInput) textInput.value = stake;
  }

  populate();
  updateStake();

  var nextBtn = document.getElementById('NextButton');
  if (nextBtn) {
    nextBtn.addEventListener('click', function(e){
      if (!sliderTouched) {
        e.preventDefault();
        e.stopImmediatePropagation();
        valMsg.style.display = 'block';
        sRng.focus();
        return;
      }
      saveResponse();
    }, true);
  }
  if (typeof q.addOnUnload === 'function') { q.addOnUnload(function(){ saveResponse(); }); }
  else { window.addEventListener('beforeunload', saveResponse); }
});
