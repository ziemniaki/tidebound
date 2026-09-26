raise "early Frostcoon evolution" if Pokemon.new(:FROSTCOON, 54).check_evolution_on_level_up
[55, 100].each do |level|
  unless Pokemon.new(:FROSTCOON, level).check_evolution_on_level_up == :NIVALORA
    raise "missing Nivalora evolution"
  end
end
%i[GLACIVERM NIVALORA].each do |species|
  raise "unexpected further evolution" if Pokemon.new(species, 100).check_evolution_on_level_up
end
puts "PASS: current Frostcoon 54/55 evolution threshold and terminal regional species."
