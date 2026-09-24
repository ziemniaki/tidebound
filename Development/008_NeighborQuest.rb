# The neighbour's plate: additive state, ordinary objects, delayed reinterpretation.
module Tidebound
  module NeighborQuest
    PIE=:TIDEBOUNDPIE
    PLATE=:TIDEBOUNDPLATE
    NECKLACE=:TIDEBOUNDNECKLACE
    ROSTERS={
      :first=>[:TBLOCALYOUTH,"Toma","I wasn't even trying!",[[:RATTATA,5,[:TACKLE,:TAILWHIP]]]],
      :runner=>[:TBABYSSRUNNER,"Bram","This is coming out of somebody's share.",[[:ZIGZAGOON,6,[:TACKLE,:GROWL]]]],
      :second=>[:TBLOCALYOUTH2,"Ivo","These pearls aren't even worth this!",[[:POOCHYENA,7,[:TACKLE,:HOWL,:SANDATTACK]]]]
    }.freeze
    WILDS={:shorebird=>[:NATU,4],:shoreforager=>[:ZIGZAGOON,4]}.freeze
    class << self
      attr_accessor :busy,:meal_visible,:meal_eaten,:pearl_visible,:pearl_glint
    end
    module_function
    def q; Opening.flags[:neighbor_quest] ||= {}; end
    def stage; q[:stage]; end
    def actor(name); Opening.actor(name); end
    def say(*lines); lines.each { |s| pbMessage(s) }; end
    def animate(e,route); Opening.animate(e,route); end
    def hint
      return nil unless Opening.flags[:oil_collected]
      case stage
      when nil then "The oil seller has something else for us. Speak to him inside his shop."
      when :pie then "Share the seller's pie with Mother."
      when :plate then "Return the empty blue-reed plate to the oil shop."
      when :pursuit
        return "The thieves ran south. Follow the coast road from the beach." unless q[:first_won]
        q[:heard] ? "Recover the oil seller's necklace from the old storehouse." : "The other boy has the necklace. Look farther down the south coast road."
      when :necklace then "Bring the pearl necklace back to the oil seller."
      when :complete then "The necklace is home. The south coast road and the northern wood are open to explore."
      end
    end
    # Bag capacity must never destroy an item or force a repeated battle.
    def exchange(old_item,new_item)
      return false unless $bag.has?(old_item)
      $bag.remove(old_item,1)
      return true if $bag.add(new_item,1)
      raise Tidebound::TransitionError,"Could not restore quest item" unless $bag.add(old_item,1)
      say("There isn't room in the Key Items pocket. You keep it safely for now.")
      false
    end
    def offer_pie
      return if stage || !Opening.flags[:oil_collected] || !Opening.flags[:shop_unlocked]
      unless $bag.add(PIE,1)
        say("Seller: I've a pie for you and your mother, too. Make a little room; I'll keep it here.")
        return
      end
      q[:stage]=:pie
      say("Seller: Wait, wait. For finding my keys. You've spared an old fool a very cold evening.",
          "He brings out a pie, still warm beneath a tea towel. Two blue reeds are painted on the rim of its plate.",
          "Seller: Take this home to your mother. City 4 recipe. My hometown makes them a little neater.",
          "Seller: I made far too much. Again. A terrible habit. You're helping me with that, too.",
          "You tuck the Homemade Pie safely into the Key Items pocket.",
          "Seller: Bring the plate back afterwards, will you? Good plates are harder to replace than keys.")
    end
    def meal
      return unless stage==:pie && $bag.has?(PIE) && $game_map.map_id==101
      return unless exchange(PIE,PLATE)
      q[:stage]=:plate; self.busy=true
      mother=actor("Mother")
      species=Opening.household_pets.key?(:NATU) ? :NATU : :MAKUHITA
      pet=Opening.household_pets.key?(species) ? actor("House:#{species}") : nil
      saved=[mother,pet,$game_player].compact.map { |e| [e,e.x,e.y,e.direction,e.through] }
      say("Mother: Oh. He still makes these?","Mother: I haven't had one in such a long time. Put it here, love. We'll have a little together.")
      pbFadeOutIn do
        mother.moveto(10,8) if mother; mother.turn_left if mother
        $game_player.moveto(7,8); $game_player.turn_right
        if pet; pet.moveto(species==:NATU ? 7 : 10,10); pet.through=true; end
        self.meal_eaten=false; self.meal_visible=true
      end
      say("The crust flakes onto the plate. Mother catches a crumb with her thumb, then gives you the larger slice.")
      animate(pet,[PBMoveRoute::UP,PBMoveRoute::TURN_UP])
      if species==:NATU && pet
        say("Wick inches closer. His eyes follow every journey of the fork.","Mother: I see you, little gentleman. There's a crumb with your name on it.")
      elsif pet
        say("Maku sets both hands on his knees and sits up very straight.","Mother: Such lovely manners, Maku. Yes, there's a little for you too.")
      end
      pbWait(0.35); self.meal_eaten=true
      say("For a little while, there is only the scrape of forks and the soft sound of eating.",
          "Mother: Just as I remember. Perhaps a little more butter. I shan't complain.",
          "She washes the plate and dries around the two painted reeds.",
          "Mother: Will you take this back when you pass his shop? Mind the rim.",
          "You keep the empty Blue-Reed Plate in the Key Items pocket.")
    ensure
      self.meal_visible=false
      saved&.each { |e,x,y,d,t| e.moveto(x,y); e.direction=d; e.through=t }
      self.busy=false
    end
    def robbery
      return unless stage==:plate && $bag.has?(PLATE) && $game_map.map_id==102
      self.busy=true
      $game_player.moveto(*Opening.coast_xy(23,14)); $game_player.turn_left
      one=actor("Robbery youth one"); two=actor("Robbery youth two"); seller=actor("Seller outside")
      [one,two].compact.each { |e| e.moveto(*Opening.coast_xy(21,11)); e.through=true; e.opacity=255 }
      say("A crash inside the shop. The door bangs open.")
      animate(one,[PBMoveRoute::CHANGE_SPEED,5,PBMoveRoute::DOWN,PBMoveRoute::DOWN]+[PBMoveRoute::RIGHT]*3+[PBMoveRoute::DOWN]*5)
      say("Boy: Hurry up!","Other boy: I AM hurrying! You try running with pockets!")
      route=[PBMoveRoute::CHANGE_SPEED,5]+[PBMoveRoute::DOWN]*2+[PBMoveRoute::RIGHT]*3+[PBMoveRoute::DOWN]*9+[PBMoveRoute::RIGHT]*6+[PBMoveRoute::DOWN]*8
      pbMoveRoute(two,route) if two
      pbMoveRoute(one,[PBMoveRoute::CHANGE_SPEED,5]+[PBMoveRoute::DOWN]*4+[PBMoveRoute::RIGHT]*6+[PBMoveRoute::DOWN]*8) if one
      if seller; seller.moveto(*Opening.coast_xy(21,11)); seller.opacity=255; seller.through=true; end
      say("Seller: HEY! GET BACK HERE, YOU LITTLE--")
      animate(seller,[PBMoveRoute::CHANGE_SPEED,3,PBMoveRoute::DOWN,PBMoveRoute::DOWN,PBMoveRoute::RIGHT])
      say("He grips the wall. His next step won't come.","Seller: Oh, damn these legs.")
      deadline=System.uptime+20
      while [one,two].compact.any?(&:move_route_forcing)
        raise "Tidebound: robbery escape timed out" if System.uptime>deadline
        pbWait(0.025)
      end
      [one,two].compact.each { |e| e.opacity=0 }
      animate(seller,[PBMoveRoute::TURN_DOWN])
      say("Seller: ...you brought my plate back.","Seller: Thank you. Here, let me take that.")
      $bag.remove(PLATE,1); q[:stage]=:pursuit
      say("Seller: A pearl necklace. That's what they've taken. Of all the things in there.",
          "Seller: They went south, down the coast road. If you happen to catch them... I'd be very grateful.",
          "Seller: But mind yourself, little one. Please.")
    ensure
      [one,two,seller].compact.each { |e| e.opacity=0; e.through=true } if defined?(one)
      self.busy=false
    end
    def south_gate
      unless [:pursuit,:necklace,:complete].include?(stage)
        say("The coast road winds south beyond the village. There is something to finish close to home first.")
        $game_player.moveto(*Opening.coast_xy(30,30)); $game_player.turn_up
        return
      end
      Opening.travel(108,18,5,2)
    end
    def wild_visible?(name); !q[(name.split(":").last+"_gone").to_sym]; end
    def wild(id)
      return if q[(id.to_s+"_gone").to_sym]
      species,level=WILDS.fetch(id)
      label=species==:NATU ? "A Natu picks between the wind-bent flowers." : "A Zigzagoon noses through an empty sack."
      return unless pbConfirmMessage(label+" Approach?") && able?
      result=Opening.fight(species,level)
      q[(id.to_s+"_gone").to_sym]=true if [1,4].include?(result)
    end
    def able?
      return true if Tidebound.state.realm==:living && $player.able_pokemon_count>0
      say("Your companions need a little strength before facing anyone. A travelling ninja's fire can help.")
      false
    end
    def trainer(id)
      type,name,loss,team=ROSTERS.fetch(id); foe=NPCTrainer.new(name,type); foe.lose_text=loss
      team.each do |species,level,moves|
        p=Pokemon.new(species,level,foe); p.moves.clear
        moves.each { |move| p.learn_move(move) }; foe.party << p
      end
      foe
    end
    def battle(id)
      return 0 unless able?
      outcome=Tidebound.trainer!(trainer(id))
      if outcome==:astral
        say("The sound of the world draws away."); Opening.travel(105,15,21,8)
      end
      outcome
    end
    def first_thief
      return if stage!=:pursuit || q[:first_won]
      say("Boy: What?","Boy: Oh. You're the lighthouse kid.","Boy: Listen. We didn't steal anything. And even if we did, you can't prove which one of us has it.")
      return unless battle(:first)==1
      q[:first_won]=true
      say("Boy: ...good thing I don't have it.","Boy: I mean-- Look over there!")
      thief=actor("Road thief"); thief.through=true if thief
      animate(thief,[PBMoveRoute::CHANGE_SPEED,5,PBMoveRoute::DOWN,PBMoveRoute::DOWN]+[PBMoveRoute::RIGHT]*3)
      thief.opacity=0 if thief
      say("He runs south before you can point out what he just said.")
    end
    def witness_hideout
      return unless stage==:pursuit && q[:first_won] && !q[:hideout_seen]
      self.busy=true; boy=actor("Running thief")
      if boy; boy.through=true; boy.opacity=255; end
      say("The other boy! He stops at the old storehouse and glances behind him.")
      animate(boy,[PBMoveRoute::CHANGE_SPEED,4]+[PBMoveRoute::RIGHT]*4+[PBMoveRoute::UP]*2)
      if boy; boy.opacity=0; boy.through=true; end
      say("A voice inside: Shut that door! You're letting the packing blow about!")
      q[:hideout_seen]=true
    ensure
      self.busy=false
    end
    def hideout_door
      unless q[:first_won]
        say("The door is barred inside. Someone is still coming down the road.")
        $game_player.moveto(35,42); $game_player.turn_down; return
      end
      witness_hideout; Opening.travel(109,11,14,8)
    end
    def overhear
      Opening.erase_autorun
      return if q[:heard] || stage!=:pursuit
      say("You stop behind a stack of crates. Nobody has noticed the door.",
          "Runner: Boss said no more taking things from houses.","Boy: It wasn't a house. It was a shop.","Runner: That's not what he meant.",
          "Packer: How much do pearls go for?","Boy: Depends.","Packer: On what?","Boy: ...the pearl?",
          "Runner: Just give it to the people at the docks. They buy anything from the coast.",
          "Lookout: Are we getting a proper Team Abyss job next time?","Runner: You're getting a broom. You spilled the packing again.")
      q[:heard]=true
    end
    def runner
      overhear unless q[:heard]
      if q[:runner_won] || stage!=:pursuit
        say("Runner: Fine. Speak to the boy. I'm not taking another fall for his pockets."); return
      end
      say("Runner: Who left the door-- Oh.","Runner: This is a private business. Very private. Out you go.")
      return unless battle(:runner)==1
      q[:runner_won]=true
      say("Runner: All right! You can have your argument with him.","Runner: I'm meant to count boxes. That's the entire job.")
    end
    def second_thief
      if [:necklace,:complete].include?(stage)
        say("Boy: I don't have anything else of his. You can stop looking at my pockets."); return
      end
      unless q[:runner_won]
        say("Runner: Leave him. You want something from here, you talk to me first."); return
      end
      unless q[:second_won]
        say("Boy: Toma said you'd go home!","Boy: You can't just follow people around taking back the things they've taken!")
        return unless battle(:second)==1
        q[:second_won]=true
      end
      unless $bag.add(NECKLACE,1)
        say("Boy: There's no room in your bag. I'll put it on this crate. I'm not fighting you for it again."); return
      end
      q[:stage]=:necklace
      say("He untangles a pearl necklace from the lining of his pocket.","Boy: Here. Take it. Stupid clasp kept catching on everything anyway.","You wrap the Pearl Necklace carefully and put it in the Key Items pocket.")
    end
    def packer; say("Packer: If I put 'assorted' on every box, I can't label one wrong. Can I?"); end
    def lookout; say("Lookout: I told them we should sell things we actually own.","Lookout: Apparently that isn't the idea."); end
    def rest
      choice=pbMessage("Traveller: Sit a while. Even a short road is longer when you're tired.",["Rest","Ask about the storehouse","Leave"],-1)
      if choice==0
        Tidebound::FieldDetails.rest(:road_fire, [108, 26, 39, 8])
      elsif choice==1
        say("Traveller: It used to hold fishing nets. Now there are boys arguing over boxes. They don't like visitors.")
      end
    end
    def return_necklace
      return unless stage==:necklace && $bag.has?(NECKLACE)
      self.busy=true
      say("Seller: ...you actually found it.","He lays it across his palm and works the clasp once. Twice.",
          "Seller: My wife wore this. Every important day of her life, apparently.","Seller: And plenty of unimportant ones.")
      pbWait(0.35)
      say("Seller: She's been gone a while. I still put it beside the mirror when I tidy.","Seller: Thank you for bringing it home.")
      self.pearl_visible=true
      pbWait(0.65) { |t| self.pearl_glint=Math.sin([t/0.65,1.0].min*Math::PI) }
      self.pearl_glint=0
      say("One pearl catches a little more light than the others.","Seller: Funny. They do that sometimes. Pearls catch light.")
      self.pearl_visible=false
      say("Seller: I ought to put it somewhere safer. Maybe the museum down at the docks...","Seller: No. It's nothing of that significance.",
          "Seller: Maybe Ellie could keep it in that humongous vault of yours.","He folds the necklace into a square of soft cloth.",
          "Seller: I'll find a place. You've done enough running on my account. Thank you, little one.")
      $bag.remove(NECKLACE,1); q[:stage]=:complete
    ensure
      self.pearl_visible=false; self.pearl_glint=0; self.busy=false
    end
    def sync_actors
      return if self.busy
      if $game_map.map_id==102
        ["Robbery youth one","Robbery youth two"].each do |name|
          e=actor(name); next unless e; e.opacity=0; e.through=true
        end
      elsif $game_map.map_id==108
        e=actor("Road thief")
        if e
          visible=stage==:pursuit && !q[:first_won]; e.opacity=visible ? 255 : 0; e.through=!visible
        end
        e=actor("Running thief"); if e; e.opacity=0; e.through=true; end
      end
    end
  end
  module NeighborOpeningHooks
    def oil_seller
      case NeighborQuest.stage
      when :necklace then NeighborQuest.return_necklace
      when :plate then travel_coast(21,12); NeighborQuest.robbery
      when :pursuit then pbMessage("Seller: South, along the coast road. But please take care of yourself.")
      when :complete
        pbMessage("Seller: I made another pie. Too much again, naturally.")
        pbMessage("Seller: Next time, bring your mother. We'll use my plates here.")
      else
        super; NeighborQuest.offer_pie if $game_map.map_id==106
      end
    end
    def mother; super; NeighborQuest.meal if flags[:oil_returned]; end
    def shop_door
      if NeighborQuest.stage==:plate && $bag.has?(NeighborQuest::PLATE); NeighborQuest.robbery
      else; super; end
    end
    def outside_seller
      if NeighborQuest.stage==:plate && $bag.has?(NeighborQuest::PLATE); NeighborQuest.robbery
      else; super; end
    end
  end
  Opening.singleton_class.prepend(NeighborOpeningHooks)
end
EventHandlers.add(:on_new_spriteset_map,:tidebound_neighbor_actors,proc { |_s,_v| Tidebound::NeighborQuest.sync_actors })
