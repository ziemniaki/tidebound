raise "forest encounter roster" unless GameData::Encounter.get(103).types[:Land]==[[45,:AIPOM,3,5],[40,:WEEDLE,3,5],[15,:WURMPLE,3,5]]
raise "road encounter roster" unless GameData::Encounter.get(108).types[:Land]==[[40,:ZIGZAGOON,4,6],[35,:SUNKERN,4,6],[15,:EKANS,4,6],[10,:PSYDUCK,4,6]]
puts "PASS: current forest and road encounter species, weights and level ranges."
