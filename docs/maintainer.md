# Making changes with an agent

Describe the player-visible change and the part of the game it affects. The
agent reads `AGENTS.md`, inspects the current game/specification, makes a branch,
implements the change and runs the relevant checks.

For example: “Change the fisher's dialogue after winning the battle. Keep
existing saves working. Build a local version for me to try.”

The agent handles setup, embedding scripts, runtime restoration and testing.
Ask it to run `uv run play` to try the working copy, or `uv run build` for a
local app to open later. Development progress is separate from normal saves.

For direct RPG Maker XP work on Windows, use `uv run editor`. Tell the agent
which maps you changed before asking it to regenerate map data: some maps are
generated, so their source must be updated to preserve editor changes.

Review the game behavior and pull request. Request `/verify` before merging
substantial work. Release publication is a separate step after verification;
the result should be one release link with three platform ZIPs.

Accepted story decisions belong in [the specification](../specs/game-design.md).
Working instructions belong in `docs/`. You do not need to maintain a second
project copy or assemble executable files by hand.
