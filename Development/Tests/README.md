# Headless checks

These exercise code and project data. They do not create a game window or prove
that the Windows rendering, controls and full battle UI work.

From this folder, with Node.js and Python available:

```
npm ci
python prepare_reference.py
node run.cjs
node native_domain.cjs
```

Python preparation requires `rubymarshal==1.2.10`. The Node dependencies pin an
official Ruby 3.2 WASM runtime. The supplied Windows game uses Ruby 3.1; our custom
scripts use syntax available in both. No Node dependencies are needed to play.

`run.cjs`: 30 tests for the domain model and battle adapter. Battle outcomes and
other engine services use test doubles. Covers death, one encounter, capture,
loss, party capacity, return, item/identity preservation, save state, memorial
teams and planned ending state.

`native_domain.cjs`: loads actual Essentials Pokemon, player, bag and SaveData.
Checks all three choices, the 99/100-step gate, optional/skipped pier routes,
returning without Pookie, identity and supplies, real Key Item save/load,
locked-store progression and old-save/astral migration. Graphics, movement and
scene services are fixtures in this harness.

`rendered_smoke.rb` and `rendered_resume.rb`: TEST-ONLY injections for a disposable
native-engine copy. Never embed them in a release. The first exercises the new
prologue and actual walking; the second loads complete engine saves to check
both walk branches, pier/key continuation and a real 0.3 save. TB_RESUME selects
walking, pier_quest, pier, keys or legacy; provide the corresponding test saves.
See ../validation_report.md for the exact completed scope and limitations.

RenderedEvidence_0_4 contains actual engine screenshots. The 0.3 evidence is
retained separately as historical coverage, including the real battle/astral loop.


Coast 0.5: rendered_coast.rb and rendered_coast_resume.rb are TEST-ONLY drivers
for a disposable native engine copy. Use the new drivers for the expanded coast;
rendered_smoke.rb and rendered_resume.rb retain historical 0.4 coordinates.
The coast driver produces full saves and explicit legacy-coordinate fixtures.
TB_COAST_RESUME selects legacy-coast, legacy-water, coast-pier or coast-current.
Load legacy-coast first to create coast-current, then test that current save
before another case overwrites the disposable output. See the current report
for exactly which movements and branches were exercised.

0.5.1: rendered_night.rb loads the retained 0.3 chosen-party save in a disposable
engine copy, inspects night across clock hours and current maps, and captures
an actual battle using its night background. It exits during presentation;
it does not claim battle completion. Never embed this driver in releases.

0.6: neighbor_flow.rb runs after opening_flow.rb in native_domain.cjs. It checks
all starter choices, additive old-oil continuation, each item handoff/save,
loss/draw/retry, defeated-trainer flags and bag-capacity rollback. Graphics and
battle outcomes are fixtures; native save/Pokemon/bag objects are real.

rendered_neighbor.rb is TEST ONLY. prepare_native_neighbor.py accepts a matching
Linux mkxp-z directory (including the retained chosen-party.rxdata test save)
and a disposable output directory outside the game project. Its injected input
completes messages, a wild encounter and three actual trainer battles. HP resets
between battles isolate staging from balance; a final 1-HP/Splash fixture forces
a real trainer defeat and verifies the pre-heal astral snapshot.
TB_NEIGHBOR_RESUME=plate or pursuit loads a full save made by the driver to check
state and actor restoration. Never inject this driver into release Scripts.
