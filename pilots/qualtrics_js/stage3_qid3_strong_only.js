// ============================================================
// QID3 — Stage 3, Q1: Evaluator Stake Decision (STRONG ONLY)
// ============================================================
// UPDATED: $0.50 bank scheme, strength-based endorser display
// Only includes strong conditions (4 pools instead of 8).
// ============================================================

Qualtrics.SurveyEngine.addOnReady(function () {
  "use strict";
  var q = this, $ = window.jQuery;
  var start = Date.now();

  var qc = q.getQuestionContainer();
  var container = q.getQuestionTextContainer ? q.getQuestionTextContainer() : qc;

  // Hide default text entry; keep as backup store
  var textInput = qc.querySelector('input[type="text"], input.InputText, textarea');
  if (textInput) textInput.style.display = 'none';

  // UI nodes — use document.getElementById for reliability across Qualtrics modes
  var endImg   = document.getElementById('endorser_img');
  var endMeta  = document.getElementById('endorser_meta');
  var selIDEl  = document.getElementById('selected_id');

  // Endorser slider (read-only display)
  var eFill    = document.getElementById('e_fill');
  var eReading = document.getElementById('e_reading');

  // Evaluator stake slider (active)
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

  // ── CONDITION POOLS: Strong conditions only ──
  var CONDITION_POOLS = {
    "M_correct_strong": [
      {eid:"63d80b500adef5b476e289a4", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"unknown_man_word", q2_sv:15},
      {eid:"6598942c3d07928cc188ffdb", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:100, q2_pid:"man_vs_man", q2_sv:1},
      {eid:"5f5452df72345118f58d187b", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"misleading_man_looks_better", q2_sv:0},
      {eid:"62877d5f6a054e53313ac916", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"split_unknowns", q2_sv:99},
      {eid:"63ecff07b619306f41db42fa", eg:"Man", q1_pid:"dominant_man_wins", q1_sv:0, q2_pid:"dominant_woman_wins", q2_sv:1},
      {eid:"55d234b45bc5bc0005d9039d", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"unknown_woman_gk", q2_sv:75},
      {eid:"62029a55ef1cb18a1337c61a", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"dominant_man_wins", q2_sv:5},
      {eid:"66b01097e95b0626c2cd7b5c", eg:"Man", q1_pid:"misleading_woman_looks_better", q1_sv:100, q2_pid:"dominant_man_wins", q2_sv:5}
    ],
    "M_incorrect_strong": [
      {eid:"59e7477e3e4b5a00016aa4d2", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:100, q2_pid:"split_unknowns", q2_sv:1},
      {eid:"5eac686d82cc012af1e953c7", eg:"Man", q1_pid:"unknown_woman_gk", q1_sv:100, q2_pid:"man_vs_man", q2_sv:82},
      {eid:"591d369e88bbb500013a8517", eg:"Man", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"unknown_woman_gk", q2_sv:86},
      {eid:"6398db762e009c7af9e1da88", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:0, q2_pid:"unknown_woman_gk", q2_sv:85},
      {eid:"67a95d468d14bd6324b4bbba", eg:"Man", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"close_woman_wins", q2_sv:81},
      {eid:"6702c3ee33eed6369eb34c8f", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:0, q2_pid:"split_unknowns", q2_sv:20},
      {eid:"570521cfde5095001018a0c8", eg:"Man", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"man_vs_man", q2_sv:7},
      {eid:"633c74ad6178784ed5b52104", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:0, q2_pid:"dominant_man_wins", q2_sv:5}
    ],
    "W_correct_strong": [
      {eid:"R_6LuSAqe1z1kqjId", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:100, q2_pid:"unknown_man_word", q2_sv:61},
      {eid:"5f285dc5b09b3715fa20a14c", eg:"Woman", q1_pid:"dominant_man_wins", q1_sv:0, q2_pid:"unknown_woman_gk", q2_sv:75},
      {eid:"6632e71b65934c5810fb2eff", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:100, q2_pid:"dominant_man_wins", q2_sv:94},
      {eid:"5d537c0cecc84200153075e9", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"unknown_man_word", q2_sv:4},
      {eid:"67215f2922159d42abf932a4", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"dominant_man_wins", q2_sv:8},
      {eid:"6643d22289210a4edf21e84d", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"man_vs_man", q2_sv:7},
      {eid:"663e26ccdbc470527165388b", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:0, q2_pid:"man_vs_man", q2_sv:21},
      {eid:"5f5967d6e280e61b2db8e55c", eg:"Woman", q1_pid:"dominant_man_wins", q1_sv:0, q2_pid:"man_vs_man", q2_sv:90}
    ],
    "W_incorrect_strong": [
      {eid:"62d59a066ee263bb659aa445", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"split_unknowns", q2_sv:91},
      {eid:"62b628e4351d179f1ff6cc59", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"unknown_woman_gk", q2_sv:65},
      {eid:"655f96e689f922fe983fed35", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"misleading_man_looks_better", q2_sv:13},
      {eid:"671498899f67df85f33ea053", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"close_woman_wins", q2_sv:90},
      {eid:"5c005838232b6c0001221acf", eg:"Woman", q1_pid:"dominant_man_wins", q1_sv:100, q2_pid:"misleading_man_looks_better", q2_sv:83},
      {eid:"61bb392e40db417c1a138dcb", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"identical_woman_woman", q2_sv:5},
      {eid:"66db9db4324609f1a7231f49", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"dominant_man_wins", q2_sv:1},
      {eid:"65714a2185b7c4c7ee00ddcd", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:0, q2_pid:"misleading_man_looks_better", q2_sv:15}
    ],
  };

  // ── Condition assignment (runs once per evaluator) ──
  var endorserId = Qualtrics.SurveyEngine.getEmbeddedData('endorser_id');
  var endorserGender, eVal, trial;

  if (!endorserId) {
    // First page in block: assign condition from CONDITION_POOLS
    var condKeys = Object.keys(CONDITION_POOLS);
    var assignedCond = condKeys[Math.floor(Math.random() * condKeys.length)];
    var pool = CONDITION_POOLS[assignedCond];
    var selected = pool[Math.floor(Math.random() * pool.length)];

    // Persist all embedded data for this evaluator's session
    Qualtrics.SurveyEngine.setEmbeddedData('assigned_condition', assignedCond);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_id', selected.eid);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_gender', selected.eg);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_pair_id', selected.q1_pid);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_slider_value_q1', selected.q1_sv);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_pair_id', selected.q2_pid);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_slider_value_q2', selected.q2_sv);

    endorserId = selected.eid;
    endorserGender = selected.eg;
    eVal = selected.q1_sv;

    // Look up Q1 trial from STIM
    trial = STIM.find(function(s){ return s.pair_id === selected.q1_pid; });
    if (!trial) trial = STIM[0]; // fallback
  } else {
    // Already assigned (e.g., page revisit) — read from embedded data
    endorserGender = Qualtrics.SurveyEngine.getEmbeddedData('endorser_gender') || 'Man';
    var q1PairId = Qualtrics.SurveyEngine.getEmbeddedData('stage3_q1_pair_id');
    trial = STIM.find(function(s){ return s.pair_id === q1PairId; });
    if (!trial) trial = STIM[0];

    var rawEVal = Qualtrics.SurveyEngine.getEmbeddedData('endorser_slider_value_q1');
    eVal = (rawEVal !== null && rawEVal !== undefined && rawEVal !== '')
      ? Number(rawEVal) : 50;
  }

  // Determine which candidate the endorser favored
  var favoredSide = (eVal > 50) ? 'B' : 'A';
  var chosen = (favoredSide === 'A') ? trial.A : trial.B;

  // Compute endorsement strength for display
  var strength = endorserStrength(eVal);

  // ── Populate UI ──
  function populate(){
    endImg.src = (endorserGender === "Woman") ? ICON.Woman : ICON.Man;
    endImg.alt = "Endorser";
    endImg.onerror = function(){ this.style.display='none'; };
    var badge = document.querySelector('#stage3-eval .badge');
    if (badge) badge.textContent = "Endorser";
    endMeta.textContent = "ID " + endorserId;

    selIDEl.textContent = chosen.id;

    // Endorser confidence bar (read-only, strength-based)
    eFill.style.width = strength + "%";
    eReading.setAttribute('aria-label', 'Endorsement strength: ' + strength + '%, ' + interpStrength(strength));
    eReading.textContent = strength + "% \u2014 " + interpStrength(strength);

    // Save Q1-specific data
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_pair_id', trial.pair_id);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_category', trial.category);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_truth', trial.truth);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_selected_label', favoredSide);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q1_selected_id', chosen.id);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_slider_value_q1', eVal);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_display_strength_q1', strength);
  }

  // ── Evaluator stake slider ──
  function updateStake(){
    var v = Number(sRng.value);
    sBubble.textContent = v + "%";
    sBubble.style.left  = v + "%";
    sFill.style.width   = v + "%";
    sReading.textContent = "Wager " + v + "% of your $0.50 bank.";
    sPayC.textContent    = "$" + (0.50 + 0.50 * (v/100)).toFixed(2);
    sPayI.textContent    = "$" + (0.50 - 0.50 * (v/100)).toFixed(2);

    Qualtrics.SurveyEngine.setEmbeddedData('stake_percent_q1', v);
    Qualtrics.SurveyEngine.setEmbeddedData('stake_percent_q1_live', v);

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

  // ── Save on Next ──
  var saved = false;
  function saveResponse(){
    if (saved) return; saved = true;
    var stake = Number(sRng.value);
    Qualtrics.SurveyEngine.setEmbeddedData('stake_percent_q1', stake);
    Qualtrics.SurveyEngine.setEmbeddedData('rt_ms_stage3_q1', Date.now() - start);
    if (textInput) textInput.value = stake;
  }

  populate();
  updateStake();

  // Save handlers — registered AFTER UI render so errors here don't block display
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
