#!/usr/bin/env python3
#Robert file
import random
import math
from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR
from fishing_game_core.game_tree import State


class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        # Initialize your minimax model
        model = self.initialize_model(initial_data=first_msg)

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)
            node.state.get_fish_positions()
            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(
                model=model, initial_tree_node=node)
            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def initialize_model(self, initial_data):
        """
        Initialize your minimax model
        :param initial_data: Game data for initializing minimax model
        :type initial_data: dict
        :return: Minimax model
        :rtype: object

        Sample initial data:
        { 'fish0': {'score': 11, 'type': 3},
          'fish1': {'score': 2, 'type': 1},
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }

        Please note that the number of fishes and their types is not fixed between test cases.
        """
        # EDIT THIS METHOD TO RETURN A MINIMAX MODEL ###

        return None

    def heuristics(self, node):

        score = 0
        hookPos = node.state.get_hook_positions()[0]
        for index in node.state.get_fish_positions():
            distance = self.manDistance(hookPos, node.state.get_fish_positions()[index])
            if (distance == 0 and node.state.get_fish_scores()[index] > 0):
                return 1000

            if (distance == 0):
                distance = 0.01
            score += (1 / distance) * node.state.get_fish_scores()[index]

        return score

    def manDistance(self, hookPos, fishPos):
        x = abs(hookPos[0] - fishPos[0])
        y = abs(hookPos[1] - fishPos[1])

        x = min(x, 20 - x)

        return x + y


    def minimax(self, node, depth, player, alpha, beta):
        if (depth == 3):

            return node.state.get_player_scores()[0] - node.state.get_player_scores()[1]

        else:
            if player == 0:
                best = -math.inf
                bestMove = 0
                for child in node.compute_and_get_children():
                    value = self.minimax(child, depth+1, 1, alpha, beta)
                    if (value > best):
                        best = value
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break

                return best

            else:
                best = math.inf
                for child in node.compute_and_get_children():
                    value = self.minimax(child, depth+1, 0, alpha, beta)
                    if (value < best):
                        best = value
                    beta = min(best, beta)
                    if beta <= alpha:
                        break

                return best

    def computeBestMove(self, node):
        children = node.compute_and_get_children()
        scores = []
        for child in children:
            player = child.state.get_player()
            score = self.minimax(child, 0, player, -math.inf, math.inf)
            scores.append(score)

        return scores.index(max(scores))

    def search_best_next_move(self, model, initial_tree_node):
        """
        Use your minimax model to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###

        # NOTE: Don't forget to initialize the children of the current node
        #       with its compute_and_get_children() method!

        # bestMove = self.computeBestMove(initial_tree_node)
        # player = initial_tree_node.state.get_player()
        # _, bestMove = self.minimax(initial_tree_node, 0, player, -math.inf, math.inf)

        bestMove = self.computeBestMove(initial_tree_node)

        return ACTION_TO_STR[bestMove]