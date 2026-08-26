# Architecture brief, pass 15 (2026-08-26): onboarding, referral framing, and an incentivized "ask"

Architect: Claude (Fable). Writer: Codex gpt-5.6-sol (high). Status: DRAFT FOR JOSE, nothing applied to the doc or
the surveys. Inputs: `in/jose_comments_2026-08-25.md` (his four comments from the advisor session + what he dictated),
`in/live_cells_2026-08-26.md` (the doc AFTER his and his advisor's hand edits on 2026-08-25; these win),
`in/current_Stage-2.md` / `in/current_Stage-3.md` (pass-14 source, now stale in the cells listed in live_cells).

## 0. What Jose and his advisor asked for (three things, plus what they already changed by hand)

A. ONBOARDING / WORLD-BUILDING (Stage 2, comment on "Welcome to [Vertex/Atlas]"): "maybe we say that we are a temp
   agency, and there's two organizations in this world; you work at Vertex, and your decisions will be under
   scrutiny"; "make it feel a bit more like onboarding"; "to simulate the perspective of the people who hire
   candidates from these types of companies, a separate set of participants are going to be acting as independent
   reviewers of a set of your decisions." Dictated: "giving the sense very early on that the decisions are going to
   be reviewed by someone else."
B. REFERRAL FRAMING OF THE PLACEMENT (Stage 2, comment on "Making your decisions"): "placing a bet on the candidate is
   a measure of confidence or certainty"; "as a representative, you refer candidates from your organization to
   OTHERS"; "referrals generate confidence scores around the people they refer; a higher amount of $0.50 indicates
   your level of confidence in that person"; "people who refer others in real life, if they are accurate, get some
   benefit from that accuracy"; "good referrals = positive incentive, positive view of the referrer and then positive
   view of the organization." Dictated: "less like a betting scheme and more about what this means to others; we
   also wanted to telegraph these preferences."
C. INCENTIVIZE THE ASK (Stage 3, comments on "Two questions ..." and "Later reviews"): "incentive the ask"; "Round 3,
   we can randomly choose from the full set of referrers. We can either randomly pair you with a random other
   referrer or, if you like this particular referrer and want to see their next referral, you can pay money to
   increase the likelihood that they're the one we show you"; "how much can I pay so I can get access to Jose."

Hand edits already live (2026-08-25, keep them): tab titles "STAGE 2: SPONSOR DECISIONS" / "STAGE 3: AUDIENCE
DECISIONS"; Stage 2 Page 4 second paragraph rewritten ("Your bonus is based on one of your reviews, picked at random.
... The second part comes from the independent reviewer: how much of their own money they were willing to place
behind the candidate you endorsed, and how much more of your work they wanted to review afterward. Together, these
decisions determine up to $2.00 of your bonus."); Stage 3 Page 1 dropped "but not the candidates' scores"; all grey
"[Page n: ...]" descriptor lines and the programming-key lines are gone, CQ rows now start "[COMPREHENSION CHECK
QUESTIONS]"; Stage 3 "Final questions" is now only the profile-icon (manipulation) item; a "Demographics" row was
added at the end of both tabs. The two Stage 3 0-10 items and their intro are unchanged.

## 1. The theory in five lines (why these three changes belong together)

Sponsorship is a referral: a representative vouches for a candidate from their own organization, in public, with their
own pay riding on it, in front of an audience that decides (i) how far to follow the call now and (ii) whether they
want more of this person's referrals later. (ii) is the representative's social capital, and it is what the gender
hypothesis is about (bidirectional muted updating of women's social capital; never Foschi). Right now the design
measures (i) with money (the placement) and (ii) with two unpaid 0-10 statements. Change A makes the audience real to
the representative from the first screen (the referral has a receiver). Change B makes the placement read as a
confidence signal to that receiver rather than a private bet. Change C makes (ii) a real, costly choice: the reviewer
pays, out of their own money, to keep (or avoid) this representative's next referral. All three are the same move:
turn "bet on a candidate" into "refer a person to someone who will remember you."

## 2. Change A: onboarding (Stage 2 Page 1, and the matching first lines of Stage 3 Page 1)

World: the study is set up like a staffing agency. Two organizations, Vertex and Atlas, each have candidates they want
placed. Each participant in Stage 2 is a representative of one of them (piped, [Vertex/Atlas]) and refers that
organization's candidates. Independent reviewers in a later study play the receiving side (the people who decide
whether to act on a staffing agency's referral); they belong to no organization.

Design consequence to flag for Jose (his advisor's "two organizations in this world"): the comparison candidate is
then simply from the OTHER organization (Atlas for a Vertex representative), and "Beacon" retires from the Stage 2
mockups. Stage 3 reviewers already see [Atlas/Vertex] on the representative and the backed candidate; "the other
candidate" becomes "the [Vertex/Atlas] candidate". Balanced across gender arms as before. If Jose prefers to keep a
third, unnamed organization for the comparison candidate, the text must say "another organization" as now; Sol
should write the two-organization version and note the one-word fallback.

Order of facts on Stage 2 Page 1 (the "under scrutiny early" ask): (1) the world and your role, two sentences; (2) in
the same breath, who will see your referrals and what they will do with them: independent reviewers in a separate
study will see some of your decisions, decide how much of their own money to place behind each of your referrals,
and, at the end, decide whether they want more of your referrals (and can pay to get them). They will form a view of
you and of [Vertex/Atlas]. (3) What you decide each time (how much of $0.50 to place behind your candidate; you always
back [Vertex/Atlas]; the only decision is how much). (4) One sentence that your bonus depends on one reviewed decision
picked at random, so any decision could count (already in the live text). Everything the current Page 1 states stays
true and stays in; the change is order, the world sentence, and the two reviewer verbs (place behind / want more).

Style: onboarding tone ("You have joined Vertex as a representative" is allowed; "Welcome to Vertex" can stay), still
prose, no sub-headers, no incentive hype, no telegraphed math (Jose's standing rules). Target under 170 words.

## 3. Change B: the placement as a referral confidence signal (Stage 2 Page 3; touches Page 4 and the UI strings)

Keep the payoff rule and the 0/50/100% bullets exactly as they are (they are his approved text and the CQ keys depend on
them). Add, before the rule, two or three sentences that give the amount its meaning: the amount you place is how
strongly you vouch for this candidate; reviewers will see it as your confidence in the referral; the more you place,
the more of your own pay rides on the candidate, which is what makes the signal credible. After the rule, one sentence
on the benefit of being accurate: accurate referrals pay you directly and make reviewers more willing to follow your
next referral and to ask for more of them. Do NOT say "the more you place the more the reviewer will back you" or any
sentence that tells the representative what placement gets them the reviewer's money; the placement must stay their
honest confidence (Jose's standing caution, pass 13). "Bet", "wager", "stake", "gamble" never appear.

Vocabulary decision for Jose (do not decide; write the default and note the variant): DEFAULT keep "representative"
as the role noun (it carries the organization, it is in every mockup and CQ) and use "refer / referral / vouch for /
back" as the verbs. VARIANT rename the role to "referrer" everywhere (his comments use it). Sol writes the default
and lists, in notes, every sentence that would change under the variant.

Stage 2 Page 4 (his rewritten paragraph is the base; keep his sentences): the second part of the bonus now reads as
(a) how much of their own money the reviewer placed behind the candidate you referred and (b) whether the reviewer
paid to keep getting your referrals (see change C; the exact clause depends on the mechanism chosen below; write it
for the recommended mechanism and give the alternative clause for the other one). "Together, these decisions
determine up to $2.00 of your bonus." stays.

Stage 2 UI strings (mockup header and slider title; for the mockups, not the doc text): header "YOU REPRESENT:
VERTEX" can stay; the slider title becomes the referral question (architect's draft: "Your referral: how much of your
$0.50 do you place behind the Vertex candidate?"; keep the anchors "Place 0% ($0.00)" / "Place 100% ($0.50)").

## 4. Change C: the incentivized ask (Stage 3; new page; the two 0-10 items become a real choice)

### 4.1 What is being measured

Social capital as willingness to pay for continued access to this representative's referrals, both directions: pay to
KEEP them (gain) and pay to AVOID them (loss). The hypothesis is about muted updating in BOTH directions for women
representatives, so the measure must not be censored at zero on the failure side. This is the reason a one-sided
"pay to keep, otherwise random" version (the literal comment) is not enough: after a wrong call most reviewers would
sit at $0.00 and the downward side of the effect would be invisible.

### 4.2 Where the choice sits in the flow (recommendation: after the last same-representative review, before one
extra "final review")

The primary DV is the per-round placement change with the SAME representative (frozen: same representative across the
rounds, outcome feedback after each). If the choice comes before the last of those rounds ("round 3" in the comment),
two things go wrong: the last placement is on a different representative for everyone who does not pay (one delta
lost, and the ones who kept the representative are self-selected). So: keep all same-representative reviews as they
are, then the choice page, then ONE additional "final review" whose representative is decided by the choice, with its
own $0.50 and its own result screen. Cost: one more review per reviewer (about a minute) plus the choice budget.
The count stays unstated in the text ("after your reviews with this representative, one final review").

### 4.3 The mechanism (the part that needs the most care)

Notation: the reviewer's earnings on a review are $0.50 + w * $0.50 on a correct call and $0.50 - w * $0.50 on a wrong
one, w = placement fraction. If the reviewer believes the representative's backed candidate wins with probability p,
the best placement is all-or-nothing and the review is worth V(p) = max($0.50, p dollars) to a risk-neutral reviewer.
A representative who has looked good is worth maybe $0.75-0.85 per review; a random representative from the pool
maybe $0.55-0.65; a representative who has looked bad is worth $0.50 (place nothing). So the VALUE DIFFERENCE between
"this representative" and "a random one" (call it D) is roughly -$0.15 to +$0.30. Any willingness-to-pay measure lives
inside that range; it is small in dollars by construction and the DV is a comparison across gender arms, not a
dollar figure with meaning of its own. (Lever if the lab wants more resolution: give the final review a $1.00 bank;
that doubles D. Not recommended without discussion; it breaks the "$0.50 per review" rule.)

M1. LINEAR "pay to raise the chance" (the literal comment: $0.00 = random draw, $0.50 = this representative for sure,
    chance proportional to the amount). NOT incentive-compatible for interior amounts: expected value is linear in
    the amount, so a rational reviewer pays either nothing or everything (everything only if D > $0.50, which is
    impossible). Real people would still pick interior values, but the number would not mean "how much they value
    the representative". Reject, or accept as a pure stated-preference-with-a-price.

M2. CHANCE SLIDER WITH A CONVEX PRICE, 50/50 FREE DEFAULT, TWO-SIDED (architect's recommendation). Screen: "For your
    final review, how likely do you want it to be that the decision comes from this same representative?" A slider
    from 0% (certainly a different representative, drawn at random from all the others) to 100% (certainly this
    representative), starting at 50% (a coin flip, free). Moving away from 50% in either direction costs money from a
    $0.25 choice budget the reviewer receives for this page and keeps if unspent; the price rises faster the further
    they move (schedule shown live under the slider, exactly like the outcome tiles on the review screen). Price =
    $0.25 * ((chance - 50) / 50)^2: 50% $0.00; 60% or 40% $0.01; 70% or 30% $0.04; 80% or 20% $0.09; 90% or 10%
    $0.16; 100% or 0% $0.25 (use 10-point steps on the slider so the table has six rows per side and the pennies are
    clean). Why it works: with a convex price the best chance for a risk-neutral reviewer is interior and increases
    linearly in D. For this schedule the price is (q - 0.5)^2 dollars, its slope is 2(q - 0.5), so the optimum is
    q* = 0.5 + D/2: D = +$0.20 gives 60%, D = -$0.10 gives 45%, and the plausible D range (-$0.15 to +$0.30) maps to
    about 42% to 65%. The CHOSEN CHANCE is therefore a linear readout of how much more (or less) this representative
    is worth to them than a random one; it is two-sided; the reviewer never has to understand an auction rule (they
    see a price for each position, as they see the two outcomes for each placement); and it is the literal "pay money
    to increase the likelihood" from the comment, made incentive-compatible. Calibration is a lab parameter: a flatter
    schedule (for example a $0.10 maximum, price = $0.10 * ((chance - 50) / 50)^2) spreads the same D range over about
    31% to 88% at the cost of smaller stakes (q* = 0.5 + 1.25 * D); a steeper one compresses the readout toward 50%.
    Real reviewers are not risk-neutral EV maximizers, so treat these as the direction of the trade-off, not as
    predictions of where the mass will sit. DV = chosen chance (0-100, expected mass in 20-80) and
    amount paid. Representative's bonus clause (Stage 2 Page 4 and Stage 3 telegraph): the chance the reviewer chose
    becomes dollars on a $1.00 scale (70% = $0.70), replacing the two 0-10 items' $0.05 per point (same $1.00
    maximum, same "if this reviewer is picked" gating). Implementation: one random draw against the chosen chance;
    "a different representative" is drawn from the other Stage 2 representatives (needs their next decision as the
    stimulus; the Stage 2 data has 10 decisions per representative, so this is available); the final review is a
    real review with a real result.

M3. CHOOSE, THEN NAME YOUR PRICE (BDM). "Which do you want for your final review: this representative or one drawn
    at random? How much of your $0.25 choice budget, at most, would you give up to make sure you get your choice?"
    Then a random price is drawn from $0.00-0.25; if it is at or below the stated amount, they pay the drawn price
    and get their choice; otherwise a coin flip decides. Incentive-compatible, gives a signed dollar WTP (+ for keep,
    - for avoid), the "how much would you pay for Jose" number. Costs: the BDM rule needs three sentences and a
    comprehension item, and Prolific samples misbid under BDM at known rates; the dollar readout is bounded by
    D / 2 (because the fallback is a coin flip) so most bids sit in $0.00-0.15.

M4. ONE-SIDED PAY-TO-KEEP (BDM against a random draw, no "avoid" side). Simplest to explain; censored at $0.00 after
    wrong calls; loses the loss side of the hypothesis. Fallback only.

M5. STATED 0-10 ITEMS (current). Free, unincentivized for the reviewer, pays the representative. Keep as the
    documented fallback; do not run alongside M2 (two "how much more of this representative" questions in a row is
    what the pass-13 readers already complained about).

Recommendation: M2, choice page after the last same-representative review, one real final review, $0.25 choice
budget kept if unspent, representative paid on the chosen chance. Ask the lab about M3 if they want a dollar figure
as the headline DV rather than a chance.

### 4.4 The organization spillover (the second of the two old items) as a real choice

On the same page, one free, real choice: "If the draw goes to a different representative, which organization should
they come from?" Options: [Atlas] / [Vertex] / Either (order: piped own org first or randomized; note both). It costs
nothing, it is implemented literally (the draw respects it), and it reveals organization-level spillover without a
second slider. Analysis: three-level ordered DV. It does not pay the representative (the organization view is
telegraphed to representatives, not paid; see change B). If the lab wants the organization item paid, the old $0.05
per point item is the fallback.

### 4.5 What the reviewer must be told, and where

Stage 3 Page 1 (Your role): the world (staffing agency, two organizations, representatives refer their own
candidates), your position (independent reviewer, no organization; you decide how far to follow each referral),
and the fact that the representative KNEW reviewers would see their referrals and that their own pay rode on them
(already in the live text; keep). Stage 3 Page 2 (Making your reviews): the pay rule unchanged; then the telegraph:
after your reviews with this representative, you will choose how likely it is that your final review comes from the
same representative, and you can spend part of a small choice budget to make it more or less likely; your choice and
your decisions may also add to the representative's bonus (modal, once, no mechanics); your own earnings always come
from your reviews and whatever you do not spend of the choice budget. The new CHOICE PAGE carries the full rule in
plain words (the slider, the free 50%, the price rising faster the further from 50%, the budget is theirs to keep,
one draw decides, the final review is a real review). Stage 3 CQ: swap the current item 5 (or add one, Jose's call)
for a choice-page item ("If you leave the slider at 50%, what happens?" A: a coin flip decides between this
representative and a different one, and you keep the whole choice budget). Keep five items if possible.

### 4.6 Truthfulness checklist for the mechanism (every sentence must be literally true when fielded)

- The draw happens exactly as stated (one uniform draw against the chosen chance).
- "A different representative, drawn at random from the other representatives" must be true: the pool is the other
  Stage 2 representatives with an unused decision available in the same candidate-set family.
- The choice budget is paid in full minus the price, on top of the review earnings and the participation payment.
- The representative's bonus clause: "the chance the reviewer chose becomes ..." only for the reviewer picked at
  random, so all representative-facing sentences stay modal ("may", "one of your reviews, picked at random").
- The final review uses the drawn representative's real decision and real outcome.

## 5. What must stay (unchanged rules)

- Vocabulary: representative / independent reviewer / place, amount placed / $0.50; never bet, wager, stake, bank,
  endorser, slots, gamble, "review budget". New verbs allowed: refer, referral, vouch for, back.
- Prose, no sub-headers inside a page, each fact once, no incentive hype, no telegraphed math beyond the pay rule
  already there, no counts ("several reviews", "your final review"), no dollar maximum for the reviewer's own pay.
- Curly apostrophes and quotes, no em dashes (use commas, periods, colons), sentence case titles.
- Stage 2 Page 2 (candidates), the 0/50/100% bullets, the Stage 3 pay rule paragraph, the manipulation-check item,
  the Demographics rows: byte-identical.
- Jose's 2026-08-25 hand edits win wherever they touch the same sentence.
- The Stage 3 candidate cards stay ID-only (no gender cue); the representative avatar is the only gender cue.

## 6. Outputs wanted from Sol

- out/Stage-2.md: full file, same "# PAGE n:" lines and order as in/current_Stage-2.md, with Page 1, Page 3 and Page 4
  rewritten per sections 2-3 (Page 4 starting from the LIVE paragraph in in/live_cells_2026-08-26.md, not the stale
  one), Page 2 byte-identical; plus, after Page 4, a "# CQ NOTE" section saying which of the four Stage 2 CQ items (in
  the live cell STAGE 2|8|0) still hold and proposing a replacement item if one is needed.
- out/Stage-3.md: full file, same structure as in/current_Stage-3.md plus a new page between "# PAGE 6: LATER REVIEWS"
  and the old "# PAGE 7": "# PAGE 6B: CHOOSE YOUR FINAL REPRESENTATIVE" (mechanism M2, with the price table as a short
  list the doc can render as bullets, and the organization choice); "# PAGE 6C: FINAL REVIEW" (two sentences: what the
  reviewer sees, same rule, its own $0.50 and result); the old Page 7 replaced by a one-line note that the two 0-10
  items are retired in this draft (keep their text in a "# FALLBACK" section at the end so nothing is lost); Page 3
  CQ with the swapped item and the key line; Page 8 as in the live cell (manipulation item only) followed by the
  Demographics label.
- out/ui_strings.md: S1 Stage 2 slider title (referral framing); S2 Stage 3 review-screen placement title if the
  referral verb changes it ("... How much of your $0.50 do you place behind their referral?"); S3 the choice-page
  slider caption and the live price line ("Chance this representative: 70%. Price: $0.04 of your $0.25."); S4 the
  final-review header line ("Final review: a different representative, drawn at random" / "Final review: the same
  representative"); S5 the two-organization comparison label on Stage 2 cards ("Atlas candidate" instead of
  "Comparison candidate" / Beacon).
- out/notes.md (under 350 words): what changed and why, every sentence you were unsure is literally true, the
  "referrer" variant list (section 3), word counts for Stage 2 Page 1 and Page 3 and Stage 3 Pages 1, 2 and 6B, and
  the CQ keys.

## 7. Architect's decisions after the review panel (2026-08-26). THIS SECTION WINS over sections 2-6 and over in/decision_memo.md wherever they differ. Sol: write to this spec.

The panel (5 lenses, 25 non-minor findings, 16 surviving adversarial refutation, memo in in/decision_memo.md) changed
the design in five places. Everything not listed here stands as written above.

7.1 The chosen chance sets ONLY the reviewer's own final review. It is never a source of the representative's bonus
    (unanimous blocker: if the representative were paid on the chance, a reviewer's wish to reward a representative
    they like would be inseparable from their belief in that representative's calls, and a gender-linked wish lands
    exactly on the hypothesis). Participant-facing consequence, Stage 3 choice page: one plain sentence that this
    choice affects only which representative the reviewer's final review comes from. The representative's bonus keeps
    coming from (a) the reviewer's placements (win-gated, as now) and (b) ONE stated item, kept from the current Page
    7: "If you could review more decisions, how many more of this representative's decisions would you want to
    review?" (0 = none, 10 = as many as possible), now at $0.10 per point (max $1.00; Jose's live "up to $2.00" stays
    true), on its own page immediately AFTER the choice page and the final review's result, with the current label
    ("This answer is your evaluation of the representative. It can add to the representative's bonus and does not
    affect your own payment."). The organization 0-10 item is retired in this draft (kept under # FALLBACK).

7.2 Price schedule and amount. The reviewer receives $0.15 for the choice and keeps whatever the choice does not
    cost. Slider 0-100 in 10-point steps, 50% is free. Price by position, defined as this table (not a formula), the
    same on both sides of 50: 60/40: $0.01; 70/30: $0.03; 80/20: $0.06; 90/10: $0.10; 100/0: $0.15. (Architect's
    override of the memo's 0/1/2/5/10/15: each step costs one cent more than the one before, which is strictly convex,
    explains itself in one sentence, and maps a risk-neutral reviewer's D onto the slider in even $0.10 steps: 60% if
    this representative is worth more than $0.10 more per review than a random one, 70% above $0.20, 80% above
    $0.30; symmetric below 50.) Do not use the word "budget"; say "$0.15 for this choice" / "the $0.15". The screen
    shows the price live under the slider ("Chance this representative: 70%. Cost: $0.03 of the $0.15. You keep
    $0.12.") the way the review screen shows the two outcomes. Expect heaping at 50 and on round numbers; the analysis
    plan (internal) pre-registers a two-part model beside the linear one. No sentence to participants about where
    the mass will sit.

7.3 Telegraph before the same-representative reviews: LIGHT. Stage 3 Page 2 keeps its pay rule, keeps "You keep what
    you earn on every review ... on top of your [$X.XX] participation payment", and its last paragraph becomes, in
    substance: at the end you will make one choice about your final review, explained when you reach it, and answer
    one question about this representative; your answers and your decisions may also add to the representative's
    bonus; your own earnings always come from your reviews and from that final choice. All mechanics live on the
    choice page (Page 6B). Reason: a reviewer who knows from the start that they can pay to keep or drop this
    representative may place differently on the rounds that carry the primary DV. Jose may override toward a fuller
    telegraph; Sol writes the light version and puts a two-sentence fuller variant in notes.md.

7.4 Truthful wording of what reviewers can do, for Stage 2 (representatives). Never "reviewers can pay to get more of
    your referrals" (overclaims: it is one more review, at a chance). Say: "at the end, a reviewer chooses how likely it
    is that one more review comes from you rather than from another representative, and can spend money to shift that
    chance." And the accuracy sentence for Stage 2 Page 3, which must stay true at a 0% placement: "Being right pays
    you directly, in proportion to how much you placed, and makes reviewers more willing to follow your next referral
    and to choose you again." Never plural "more referrals" for what a reviewer gets.

7.5 Organization spillover as a free real choice on the choice page, worded so it is meaningful at every slider
    position (it only matters if the draw goes to a different representative): "If your final review comes from a
    different representative, which organization should they represent?" Options in this order: [Atlas/Vertex] (the
    representative's organization, piped first), [Vertex/Atlas], Either. Flagged for Jose as a resolution downgrade
    versus the paid 0-10 organization item (lab open item 3); Sol writes it and keeps the old item under # FALLBACK.

7.6 Piping rule. Own organization is the stage's existing bracket ([Vertex/Atlas] in Stage 2, [Atlas/Vertex] in
    Stage 3); the other organization is the same two names in the opposite order. Stage 2: "Each review compares one
    [Vertex/Atlas] candidate with one [Atlas/Vertex] candidate." Stage 3: "the [Vertex/Atlas] candidate" for the other
    side. Never the same order in both slots of one sentence.

7.7 Stage 3 CQ item for the choice page (replaces item 5 of the current five; item 5's content, "what I earn on every
    review, added together", folds into the new item's correct option or is dropped, Sol's call; keep five items):
    stem "You set the slider to 70%. What happens?"; correct option: there is a 70% chance your final review comes
    from this representative, $0.03 of the $0.15 is spent and you keep $0.12; two distractors (for example: you pay
    $0.15 and get this representative for sure; nothing changes until you move the slider to 100%). Key line in the
    same format as the current file. Note: the CQ comes BEFORE the reviews, so under the light telegraph (7.3) this
    item would reveal the mechanism early. Sol's call, stated in notes.md: either (a) keep item 5 as it is and put the
    choice-page item as a single check ON the choice page itself (preferred), or (b) put it in the pre-review CQ.

7.8 Reference draft for Stage 2 Page 1 (from the panel; Sol may use it whole, improve it, or replace it, but the
    order of facts and every fact must survive):
    "Welcome to [Vertex/Atlas]. This study is set up like a staffing agency with two organizations, Vertex and Atlas,
    and you have joined [Vertex/Atlas] as a representative. Your decisions will be seen: in a separate study,
    independent reviewers will see some of your referrals. For each one, a reviewer decides how much of their own
    money to place behind the candidate you backed, and at the end chooses how likely it is that one more review comes
    from you rather than another representative, and can spend money to shift that chance. Your decisions shape the
    view they form of you and of [Vertex/Atlas]. / Each review compares one [Vertex/Atlas] candidate with one
    [Atlas/Vertex] candidate on logical reasoning. You always refer the [Vertex/Atlas] candidate; the only decision is
    how much of $0.50 to place behind them, so place the amount that best reflects your judgment. / Your bonus depends
    on one of your reviewed decisions, picked at random, so any decision could count."

7.9 Stage 3 flow in this draft (count-free): consent; Page 1 Your role; Page 2 Making your reviews; Page 3 CQ (five
    items); review screens and results with the same representative (mockups, unchanged text); Page 6 Later reviews
    (its end-of-reviews text now reads as the end of the reviews WITH THIS REPRESENTATIVE, before the choice; Sol
    rewrites the two lines so they do not say "all of your reviews"); Page 6B Choose your final representative (the
    slider, the price table as bullets, the $0.15, the one-draw sentence, "affects only your own final review", the
    organization choice); Page 6C Final review (what they will see, same rule, its own $0.50, result shown, then
    "You have now completed all of your reviews. Your total earnings from the reviews are: $[X.XX]" moved here);
    Page 7 One question about the representative (the kept 0-10 item, its label); Page 8 Final questions
    (manipulation item only, as live); Demographics label. # FALLBACK at the end: the retired organization item and
    the old two-item intro, verbatim.

7.10 Stage 2 flow: Page 1 (7.8), Page 2 byte-identical, Page 3 (section 3 + 7.4 sentence; bullets byte-identical),
    Page 4 from the LIVE paragraph with the reviewer clause reworded per 7.4 ("how much of their own money they were
    willing to place behind the candidate you referred, and how much more of your work they said they would want to
    review"; keep "Together, these decisions determine up to $2.00 of your bonus."), then # CQ NOTE.

7.11 Internal build notes (NOT for Sol's text; recorded for the lab in INTERNAL notes): one draw per reviewer written
    to embedded data on first execution and reused on reload (check-before-roll, as stage3_qid3_combined.js does for
    the condition); the price the screen shows and the price paid come from one function; the alternate
    representative sampler must honor the organization choice (acceptance test: N draws per option, 100% match) and
    must have an unused decision available for the drawn representative; the representative's "one of your reviews,
    picked at random" draws only among decisions whose reviewer finished the session; IRB and the Prolific listing must
    cover one extra paid review (about one minute, up to $0.50 more) and the $0.15; the Stage 2 mockups need a
    re-render with Atlas as the comparison organization before the draft is shown whole; Stage 3 avatar gender is
    yoked to the real Stage 2 respondent's gender (CONDITION_POOLS carry eg), so changes A and B, which add scrutiny
    and confidence-signal framing, could move real placements differently by the representative's own gender; check
    raw placement by self-reported gender in the new Stage 2 data before the next roster build.
