class GameActionsMixin:
    def _trigger_visible_effect(self, card_type):
        if self._check_court_victories():
            return self._complete_turn(self.last_message)

        if card_type == 0:
            self.pending_effect = {"type": "assassin_peek", "step": "choose_two_court_cards"}
            return {
                "ok": True,
                "turn_completed": False,
                "message": "Choose two court cards to peek.",
                "pending_effect": self.pending_effect,
                "winner": self.winner,
            }

        if card_type == 1:
            self.pending_effect = {"type": "knight_swap", "step": "swap_two_court_cards"}
            return {
                "ok": True,
                "turn_completed": False,
                "message": "Choose two court cards to swap.",
                "pending_effect": self.pending_effect,
                "winner": self.winner,
            }

        if card_type == 2:
            self.pending_effect = {"type": "queen_peek", "step": "choose_two_enemy_cards"}
            return {
                "ok": True,
                "turn_completed": False,
                "message": "Choose two enemy hand cards to inspect.",
                "pending_effect": self.pending_effect,
                "winner": self.winner,
            }

        if card_type == 3:
            self.pending_effect = {"type": "king_choice", "step": "choose_mode"}
            return {
                "ok": True,
                "turn_completed": False,
                "message": "Choose king mode: flip or draw.",
                "pending_effect": self.pending_effect,
                "winner": self.winner,
            }

        return self._complete_turn("Move completed")

    def _flip_court(self, court_index, trigger_effect=True):
        self.court_cards[court_index].visible = not self.court_cards[court_index].visible
        if self._check_court_victories():
            return self._complete_turn(self.last_message)

        if self.court_cards[court_index].visible and trigger_effect:
            return self._trigger_visible_effect(self.court_cards[court_index].typeCard)

        return self._complete_turn("Card flipped")

    def _swap_hand_court(self, hand_index, court_index, visible):
        self.court_cards[court_index], self.players[self.currentPlayerId].cards[hand_index] = (
            self.players[self.currentPlayerId].cards[hand_index],
            self.court_cards[court_index],
        )
        self.court_cards[court_index].visible = bool(visible)

        if self.court_cards[court_index].visible:
            return self._trigger_visible_effect(self.court_cards[court_index].typeCard)

        if self._check_court_victories():
            return self._complete_turn(self.last_message)
        return self._complete_turn("Card swapped")

    def _handle_pending(self, action):
        pending_type = self.pending_effect["type"]
        action_type = action.get("type")

        if pending_type == "assassin_peek":
            if action_type != "assassin_peek":
                return {"ok": False, "message": "Expected assassin_peek action."}
            indices = action.get("indices", [])
            if len(indices) != 2 or indices[0] == indices[1]:
                return {"ok": False, "message": "Pick two different court cards."}
            if not all(self._validate_index(idx, 0, 3) for idx in indices):
                return {"ok": False, "message": "Court indices must be between 0 and 3."}
            private = [self.court_cards[indices[0]].name, self.court_cards[indices[1]].name]
            result = self._complete_turn("Assassin effect resolved")
            result["private"] = {"peeked_cards": private}
            return result

        if pending_type == "knight_swap":
            if action_type != "knight_swap":
                return {"ok": False, "message": "Expected knight_swap action."}
            first = action.get("first_index")
            second = action.get("second_index")
            if first == second:
                return {"ok": False, "message": "Pick two different court cards."}
            if not self._validate_index(first, 0, 3) or not self._validate_index(second, 0, 3):
                return {"ok": False, "message": "Court indices must be between 0 and 3."}
            self.court_cards[first], self.court_cards[second] = self.court_cards[second], self.court_cards[first]
            if self._check_court_victories():
                return self._complete_turn(self.last_message)
            self.pending_effect = {"type": "knight_flip", "step": "flip_one_court_card_no_effect"}
            return {
                "ok": True,
                "turn_completed": False,
                "message": "Swap done. Flip one court card (no effect).",
                "pending_effect": self.pending_effect,
                "winner": self.winner,
            }

        if pending_type == "knight_flip":
            if action_type != "knight_flip":
                return {"ok": False, "message": "Expected knight_flip action."}
            court_index = action.get("court_index")
            if not self._validate_index(court_index, 0, 3):
                return {"ok": False, "message": "Court index must be between 0 and 3."}
            self.court_cards[court_index].visible = not self.court_cards[court_index].visible
            if self._check_court_victories():
                return self._complete_turn(self.last_message)
            return self._complete_turn("Knight effect resolved")

        if pending_type == "queen_peek":
            if action_type != "queen_peek":
                return {"ok": False, "message": "Expected queen_peek action."}
            indices = action.get("indices", [])
            if len(indices) != 2 or indices[0] == indices[1]:
                return {"ok": False, "message": "Pick two different enemy card slots."}
            if not all(self._validate_index(idx, 0, 2) for idx in indices):
                return {"ok": False, "message": "Enemy indices must be between 0 and 2."}

            opp_id = self._opponent_id(self.currentPlayerId)
            opp_cards = self.players[opp_id].cards
            private_names = []
            queens_removed = 0

            for idx in sorted(indices, reverse=True):
                card = opp_cards[idx]
                private_names.append(card.name)
                if card.typeCard == 2:
                    removed = opp_cards.pop(idx)
                    self.deck.append(removed)
                    replacement = self._draw_card()
                    if replacement is not None:
                        opp_cards.append(replacement)
                    queens_removed += 1

            result = self._complete_turn("Queen effect resolved")
            result["private"] = {
                "revealed_cards": list(reversed(private_names)),
                "queens_removed": queens_removed,
            }
            return result

        if pending_type == "king_choice":
            if action_type != "king_choice":
                return {"ok": False, "message": "Expected king_choice action."}
            mode = action.get("mode")
            if mode == "flip":
                self.pending_effect = {"type": "king_flip", "step": "flip_and_trigger"}
                return {
                    "ok": True,
                    "turn_completed": False,
                    "message": "Choose one court card to flip.",
                    "pending_effect": self.pending_effect,
                    "winner": self.winner,
                }
            if mode == "draw":
                drawn = 0
                for _ in range(2):
                    card = self._draw_card()
                    if card is not None:
                        self.players[self.currentPlayerId].cards.append(card)
                        drawn += 1
                self.pending_effect = {
                    "type": "king_discard",
                    "step": "discard_two_cards",
                    "drawn": drawn,
                }
                return {
                    "ok": True,
                    "turn_completed": False,
                    "message": "Choose two cards from your hand to discard to deck.",
                    "pending_effect": self.pending_effect,
                    "winner": self.winner,
                }
            return {"ok": False, "message": "King mode must be 'flip' or 'draw'."}

        if pending_type == "king_flip":
            if action_type != "king_flip":
                return {"ok": False, "message": "Expected king_flip action."}
            court_index = action.get("court_index")
            if not self._validate_index(court_index, 0, 3):
                return {"ok": False, "message": "Court index must be between 0 and 3."}
            self.court_cards[court_index].visible = not self.court_cards[court_index].visible
            if self._check_court_victories():
                return self._complete_turn(self.last_message)
            if self.court_cards[court_index].visible:
                return self._trigger_visible_effect(self.court_cards[court_index].typeCard)
            return self._complete_turn("King effect resolved")

        if pending_type == "king_discard":
            if action_type != "king_discard":
                return {"ok": False, "message": "Expected king_discard action."}
            indices = action.get("indices", [])
            if len(indices) != 2 or indices[0] == indices[1]:
                return {"ok": False, "message": "Pick two different hand cards."}
            cards = self.players[self.currentPlayerId].cards
            max_index = len(cards) - 1
            if not all(self._validate_index(idx, 0, max_index) for idx in indices):
                return {"ok": False, "message": "Discard indices are out of range."}

            for idx in sorted(indices, reverse=True):
                removed = cards.pop(idx)
                self.deck.append(removed)
            return self._complete_turn("King draw/discard effect resolved")

        return {"ok": False, "message": "Unknown pending effect state."}

    def apply_action(self, player_id, action):
        self.check_start_turn_victory()
        if self.winner is not None:
            return {
                "ok": False,
                "message": "Game is already finished.",
                "winner": self.winner,
            }

        if player_id != self.currentPlayerId:
            return {
                "ok": False,
                "message": "It is not your turn.",
                "winner": self.winner,
            }

        if not isinstance(action, dict):
            return {"ok": False, "message": "Action payload must be an object."}

        if self.pending_effect is not None:
            return self._handle_pending(action)

        action_type = action.get("type")

        if action_type == "flip_court":
            court_index = action.get("court_index")
            if not self._validate_index(court_index, 0, 3):
                return {"ok": False, "message": "Court index must be between 0 and 3."}
            return self._flip_court(court_index, trigger_effect=True)

        if action_type == "swap_hand_court":
            hand_index = action.get("hand_index")
            court_index = action.get("court_index")
            visible = bool(action.get("visible", False))
            if not self._validate_index(hand_index, 0, len(self.players[self.currentPlayerId].cards) - 1):
                return {"ok": False, "message": "Hand index is out of range."}
            if not self._validate_index(court_index, 0, 3):
                return {"ok": False, "message": "Court index must be between 0 and 3."}
            return self._swap_hand_court(hand_index, court_index, visible)

        return {"ok": False, "message": "Unknown action type."}
