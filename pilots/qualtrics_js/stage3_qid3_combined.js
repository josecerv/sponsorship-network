// ============================================================
// QID3 — Stage 3, Q1: Evaluator Stake Decision
// ============================================================
// UPDATED: $0.50 bank scheme, strength-based endorser display
//
// HOW TO USE:
//   1. Run: python pilot/build_stage3_roster.py
//   2. Copy the CONDITION_POOLS block from pilot/stage3_condition_pools.js
//      and paste it BELOW the "// >>> PASTE CONDITION_POOLS HERE <<<" marker
//   3. Replace the existing QID3 JavaScript in Qualtrics with this file
//   4. Add 'assigned_condition' to Survey Flow embedded data fields
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

  // ── CONDITION POOLS: Real endorser data from Stage 2 ──
  var CONDITION_POOLS = {
    "M_correct_strong": [
      {eid:"6596d692ac956830b68776e0", eg:"Man", q1_pid:"dominant_man_wins", q1_sv:8, q2_pid:"misleading_woman_looks_better", q2_sv:6},
      {eid:"570521cfde5095001018a0c8", eg:"Man", q1_pid:"man_vs_man", q1_sv:7, q2_pid:"unknown_woman_gk", q2_sv:90},
      {eid:"561bbdf9811d22000df3138a", eg:"Man", q1_pid:"dominant_man_wins", q1_sv:6, q2_pid:"dominant_woman_wins", q2_sv:13},
      {eid:"5e059d2bb1fb05fd1f841142", eg:"Man", q1_pid:"dominant_man_wins", q1_sv:5, q2_pid:"misleading_woman_looks_better", q2_sv:5},
      {eid:"59e7477e3e4b5a00016aa4d2", eg:"Man", q1_pid:"man_vs_man", q1_sv:4, q2_pid:"split_unknowns", q2_sv:1},
      {eid:"559c3e07fdf99b32b55f2d8d", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:3, q2_pid:"misleading_woman_looks_better", q2_sv:5},
      {eid:"5c3a865019ceb400010c914a", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:2, q2_pid:"misleading_man_looks_better", q2_sv:2},
      {eid:"670d816961bebcb45b53b929", eg:"Man", q1_pid:"dominant_woman_wins", q1_sv:1, q2_pid:"misleading_man_looks_better", q2_sv:1}
    ],
    "M_correct_weak": [
      {eid:"665e680164927b18554b66ec", eg:"Man", q1_pid:"identical_woman_woman", q1_sv:51, q2_pid:"misleading_woman_looks_better", q2_sv:5},
      {eid:"641385c88f29eb3264283818", eg:"Man", q1_pid:"close_woman_wins", q1_sv:48, q2_pid:"dominant_woman_wins", q2_sv:2},
      {eid:"60ec54c58f88686dadb1a0c9", eg:"Man", q1_pid:"split_unknowns", q1_sv:53, q2_pid:"dominant_man_wins", q2_sv:6},
      {eid:"67dec78617088acfae7e4475", eg:"Man", q1_pid:"unknown_woman_gk", q1_sv:46, q2_pid:"misleading_woman_looks_better", q2_sv:44},
      {eid:"66bffd8c97a80ac91e1087e0", eg:"Man", q1_pid:"unknown_man_word", q1_sv:55, q2_pid:"dominant_woman_wins", q2_sv:1},
      {eid:"5d951ede9b6f880018f63b6e", eg:"Man", q1_pid:"split_unknowns", q1_sv:56, q2_pid:"close_woman_wins", q2_sv:91},
      {eid:"6750f7eb7c60e2b2c22aeaea", eg:"Man", q1_pid:"split_unknowns", q1_sv:57, q2_pid:"misleading_woman_looks_better", q2_sv:5},
      {eid:"566a3e0e7da0350012b3ec49", eg:"Man", q1_pid:"unknown_man_word", q1_sv:58, q2_pid:"dominant_woman_wins", q2_sv:1}
    ],
    "M_incorrect_strong": [
      {eid:"631c8e97db06f601f81bd82f", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:8, q2_pid:"dominant_man_wins", q2_sv:2},
      {eid:"633f03bb432dc8f74ab3a896", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:7, q2_pid:"dominant_man_wins", q2_sv:12},
      {eid:"5ee00b8630f30b34f2a5dc1c", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:6, q2_pid:"dominant_man_wins", q2_sv:4},
      {eid:"66231fc6e1ecba676935943a", eg:"Man", q1_pid:"misleading_woman_looks_better", q1_sv:5, q2_pid:"dominant_woman_wins", q2_sv:1},
      {eid:"6745f39f437c441b19285a1a", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:4, q2_pid:"dominant_woman_wins", q2_sv:4},
      {eid:"62877d5f6a054e53313ac916", eg:"Man", q1_pid:"man_vs_man", q1_sv:97, q2_pid:"split_unknowns", q2_sv:99},
      {eid:"63ecff07b619306f41db42fa", eg:"Man", q1_pid:"misleading_man_looks_better", q1_sv:2, q2_pid:"dominant_woman_wins", q2_sv:1},
      {eid:"6675f3ac3a5d0633257190c4", eg:"Man", q1_pid:"misleading_woman_looks_better", q1_sv:1, q2_pid:"man_vs_man", q2_sv:86}
    ],
    "M_incorrect_weak": [
      {eid:"67aa52dcb66d138fca70a211", eg:"Man", q1_pid:"identical_woman_woman", q1_sv:49, q2_pid:"misleading_man_looks_better", q2_sv:5},
      {eid:"66956649d7179281d46fa6f2", eg:"Man", q1_pid:"unknown_man_word", q1_sv:48, q2_pid:"dominant_woman_wins", q2_sv:5},
      {eid:"673b834c1ca9feb154a86523", eg:"Man", q1_pid:"split_unknowns", q1_sv:47, q2_pid:"dominant_woman_wins", q2_sv:89},
      {eid:"5f2f03deec679e2cf4a992e6", eg:"Man", q1_pid:"identical_woman_woman", q1_sv:46, q2_pid:"dominant_man_wins", q2_sv:6},
      {eid:"5e5731e3e1e8b90e25c1f3a2", eg:"Man", q1_pid:"split_unknowns", q1_sv:45, q2_pid:"misleading_man_looks_better", q2_sv:11},
      {eid:"629186f7e2f20297ead170be", eg:"Man", q1_pid:"close_woman_wins", q1_sv:56, q2_pid:"dominant_man_wins", q2_sv:1},
      {eid:"5ced8f96a726ed0015d31452", eg:"Man", q1_pid:"identical_woman_woman", q1_sv:43, q2_pid:"dominant_man_wins", q2_sv:1},
      {eid:"612962f44f151ddfd0298c52", eg:"Man", q1_pid:"unknown_man_word", q1_sv:42, q2_pid:"dominant_woman_wins", q2_sv:12}
    ],
    "W_correct_strong": [
      {eid:"6679dc943f855ba978447c25", eg:"Woman", q1_pid:"dominant_man_wins", q1_sv:8, q2_pid:"close_woman_wins", q2_sv:89},
      {eid:"66200b032829f40f3664afdf", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:7, q2_pid:"unknown_man_word", q2_sv:2},
      {eid:"660de2426df2c14f27678f6b", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:6, q2_pid:"misleading_man_looks_better", q2_sv:1},
      {eid:"611341c34be95409850e4341", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:5, q2_pid:"misleading_woman_looks_better", q2_sv:5},
      {eid:"6754246c81ce61cb6ffe887f", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:4, q2_pid:"misleading_man_looks_better", q2_sv:2},
      {eid:"61033627c32742424aeaaac1", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:3, q2_pid:"misleading_woman_looks_better", q2_sv:3},
      {eid:"6632944bbc110f7862810d5a", eg:"Woman", q1_pid:"man_vs_man", q1_sv:2, q2_pid:"dominant_woman_wins", q2_sv:4},
      {eid:"67ddbba0fa5e1ce984f9fb87", eg:"Woman", q1_pid:"dominant_woman_wins", q1_sv:1, q2_pid:"dominant_man_wins", q2_sv:93}
    ],
    "W_correct_weak": [
      {eid:"65e8ff784cc1b2fc71bc5368", eg:"Woman", q1_pid:"close_woman_wins", q1_sv:49, q2_pid:"misleading_woman_looks_better", q2_sv:5},
      {eid:"66ccca31c45aad520357f3fb", eg:"Woman", q1_pid:"identical_woman_woman", q1_sv:52, q2_pid:"misleading_woman_looks_better", q2_sv:1},
      {eid:"59d7c0f750f88f000161eb21", eg:"Woman", q1_pid:"identical_woman_woman", q1_sv:53, q2_pid:"misleading_man_looks_better", q2_sv:19},
      {eid:"652ecb92078fe073ab29b920", eg:"Woman", q1_pid:"identical_woman_woman", q1_sv:54, q2_pid:"dominant_man_wins", q2_sv:1},
      {eid:"662945728093113a43ab8077", eg:"Woman", q1_pid:"split_unknowns", q1_sv:55, q2_pid:"unknown_woman_gk", q2_sv:75},
      {eid:"5b81e0a72ce68d0001fa68d5", eg:"Woman", q1_pid:"split_unknowns", q1_sv:56, q2_pid:"dominant_man_wins", q2_sv:12},
      {eid:"66db9db4324609f1a7231f49", eg:"Woman", q1_pid:"identical_woman_woman", q1_sv:57, q2_pid:"dominant_man_wins", q2_sv:1},
      {eid:"66e7853b4e311a12f93b5411", eg:"Woman", q1_pid:"close_woman_wins", q1_sv:42, q2_pid:"dominant_woman_wins", q2_sv:2}
    ],
    "W_incorrect_strong": [
      {eid:"66d9d8108156d32cbe34ee6f", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:8, q2_pid:"man_vs_man", q2_sv:10},
      {eid:"67e188720841b364cd463eaa", eg:"Woman", q1_pid:"misleading_man_looks_better", q1_sv:7, q2_pid:"dominant_woman_wins", q2_sv:2},
      {eid:"5fab34d5e971f1617667232e", eg:"Woman", q1_pid:"unknown_woman_gk", q1_sv:94, q2_pid:"dominant_woman_wins", q2_sv:1},
      {eid:"5e05ab290db892fcd8036b1a", eg:"Woman", q1_pid:"misleading_man_looks_better", q1_sv:5, q2_pid:"unknown_woman_gk", q2_sv:65},
      {eid:"5d537c0cecc84200153075e9", eg:"Woman", q1_pid:"unknown_man_word", q1_sv:4, q2_pid:"misleading_woman_looks_better", q2_sv:4},
      {eid:"641386b1cb9a9c1e3569d4ee", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:3, q2_pid:"dominant_woman_wins", q2_sv:2},
      {eid:"65cce024500351e8c8f7ff26", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:2, q2_pid:"dominant_woman_wins", q2_sv:6},
      {eid:"65dca046786b41c22b4de4e6", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:1, q2_pid:"unknown_man_word", q2_sv:4}
    ],
    "W_incorrect_weak": [
      {eid:"5e9f3f09ccc75a0c345e4845", eg:"Woman", q1_pid:"split_unknowns", q1_sv:49, q2_pid:"misleading_woman_looks_better", q2_sv:5},
      {eid:"63d5b810f3dbbd11e7e65870", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:48, q2_pid:"close_woman_wins", q2_sv:98},
      {eid:"671165ce01cd9c2699b90dc1", eg:"Woman", q1_pid:"identical_woman_woman", q1_sv:47, q2_pid:"misleading_man_looks_better", q2_sv:6},
      {eid:"65bf99712dfa1f05ee0333c8", eg:"Woman", q1_pid:"identical_woman_woman", q1_sv:46, q2_pid:"dominant_woman_wins", q2_sv:2},
      {eid:"61496cada4d62f06804fa610", eg:"Woman", q1_pid:"identical_woman_woman", q1_sv:45, q2_pid:"dominant_man_wins", q2_sv:4},
      {eid:"677c314658f46f3c0f19ba34", eg:"Woman", q1_pid:"close_woman_wins", q1_sv:56, q2_pid:"man_vs_man", q2_sv:22},
      {eid:"558b20eefdf99b7dfdbac3c9", eg:"Woman", q1_pid:"misleading_woman_looks_better", q1_sv:43, q2_pid:"unknown_woman_gk", q2_sv:76},
      {eid:"5eb02a40b17a8c0868685d32", eg:"Woman", q1_pid:"unknown_man_word", q1_sv:42, q2_pid:"dominant_woman_wins", q2_sv:9}
    ]
  };

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

  // Compute endorsement strength for display (raw 0-100, then mapped to 10-90)
  var rawStrength = endorserStrength(eVal);
  var strength = displayConfidence(rawStrength);

  // ── Populate UI ──
  function populate(){
    endImg.src = (endorserGender === "Woman") ? ICON.Woman : ICON.Man;
    endImg.alt = "Endorser";
    endImg.onerror = function(){ this.style.display='none'; };
    var gs = GENDER_STYLE[endorserGender] || GENDER_STYLE.Man;

    // 1. Avatar: colored border + tinted bg + glow ring
    endImg.style.border = gs.border;
    endImg.style.backgroundColor = gs.bg;
    endImg.style.boxShadow = gs.shadow;
    if (endorserGender === "Woman") endImg.style.objectPosition = "center 20%";

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

    // Confidence bar
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
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_raw_strength_q1', rawStrength);
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
