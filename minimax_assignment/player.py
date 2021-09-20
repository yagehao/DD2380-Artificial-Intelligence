#!/usr/bin/env python3
import random
import math 

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
            #_, best_move = self.minimax(
            #    model=model, initial_tree_node=node, depth_counter=-1)
            _, best_move = self.minimax_with_pruning(
                model=model, initial_tree_node=node, depth_counter=0, alpha=-math.inf, beta=math.inf)
            #print(best_move)
            #print("1111111111111：", best_move)

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

    def minimax_with_pruning(self, model, initial_tree_node, depth_counter, alpha, beta):
        """
        Use your minimax model with alpha-beta pruning to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node 
            (see the Node class in game_tree.py for more information!)
        :param depth_counter: depth of the node in the tree
        :type depth_counter: int
        :param alpha: alpha value in alpha-beta pruning
        :type alpha: float
        :param beta: beta value in alpha-beta pruning
        :type beta: float
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###
        
        # NOTE: Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!

        #random_move = random.randrange(5)
        #return ACTION_TO_STR[random_move]

        #depth_counter += 1
        #print("depth_counter:", depth_counter)

        current_state = initial_tree_node
        children = current_state.compute_and_get_children()

        if depth_counter == 5 or children == None: # terminal state
            v = self.heuristic(current_state)
            action = ACTION_TO_STR[current_state.move]
            #print("11111:", v, action)
            return v, action # action led to node current_state

        else:
            if current_state.state.get_player() == 0: # player A
                #print("AAAAAAAA")
                best_v = -math.inf # heuristic value
                #best_action = "DEFAULT"
                #best_action = ACTION_TO_STR[1] #"UP"

                for child in children:
                    v, action = self.minimax_with_pruning(model, child, depth_counter+1, alpha, beta)
                    #print("222222:", v, action)
                    
                    if v > best_v: 
                        best_v = max(best_v, v)
                        best_action = action 
                    #print("333333:", best_v, best_action)

                    alpha = max(alpha, best_v)
                    if beta <= alpha:
                        #print("PRUNING")
                        break # beta prune
                return best_v, best_action

            else: # player B, current_state.state.get_player() == 1
                #print("BBBBBBBBB")
                best_v = math.inf
                #best_action = "DEFAULT"
                #best_action = ACTION_TO_STR[1] #"UP"

                for child in children:
                    v, action = self.minimax_with_pruning(model, child, depth_counter+1, alpha, beta)
                    #print("44444:", v, action)
    
                    if v < best_v: 
                        best_v = min(best_v, v)
                        best_action = action
                    #print("555555:", best_v, best_action)

                    beta = min(beta, best_v)
                    if beta <= alpha:
                        #print("PRUNING")
                        break # alpha prune
                return best_v, best_action

    

    def minimax(self, model, initial_tree_node, depth_counter):
        """
        Use your minimax model to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node
        :type initial_tree_node: game_tree.Node 
            (see the Node class in game_tree.py for more information!)
        :param depth_counter: depth of the node in the tree
        :type depth_counter: int
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###
        
        # NOTE: Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!

        #random_move = random.randrange(5)
        #return ACTION_TO_STR[random_move]

        #depth_counter += 1
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
                    v, action = self.minimax(model, child, depth_counter)
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
                    v, action = self.minimax(model, child, depth_counter)
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
        score_diff = node.state.player_scores[0] - node.state.player_scores[1]

        # hook position
        your_hook = node.state.get_hook_positions()[0]
        oppo_hook = node.state.get_hook_positions()[1]

        # fish position and scores
        fish_pos = node.state.get_fish_positions()
        fish_score = node.state.get_fish_scores() 

        # heuristics = 1 / distance(hook, fish_pos) * fish_score
        heuristic_value = 0
        for i in fish_pos.keys():
            if your_hook == fish_pos[i]:
                #print("111111111111111", ACTION_TO_STR[node.move])
                return 99999999 # you catch the fish

            d = self.distance(your_hook, fish_pos[i], oppo_hook)
            #heuristic_value += 1 / d * fish_score[i]
            heuristic_value = max(heuristic_value, 1 / d * fish_score[i])
            
        return heuristic_value + 2 * score_diff


    def distance(self, your_hook, fish_pos, oppo_hook):
        "Manhattan distance"
        
        # block case 1: you oppo fish
        if fish_pos[0] - your_hook[0] > oppo_hook[0] - your_hook[0]:
            x = your_hook[0] + (20 - fish_pos[0])
            y = abs(fish_pos[1] - your_hook[1])
            d = x + y 

        # block case 2: fish oppo you
        elif your_hook[0] - fish_pos[0] > oppo_hook[0] - fish_pos[0]:
            x = fish_pos[0] + (20 - your_hook[0])
            y = abs(fish_pos[1] - your_hook[1])
            d = x + y 
        
        else:
            x = abs(fish_pos[0] - your_hook[0])
            y = abs(fish_pos[1] - your_hook[1])
            d = x + y 

        return d



# if a fish is catching by opponent, then stop considering to catch it