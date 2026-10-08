# Codex-operated game knowledge graph

One local graph holds the world, gameplay design, relationships and asset direction.
Codex reads and writes it through [KG](../tools/kg/README.md). The standalone
SurrealDB server and local Surrealist browser need no Docker, remote account or
inference service. Codex supplies the reasoning; the native game implements play.

The storage model stays small: entities, relationships and optional JSON content.
Deep design comes from how its subjects affect each other. Adding more forms,
metadata or entity types does not create that depth.

## Representation and ownership

| Structure | Responsibility |
| --- | --- |
| Entity: `id`, `kind`, `name`, `description` | An independently meaningful subject and a readable account of it. A kind is a label, not an inheritance hierarchy. |
| Optional `data` | Content that benefits from a distinct value: design prose, dialogue, ordered beats, author questions, dimensions or types. No required per-kind template. |
| Relationship: `kind`, `to`, optional `description` | A meaningful connection between subjects. A description can explain its timing, reason or condition. |
| Source entity and `sourced_from` relationship | Where an imported claim or quotation can be checked; useful source sections can qualify the link. |

Dialogue entries use `context` and `text`, with speakers and line breaks inside
the text. Imported exchanges cite source entities through links. Relationship
prose lives directly in `description`, without a `data` wrapper.

Git serializes outgoing relationships in each entity’s `links` list. The database
stores them as native relations with endpoints. These are representations of the
same graph, not two independently maintained systems. IDs survive names and source
file moves. Python validates identity, endpoints and portable JSON, not literary
quality, completeness, canon or gameplay reachability.

Use [the authoring guide](../knowledge/authoring.md) for content conventions.
A shared history or conflict can need its own entity. A repeated fact, an empty
asset brief or a question about one person usually belongs on its subject.
Species, individual companions, impersonators, locations and events have different
identities even when their names or descriptions overlap.

Facts have an owner; scenes explain how they become experience. For example, the
necklace owns its history, the return scene owns the exchange, and the relationship
to the vault explains when it is kept there. Retrieval should bring those records
together without requiring three independently maintained accounts of the event.

## Review of the current design

| Finding | Refinement |
| --- | --- |
| Most links led to sources while important story participants were disconnected. | Connect scenes, objects, people, places and conditional outcomes. A citation cannot substitute for a world relationship. |
| Small lore nodes repeated Mother’s role, an evolution rule, a minigame boundary or a line of item history. | Keep these facts with their subjects; reserve independent lore records for truths or beliefs that connect several subjects. |
| Visual dictionaries and relationship qualifiers accumulated slightly different labels. | Use one `design` description across subjects and one relationship `description` for prose qualifiers. Write source-section notes in the link description; keep useful structured values such as creature dimensions. |
| Sequence fields proliferated and a chapter’s order implied a rigid route. | Reuse ordered beats, with optional actions and branches explained in their text. Scene membership links do not mean mandatory progression. |
| Removing metadata did not itself describe meaningful choices. | A branching beat uses a description and options; each option states an action and consequence. Suicune’s kill/capture encounter is the worked example. |
| Mandatory citations encouraged treating every drafted idea as sourced canon. | Check citations when supplied. Ground imported facts and quotations; label invention honestly without manufacturing evidence. |

No new runtime schema or workflow engine is needed for these refinements. In
particular, a branching beat and an author question can both use small option
objects without becoming executable expressions or tasks with approval states.

## Whole-world review

The review covered creatures, characters and scenes, settlements and history,
then reconciled their shared places and consequences. The graph now includes
concrete proposals for several previously disconnected parts of the game:

- Natu disturb feeding Wurmple; Psyduck loosen soil around sheltered Sunkern;
  Weedle choose different leaves. Aipom, Weedle and Zigzagoon now have records
  grounded in their existing encounters. Household companions retain familiar
  habits after evolution, while their changed bodies affect daily life.
- Koga’s friendship develops through shared work and familiar companions. An
  early refuge visit supplies a crossing, sounds and animal behavior to recognize
  after poisoning. The false return includes actual comfort before coercion;
  later testimony distinguishes participation, belief and responsibility.
- Oil links ship, shop and lighthouse. Theft interrupts particular work, giving
  Team Abyss’s fencing and pressure consequences beyond another boss battle.
  Proposed river and mountain exchanges connect livelihoods to the search.
- The museum and a submerged coast offer ordinary evidence before supernatural
  explanations. The island has a proposed arrival, shrines a first-visit situation,
  and the cemetery a place to pause without a death quota or resurrection promise.
  Sound direction comes from work and creature activity as well as their absence.

These passages are proposed where invented. Native encounters, quoted pond
conversations and established rules remain sourced. Blanket citations to late
amendments were replaced with relevant passages. Lapras’s scene sequence stays
on its arc, and its pier is correctly placed in Shiohama rather than the docks.
No new mandatory fields or runtime schema were needed.

The subsequent source pass through version 0.8.12 adds the harbour’s actual
residents, three errands, personal objects and ring, together with the Hollow
Wood, Skull Hollow and their encountered Ghost species. Existing conversations
provide the histories; generated challenger names remain separate from fixed
residents. The pond’s cache trail, one-time pier glimpse and cave loss recovery
are grounded in current source. The traveller’s old missing-bridge line remains
a recorded continuity question beside the now-open route, not invented geography.

## Decisions that still shape the game

The graph has more usable situations, but several missing designs cannot be
settled by adding detail around them:

- **Ancient wrong and present breach:** choose what was taken, whose life it
  disrupted and what the criminals disturb now. Then write a corroborated evidence
  sequence; ruins and persuasive speeches alone cannot establish the history.
- **Recovery and the ending:** design Suicune’s cure and the precise sabre
  interaction, including captured-but-unhealed and subsequently lost cases.
  Proposed aftermaths show the desired difference without inventing final rules.
- **Koga’s local cast:** choose his familiar team and develop recurring witnesses
  before the conjuration testimony. The guardian needs an identity and a means
  of communication. Real Koga’s fate remains deliberately unanswered.
- **Journey and traversal:** the island still needs a full local conflict and a
  return route. Shrines need particular masters, trials and a viable Dive route,
  including after companion loss. The shared astral scene needs an entry that
  does not require sacrificing a companion.
- **Creature progression:** test the long Frostcoon-to-Nivalora commitment against
  actual chapter pacing. Additional household evolution stages, Lapras’s regional
  move identity and Sunkern’s inherited sun abilities need intentional choices.
  Distinct motion and final cries need asset work beyond visual descriptions.
- **Life under permanent night:** establish food and fuel sources as their places
  become relevant. A few observed dependencies will be more useful than an
  invented economy explaining every meal.

Mother’s ritual purpose and reveal still require deliberate design. The sea’s
remaining mystery is a constraint to preserve, not a hole to fill.

Further coverage should be driven by playable situations:

| Question | Where it belongs |
| --- | --- |
| How is a creature noticed, approached, avoided or recruited? | Its behavior in prose and acquisition relationships; a scene when choices and consequences warrant one. |
| How does raising it change play, and what does evolution preserve? | Species/individual descriptions, evolution links and selected moves with their relevant limitations. |
| What do people and creatures need from the place and one another? | Existing descriptions and relationships: food, shelter, work, trade, competition or care. |
| What can the player learn before making a lasting choice? | Observable scene beats, dialogue and understandable warning signs; author questions for unsettled presentation. |
| What persists on returning, after failure, or with a different companion? | Consequences and a few meaningful variations of the scene, not a combinatorial route catalog. |
| What makes the subject recognizable in play? | Design prose, movement and sound direction, readable scale and distinct interaction cues; references to actual assets when available. |

The first creature extension adds only one content convention: optional `moves`
entries with `name` and `description`. Availability, effect and design relevance
fit in that description. Keep shared mechanics in an independent record only when
several subjects need to reference and develop the same rule. Do not add a move
node for every stock attack or an empty diet/breeding/temperament form to each species.

These are missing designs, not missing mandatory fields. A new property earns its
place when it helps a concrete use, such as comparing dimensions, preserving a
conversation’s order or keeping alternatives distinct. Otherwise use prose.
Quiet details can create familiarity, humor or atmosphere without a plot payoff.

## Time, knowledge and uncertainty

The graph describes a whole design, not a player save. Relationships can describe
ownership before and after events. Scenes carry actions, choices and consequences.
When many participants and consequences make an event independently important,
represent it as a scene; otherwise a sentence can describe the change.

Distinguish world truth, a character’s belief, the player’s observation and an
unresolved author decision in the relevant passages. All queries are author views
and can contain spoilers. Codex must respect reveal timing when producing dialogue,
images and music. The tool neither hides spoilers automatically nor simulates play.
Real Koga’s fate remains a deliberate mystery; an unwritten reveal is not the same
thing as a question intended never to be answered.

## Working with the graph

Codex reads source material and related records, develops a connected situation,
writes it, inspects the neighborhood and exports it. Text ingestion is that same
workflow, not another extraction service. Full-text search indexes names,
descriptions and nested data; graph traversal supplies connections. No duplicated
search field, embedding provider or separate memory store is involved.

The live database is the working copy. Git holds a manifest and a small JSON file
per entity. Export before replacement imports or branch switches, reconcile file
conflicts, validate and import explicitly. Separate checkouts use separate local
servers. Same-entity conflicts still need deliberate reconciliation.

Media stays with existing asset owners, referenced when an actual artifact exists.
Codex uses the tools available in the session for generation and native integration;
KG is not a media pipeline. Source refactors need graph edits only when meaning or
useful evidence changes. Native tests and playtests establish implementation;
KG tests establish persistence, transactions, search, references and roundtrips.
See [Tidebound integration](tidebound-kg-integration.md) for the project boundary.
