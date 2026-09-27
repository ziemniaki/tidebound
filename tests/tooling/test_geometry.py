"""Playable routes through the generated maps, including movement rules flood-fill misses."""

from collections import deque
import json
from pathlib import Path
import unittest
from rubymarshal.reader import loads

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "tools/generated"
DIRECTIONS = {2: (0, 1), 4: (-1, 0), 6: (1, 0), 8: (0, -1)}


def neighbors(position):
    x, y = position
    return [(x + dx, y + dy) for dx, dy in DIRECTIONS.values()]


def reachable(start, edges):
    seen = set(start)
    queue = deque(seen)
    while queue:
        for position in edges(queue.popleft()):
            if position not in seen:
                seen.add(position)
                queue.append(position)
    return seen


class GeometryTests(unittest.TestCase):
    def test_maze_has_no_slide_cycles_or_reachable_softlocks(self):
        maze = json.loads((GENERATED / "maze_manifest.json").read_text())
        mask = json.loads((GENERATED / "collisions.json").read_text())["114"]
        pushers = {(x, y): direction for x, y, direction in maze["pushers"]}
        stops = set(map(tuple, maze["stops"]))
        warps = {(x, y): (u, v) for x, y, u, v in maze["warps"]}
        goal = tuple(maze["goal"])

        def walkable(position):
            x, y = position
            return (
                0 <= y < len(mask)
                and 0 <= x < len(mask[0])
                and mask[y][x] == "1"
                and position != goal
            )

        for landing in warps.values():
            self.assertTrue(
                walkable(landing) and landing not in warps and landing not in pushers,
                f"Warp lands on a blocked tile or another trigger: {landing}",
            )

        def resolve(position):
            if position in warps:
                return warps[position]
            if position not in pushers:
                return position
            direction = pushers[position]
            seen = set()
            while True:
                direction = pushers.get(position, direction)
                state = (position, direction)
                self.assertNotIn(state, seen, f"Slide cycle at {position}")
                seen.add(state)
                dx, dy = DIRECTIONS[direction]
                next_position = (position[0] + dx, position[1] + dy)
                if not walkable(next_position):
                    return position
                position = next_position
                if position in stops:
                    return position

        def edges(position):
            return [
                resolve(next_position)
                for next_position in neighbors(position)
                if walkable(next_position)
            ]

        positions = reachable([tuple(maze["start"])], edges)
        exits = positions.intersection(neighbors(goal))
        self.assertTrue(exits, "Natu is unreachable")
        # Traverse reversed edges once: every reachable resting place needs a route out.
        predecessors = {position: [] for position in positions}
        for position in positions:
            for destination in edges(position):
                predecessors[destination].append(position)
        escapable = reachable(exits, predecessors.__getitem__)
        self.assertEqual(positions - escapable, set(), "Reachable maze positions trap the player")

    def test_pond_rewards_are_reachable_and_island_requires_surf(self):
        pond = json.loads((GENERATED / "pond_manifest.json").read_text())
        mask = json.loads((GENERATED / "collisions.json").read_text())["108"]
        water = set(map(tuple, pond["water"]))
        island = set(map(tuple, pond["island"]))

        def edges(position, surf=False):
            return [
                (x, y)
                for x, y in neighbors(position)
                if 0 <= y < len(mask)
                and 0 <= x < len(mask[0])
                and (mask[y][x] == "1" or (surf and (x, y) in water))
            ]

        foot = reachable([(18, 5)], edges)
        surf = reachable([(18, 5)], lambda position: edges(position, surf=True))
        self.assertFalse(foot & island, "Island is reachable on foot")
        self.assertLessEqual(island - {tuple(pond["obelisk"])}, surf, "Surf cannot reach landing")
        self.assertLessEqual(set(map(tuple, pond["hidden_path"])), foot, "Hidden spur is blocked")
        self.assertTrue(all(mask[y][x] == "0" for x, y in water), "Water is walkable")
        area = loads((ROOT / "game/Data/Map108.rxdata").read_bytes()).attributes
        for event in area["@events"].values():
            attributes = event.attributes
            name = attributes["@name"]
            if name.startswith("Pond fisher") or name in (
                "Pond hidden cache",
                "Berry:ORANBERRY",
                "Wild:PSYDUCK:shoreduck",
            ):
                self.assertTrue(
                    foot.intersection(neighbors((attributes["@x"], attributes["@y"]))),
                    f"Cannot interact with {name}",
                )
