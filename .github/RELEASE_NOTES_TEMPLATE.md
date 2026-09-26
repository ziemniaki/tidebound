# Writing player-facing release notes

Use this guide when updating the root `RELEASE_NOTES.md`. The release builder
copies that reviewed file into the candidate; GitHub displays it as the release
body. This template is contributor guidance, not an automatically interpreted
GitHub feature. Do not publish the instructions or unused template sections.

## Editorial instructions for people and assistants

- Write for someone deciding whether to download the game. Lead with the most
  useful change in one short sentence, then make the rest easy to scan.
- Compare with the previous public release. For a refreshed draft, also tell
  earlier testers whether they should download it again.
- Use one flat changelog list, with no New/Improved/Fixed subheadings or other
  change categories. Prefer 3–7 concrete bullets; keep each short. Put essential
  launch guidance in a brief paragraph underneath, without another heading.
- Describe visible behavior: “Fixed the Mac unzip error” or “Added a southern
  pond to explore.” Explain what changed for the player, not how it was coded.
- Include save compatibility, real platform limitations, required actions and
  known player-facing problems when they matter. Do not claim a full playtest
  based on smoke checks or hide a known launch restriction.
- Keep unreleased story details and spoilers out of the notes.
- Do not list CI jobs, refactors, commit IDs, PR numbers, checksums, manifest
  files, dependency versions, test counts or agent activity. Those belong in
  contributor docs and CI artifacts, unless a specific detail changes what the
  player must do.
- No “various improvements,” “under the hood,” “exciting,” “seamless,” or filler.
  Do not invent benefits or pad a small release into a marketing announcement.
- Attach only one player ZIP per supported OS. Keep provenance/checksums and the
  editable project ZIP in CI artifacts; notes belong in the release body.

## Starting layout

```markdown
# Tidebound <version>

One sentence about the main change for players.

- **Concrete feature:** what players can now do.
- **Recognizable problem:** what works correctly now.
- **Compatibility:** mention only if players need to know.

Choose your platform ZIP below, unzip it, and follow READ_ME_FIRST.txt.
Add only essential launch actions or limitations here.
```
