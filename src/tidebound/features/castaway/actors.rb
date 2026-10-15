Tidebound::Actors.on_entry(:castaway_canvas) { !Tidebound::Castaway.flags[:canvas] }
Tidebound::Actors.on_entry(:castaway_tools) { !Tidebound::Castaway.flags[:tools] }
Tidebound::Actors.on_entry(:castaway_shelter) { Tidebound::Castaway.flags[:shelter] }
Tidebound::Actors.on_entry(:castaway_signal) { Tidebound::Castaway.flags[:signalled] }
Tidebound::Actors.on_entry(:castaway_cutter) { Tidebound::Castaway.flags[:signalled] }
Tidebound::Actors.on_entry(:castaway_water) { Tidebound::Castaway.flags[:water] }
