# Shared NPCs have one explicit interaction order across the story's chapters.
module Tidebound
  module Interactions
    module_function

    def oil_seller
      if vault_reward_pending?
        VaultVisit.reward
        return
      end

      case NeighborQuest.stage
      when :necklace
        NeighborQuest.return_necklace
      when :plate
        Tidebound::World.travel_coast(21, 12)
        NeighborQuest.robbery
      when :pursuit
        pbMessage('Seller: South, along the coast road. But please take care of yourself.')
      when :complete
        pbMessage('Seller: I made another pie. Too much again, naturally.')
        pbMessage("Seller: Next time, bring your mother. We'll use my plates here.")
      else
        Opening.collect_oil
        NeighborQuest.offer_pie if $game_map.map_id == 106
      end

      VaultVisit.reward if vault_reward_pending?
    end

    def mother
      if VaultVisit.q[:gift] && !VaultVisit.q[:open]
        VaultVisit.mother
      elsif VaultVisit.q[:museum]
        pbMessage('Mother: Did you find the museum? Good. I am glad you went.')
      else
        Opening.mother_dialogue
        NeighborQuest.meal if Tidebound.story[:oil_returned]
      end
    end

    def shop_door
      if returning_plate?
        NeighborQuest.robbery
      else
        Opening.enter_shop
      end
    end

    def outside_seller
      if returning_plate?
        NeighborQuest.robbery
      else
        Opening.unlock_shop
      end
    end

    def hint
      VaultVisit.hint || NeighborQuest.hint
    end

    def vault_reward_pending?
      NeighborQuest.stage == :complete && !VaultVisit.q[:gift]
    end

    def returning_plate?
      NeighborQuest.stage == :plate && $bag.has?(NeighborQuest::PLATE)
    end
  end
end
