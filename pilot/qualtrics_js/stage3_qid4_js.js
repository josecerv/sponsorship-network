// ============================================================
// QID4 — Stage 3, Q2: Second Evaluator Stake Decision
// ============================================================
// UPDATED: Reads Q2 pair + endorser slider from embedded data
// (set by QID3's condition assignment) instead of randomizing.
// ============================================================

Qualtrics.SurveyEngine.addOnReady(function () {
  "use strict";
  var q = this, $ = window.jQuery;
  var start = Date.now();

  var qc = q.getQuestionContainer();
  var container = q.getQuestionTextContainer ? q.getQuestionTextContainer() : qc;

  var textInput = qc.querySelector('input[type="text"], input.InputText, textarea');
  if (textInput) textInput.style.display = 'none';

  // UI
  var endImg   = container.querySelector('#endorser_img');
  var endMeta  = container.querySelector('#endorser_meta');
  var selIDEl  = container.querySelector('#selected_id');

  var eFill    = container.querySelector('#e_fill');
  var eReading = container.querySelector('#e_reading');

  var sRng     = container.querySelector('#stake_rng');
  var sFill    = container.querySelector('#stake_fill');
  var sBubble  = container.querySelector('#stake_bubble');
  var sReading = container.querySelector('#stake_reading');
  var sPayC    = container.querySelector('#pay_correct');
  var sPayI    = container.querySelector('#pay_incorrect');

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

  function interpEndorser(v){
    v = Number(v);
    if (v === 50) return "Endorser was unsure";
    if (v < 50)  return (v <= 15) ? "Endorser was very confident in Candidate A" : "Endorser leaned toward Candidate A";
    return (v >= 85) ? "Endorser was very confident in Candidate B" : "Endorser leaned toward Candidate B";
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

  // Read Q2 endorser slider value from embedded data
  var rawEVal = Qualtrics.SurveyEngine.getEmbeddedData('endorser_slider_value_q2');
  var eVal = (rawEVal !== null && rawEVal !== undefined && rawEVal !== '')
    ? Number(rawEVal) : 50;
  if (eVal === 50) eVal = 49; // avoid neutral

  var favoredSide = (eVal > 50) ? 'B' : 'A';
  var chosen = (favoredSide === 'A') ? trial.A : trial.B;

  function populate(){
    endImg.src = (endorserGender === "Woman") ? ICON.Woman : ICON.Man;
    endMeta.textContent = "ID " + endorserId;

    selIDEl.textContent = chosen.id;

    eFill.style.width = eVal + "%";
    eReading.textContent = eVal + " \u2014 " + interpEndorser(eVal);

    // Save Q2-specific data
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_pair_id', trial.pair_id);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_category', trial.category);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_truth', trial.truth);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_selected_label', favoredSide);
    Qualtrics.SurveyEngine.setEmbeddedData('stage3_q2_selected_id', chosen.id);
    Qualtrics.SurveyEngine.setEmbeddedData('endorser_slider_value_q2', eVal);
  }

  function updateStake(){
    var v = Number(sRng.value);
    sBubble.textContent = v + "%";
    sBubble.style.left  = v + "%";
    sFill.style.width   = v + "%";
    sReading.textContent = "Stake " + v + "% of your $2 bonus.";
    sPayC.textContent    = "$" + (2 * (v/100)).toFixed(2);
    sPayI.textContent    = "$" + (2 * (1 - v/100)).toFixed(2);
    if (textInput) textInput.value = v;
  }

  sRng.addEventListener('input', updateStake);
  sRng.addEventListener('keydown', function (e) {
    var step = e.shiftKey ? 5 : 1;
    if (e.key === 'ArrowLeft'){ sRng.value = Math.max(0, Number(sRng.value) - step); updateStake(); e.preventDefault(); }
    if (e.key === 'ArrowRight'){ sRng.value = Math.min(100, Number(sRng.value) + step); updateStake(); e.preventDefault(); }
  });

  var saved = false;
  function saveResponse(){
    if (saved) return; saved = true;
    var stake = Number(sRng.value);
    Qualtrics.SurveyEngine.setEmbeddedData('stake_percent_q2', stake);
    Qualtrics.SurveyEngine.setEmbeddedData('rt_ms_stage3_q2', Date.now() - start);
    if (textInput) textInput.value = stake;
  }

  $(document).off('click.s3Q2','#NextButton').on('click.s3Q2','#NextButton',saveResponse);
  if (typeof q.addOnUnload === 'function'){ q.addOnUnload(saveResponse); }
  else { window.addEventListener('beforeunload', saveResponse); }

  populate();
  updateStake();
});
