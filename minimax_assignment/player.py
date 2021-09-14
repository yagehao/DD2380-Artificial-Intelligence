#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR

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

            # Possible next moves: "stay", "left", "right", "up", "down"
            _, best_move = self.search_best_next_move(
                model=model, initial_tree_node=node, depth_counter=-1)
            #print(best_move)

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

    def search_best_next_move(self, model, initial_tree_node, depth_counter):
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

        #random_move = random.randrange(5)
        #return ACTION_TO_STR[random_move]

        depth_counter += 1
        #print("depth_counter:", depth_counter)

        current_state = initial_tree_node
        children = current_state.compute_and_get_children()

        if depth_counter == 3: # terminal state
            v = self.heuristic(current_state)
            action = ACTION_TO_STR[current_state.move]
            #print("11111:", v, action)
            return v, action # action led to node current_state

        else:
            if current_state.state.get_player() == 0: # player A
                #print("AAAAAAAA")
                best_v = -99999999 # heuristic value
                best_action = "DEFAULT"
                for child in children:
                    v, action = self.search_best_next_move(model, child, depth_counter)
                    #print("222222:", v, action)
                    
                    if v > best_v: 
                        best_v = max(best_v, v)
                        best_action = action 
                    #print("333333:", best_v, best_action)
                return best_v, best_action

            else: # player B, current_state.state.get_player() == 1
                #print("BBBBBBBBB")
                best_v = 99999999
                best_action = "DEFAULT"
                for child in children:
                    v, action = self.search_best_next_move(model, child, depth_counter)
                    #print("44444:", v, action)
    
                    if v < best_v: 
                        best_v = min(best_v, v)
                        best_action = action
                    #print("555555:", best_v, best_action)
                return best_v, best_action







        
    def heuristic(self, node):
        """
        Compute naive heuristic value for node.
        :param node: a node in game tree
        :type node: game_tree.Node
        :return: heuristic value
        :type: float
        """
        heuristic_value = node.state.player_scores[0] - node.state.player_scores[1]

        return heuristic_value
