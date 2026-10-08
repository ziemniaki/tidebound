# Writing Tidebound’s world

Write a world another agent can understand, develop and implement. The bible is
creative authority; native source establishes what is playable. Read the relevant
passages and later amendments before changing their meaning. New lore can be
written here without implementing it in the game.

## A small vocabulary

Records use `id`, `kind`, `name`, `description`, `links`, and optional `data`.
Kinds are useful labels, not classes with required forms. Use prose until a list,
number or small object makes something easier to understand or use.

| Content | Useful shape |
| --- | --- |
| Identity, life, motives, ecology, history and rules | Connected paragraphs in `description`. |
| Appearance and asset direction | One `data.design` string, for any subject. Describe actual form, materials, color, movement and relevant constraints together. |
| A scene or a longer arc | Ordered `data.beats`. A beat is normally a sentence; a branching beat can have a `description` and `options`, each with a `description` of the action and consequence. |
| What persists after a scene | Plain `data.consequences` when this needs explanation beyond the beats. |
| Dialogue | Exchanges with only `context` and `text`. Write speaker names and line breaks inside the text; cite existing dialogue through `sourced_from` links. |
| An unresolved author decision | `data.questions`, each with `question` and optional `options` containing `description`. |
| Useful exact properties | Ordinary values such as species `types`, `height_m` and `weight_kg`. Add them because they matter, not because another record has them. |
| Defining moves | Optional `data.moves`: a selection of `{name, description}` objects explaining availability, effect and why the move matters to this creature. |

These are conventions for content that benefits from them, not mandatory fields
or new database types. A species may need dimensions; a remembered person may
need only a paragraph. Omit empty data. Keep a coherent passage together instead
of dividing it into `motivation`, `contradiction`, `role`, `voice` and other labels
that an LLM can already understand from the prose. Lists of useful observed habits
are fine; do not duplicate them as a second biography.

No scope/status/development badges, audience lists, confidence scores, search
copies or source hashes. Describe playable extent once on the chapter, and explain
an individual prototype only when its limits affect interpretation. The native
game owns balance tables, save flags and execution; copy only rules needed to
understand design. Do not create a second rules engine.

## Identities and connections

Give something its own record when it needs independent identity or connects
several parts of the world. Keep a species distinct from an individual, an
impersonator distinct from the missing person, and a place distinct from events
there. A fact that merely restates its subject belongs on that subject. A shared
truth such as the demons’ grievance can warrant a record connected to its
participants, evidence and consequences. A secret does not automatically need one.

Relationships make context retrievable. Connect a scene to its important people,
objects and places. Connect ownership, family, dependence, conflict, evolution and
actual outcomes where established. Do not link every noun mentioned in a paragraph.
Use the existing relation name when it means the same thing; a new verb needs a
real distinction, not different phrasing. Read incoming as well as outgoing links;
do not store reverse duplicates just to make both records look populated.

A link needs only `kind` and `to`. If its meaning depends on time, a belief or a
condition, put that in one `description` string directly on the link. For example,
the necklace is `kept_at` the vault **after recovery and the vault visit**. A hopeful ending
`requires` this Suicune **saved and healed**, not merely a creature with his name.
Do not use a prerequisite link to mean that a person appears in a scene.

The graph describes the whole story, not the current state of a playthrough.
Keep changes in their scenes and explain conditional relationships in words.
Repeated changes between the same subjects can be described on the relationship;
if an event has its own participants and consequences, give that event a scene.
An ordered outline is not automatically a mandatory route: identify optional
visits, refusal, retry and alternative routes where they actually exist.

Facts have an owner. Scenes show when and how a player encounters them; other
records can summarize enough for orientation without copying the whole account.
A source link identifies evidence to inspect. Keep source paths on source records,
with useful sections in `sourced_from` link descriptions, rather than code
manifests on people.
Existing source citations do not certify newly invented passages. Ground imported
facts and quoted dialogue in evidence. A new proposal need not manufacture a source
record; identify it as a proposal and cite existing constraints only as context.

## Choices and unknowns

Player choices and author decisions are different. A player choice belongs in a
scene or arc and states what the action changes. For example, Suicune’s existing
planned encounter can use this beat:

```json
{
  "description": "Confront corrupted Suicune at the poisoned refuge.",
  "options": [
    {"description": "Kill him. The journey remains finishable, but the intended healed-Suicune and sabre resolution is lost."},
    {"description": "Capture him. Healing remains a responsibility; capture alone does not cure the forest or secure the hopeful ending."}
  ]
}
```

How that irreversible choice is presented remains an author question. Keep it
in `questions`; its options are unchosen designs. Lapras’s unsettling truth also
has two existing bible proposals: an involuntary link by which the sea recognizes
the protagonist, or carrying traces of the drowned. Neither is established fact.

Omit alternatives when none are useful. Do not invent options to meet a count.
No question IDs, resolution flags, scores or decision lifecycle. After a decision,
incorporate its answer and remove the answered question; Git retains the history.
Keep questions that would change the next work, not a checklist of every unwritten
name, date and costume detail. Several independent decisions can remain separate
small objects on the subject.

Label proposed or inferred material in the passage itself. Attribute a belief to
who holds it and the evidence available to them. A whole village need not share
one mind. Preserve deliberate mysteries: Koga’s fate is not an author question
waiting for a helpful agent to solve. An unwritten reveal, such as the imitation’s
origin, is different: it eventually needs evidence and a scene.

## Depth through interaction

Develop a connected situation, not isolated biographies. Start with what already
exists: somebody needs something, another person or creature can affect it, and
acting changes their relationship or surroundings. Ask what each can offer, what
they depend on, and where reasonable interests conflict. These are writing prompts,
not property names. Let attachment and familiarity exist before damaging them.

The opening’s plate is useful because borrowing it creates a reason to return;
the return exposes the theft; recovery permits the seller’s private recollection;
his trust leads to the vault. Ordinary actions produce the story. The pearl’s
later meaning can deepen that experience without making the meal a disguised trap.

For creatures, connect anatomy, movement and behavior to a habitat and a way of
living. Consider food, shelter, other creatures and human use where relevant.
Then distinguish the individual through experience: Maku’s careful second pat
follows his clumsy handling of bottles. It is not a temperament assigned to every
Makuhita. A dangerous animal need not be possessed, and a kind one need not betray.
Do not invent biology to explain every supernatural mystery.

When developing a creature, consider how a player encounters it, recognizes its
behavior, approaches or avoids it, and lives with it after recruitment. Diet,
shelter, social behavior, warning signs, ordinary variation, care and relationships
with other species can supply useful detail. Develop the relevant ones together
in prose; these are not fields to fill for every species. Describe something a
scene can show. Regional Wurmple’s proposed clipped leaf edges and anchored silk
are encounter clues; Frostcoon’s proposed reaction to a shaken branch can support
care without inventing a hidden affection meter.

Evolution needs both the established condition on an `evolves_into` link and an
account of what changes: movement, size, behavior, battle role and what remains
recognizable about the individual. Include known intermediate stages. Do not
invent a target node for an unnamed future stage; put that decision on the last
known stage. A level threshold does not establish a biological explanation or a
new ritual. Explain important inherited-move changes, such as Frostcoon replacing
attacks with support moves, where they affect the raising experience.

Keep `moves` selective, not a second complete learnset. For example:
`{"name": "Wish", "description": "Level 10. Delayed healing can reach a teammate switched into Frostcoon’s position."}`
Check availability and effects against the pinned native version and authored
overrides, not recollection of another Pokémon game. Explain useful ability
interactions and limitations in prose. Distinguish a move present in a species
list from one actually learned by an individual. Maku’s starting Foresight and
Wick’s early Night Shade are authored individual choices; evolution need not
erase them. The game still owns exact balance and complete compatibility tables.

A battle move is not automatically a field action or lore power. Healing need
not cure poison or resurrect; Teleport need not unlock travel; a weather ability
does not create a day/night cycle. Equally, a native Habitat label, inherited cry
or stock Pokédex story need not be intentional regional design. Record meaningful
mismatches as questions, without silently changing the game to fit the prose.
Acquisition links describe actual or explicitly planned encounters, separately
from proposed ecological ranges. An evolved creature need not have a wild spawn.

Places need ordinary uses, resources, paths and recognizable sounds. History
should leave evidence people use, misunderstand, preserve or dispute. Institutions
need practices and people with different interests before more ranks and titles.
A familiar route, household object or changed conversation can carry consequences
more effectively than another ancient order or lore monologue.

Let settlements depend on one another through specific goods, skills and routes.
Follow a useful object from maker to carrier to user before inventing a new
currency or trade faction. A stolen crate matters when somebody cannot finish
their work without it. Give people different knowledge and responsibility: the
person who organized a harmful act, someone who complied, a dissenter and a
neighbor who believed a rumour need not tell the same story.

Establish a place before damaging it. Reuse a crossing, resting spot, familiar
sound or creature habit so the change can be noticed without an explanatory
speech. Afterwards, show both what people can repair and what remains lost.
Evidence should establish only what it actually supports; discovering how an
imitation was made does not answer where the missing person went.

A choice needs understandable stakes at the moment it is made. Decide what the
player can observe then, what remains uncertain, what they can decline, and what
changes later. Check how the journey continues after failure or loss. Do not add
branches that exist only to imply depth, or silently choose permanent outcomes
through ordinary actions. Exact unknown rules stay questions, not invented flags.

Quiet details also matter: recognition, pleasure, humor, atmosphere and rest do
not all need a quest payoff. Not every kindness is suspicious; not every object
is a clue; not every scene needs a twist. Avoid explaining a world so completely
that there is no room left to inhabit it.

## Dialogue, design and revelation

A speaker wants something from a listener. Let an exchange request, evade, correct,
refuse or change a relationship. Voice comes from attention, vocabulary and rhythm.
Read it aloud and remove lines that recite the dossier. State in `context` whether
lines are existing dialogue or a proposed draft; verify quotations and reachable
branches against source. Keep shared exchanges on their scenes, with short voice
samples on characters only when useful. Each exchange has just `context` and
`text`; use speaker labels and line breaks inside the text, including narration
where needed. Cite imported dialogue on a `sourced_from` link, whose description
identifies the exchange when an entity has several sources. Preserve the exact
words and order when converting existing dialogue.

```json
{
  "context": "Existing dialogue. During Mother’s hall conversation.",
  "text": "Mother: Oh, Maku! Gently, sweetheart. Those are bottles, not turnips.\nNarration: Maku pats the box twice, very carefully."
}
```

A relationship qualifier is equally direct:

```json
{
  "kind": "kept_at",
  "to": "vault",
  "description": "After recovery and the vault visit."
}
```

Design prose should let an artist draw the subject. Whyduck’s uneven skull edge,
dark cleft and folded pink hemispheres help; “ancient, haunting, mysterious” does
not. Put proposed appearance choices in words rather than silently making them
canon. Inspect existing art before claiming continuity. Individuals can refer
to their species design and describe only differences or staging. Separate an
asset record only when an actual deliverable or variant needs its own references.

Locations can also describe what is heard: a repair rhythm, loose rigging, water
under a crossing or the absence of familiar calls. Give later music and sound
work a place and an activity to respond to. Do not assign every location a new
theme track, instrumentation template or supernatural signal by default.

This is an author graph containing spoilers. Separate what happened, what a
character believes, what the player observes and when the explanation becomes
available. Write those distinctions where they matter, without universal knowledge
or disclosure fields. The seller can explain a glint ordinarily while the author
knows a deeper ecology. Early images and music must also respect that timing.

## How an agent should work

Read a small connected cluster, its sources and relevant later amendments. Find
existing people, objects or places that can carry the requested idea before adding
new ones. For new lore requests, write concrete proposed material, not just more
questions. Established constraints still apply; prior user decisions need no new
approval ceremony. Ask only when a consequential choice cannot usefully proceed
within that direction.

Read the result as player, writer and artist: what can be done or pictured, what
changes, which relationships explain it, and where does knowledge come from?
Check nearby continuity and alternatives, including loss and optional paths.
Remove duplicate facts, administrative fields and connective prose that says
nothing specific. Do not mistake more nodes, words or unanswered mysteries for
more depth. Write the live graph, inspect the affected neighborhood, export and
validate. Report which gaps remain; structural checks cannot certify literary
quality or prove gameplay.
