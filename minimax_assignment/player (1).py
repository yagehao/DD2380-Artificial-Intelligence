#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR, TYPE_TO_SCORE

import time 
import math 


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
        self.start_time = None 
        #self.checked_dict = dict() # node already checked {node : [score, move]}

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
            self.checked_dict = dict() # node already checked {node : [score, move]}

            #IDS
            self.start_time = time.time() 
            for max_depth in range(3,15,2):
                #print(max_depth)
                if time.time() - self.start_time > 0.016:
                    #print("111111111111111111", max_depth)
                    best_move = move
                    break 
                _, move = self.search_best_next_move(
                    node, depth=max_depth, player=0, alpha=-math.inf, beta=math.inf)
            best_move = move 
            #print(best_move)
            
            
            '''
            max_depth = 3
            _, best_move = self.search_best_next_move(
                node, depth=max_depth, player=0, alpha=-math.inf, beta=math.inf)
            '''

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

    def search_best_next_move(self, node, depth, player, alpha, beta):
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

        # repeated state checking using string hash
        key = self.strhash(node.state)
        if key in self.checked_dict and self.checked_dict[key][0] >= depth:
            return self.checked_dict[key][1], self.checked_dict[key][2]

        children = node.compute_and_get_children()
        #children.sort(key=self.heuristics, reverse=True) # move ordering
        
        if depth==0 or len(children)== 0:
            h = self.heuristics(node) ######################
            action = ACTION_TO_STR[node.move]
            self.checked_dict.update({key : [depth, h, action]})
            return h, action 

        if player == 0:
            best_max = -math.inf
            #best_action = ACTION_TO_STR[0]
            #children.sort(key=self.heuristics, reverse=True) # move ordering 
            for child in children:
                h, action = self.search_best_next_move(child, depth-1, 1, alpha, beta)
                if h > best_max:
                    best_max = h 
                    best_action = action
                alpha = max(best_max, alpha)
                if alpha >= beta:
                    break 
            self.checked_dict.update({key : [depth, best_max, best_action]})
            return best_max, best_action
        else:
            best_min = math.inf
            #best_action = ACTION_TO_STR[0]
            #children.sort(key=self.heuristics, reverse=False) # move ordering 
            for child in children:
                h, action = self.search_best_next_move(child, depth-1, 0, alpha, beta)
                if h < best_min:
                    best_min = h 
                    best_action = action
                beta = min(best_min, beta)
                if alpha >= beta:
                    break 
            self.checked_dict.update({key : [depth, best_min, best_action]})
            return best_min, best_action
                

    def heuristics(self, node):

        score = 0
        diff = node.state.get_player_scores()[0] - node.state.get_player_scores()[1]
        hookPos = node.state.get_hook_positions()[0]
        oppoPos = node.state.get_hook_positions()[1]
        oppoFish = node.state.player_caught[1]

        for index in node.state.get_fish_positions():
            #p2_distance = self.distance(oppoPos, node.state.get_fish_positions()[index], hookPos)
            # if opponent caught the fish, not consider this fish anymore
            #if p2_distance == 0:
            if index == oppoFish:
                #print("STOOOOOOOOOOP")
                diff -= node.state.get_fish_scores()[index]
                #continue 
            
            p1_distance = self.distance(hookPos, node.state.get_fish_positions()[index], oppoPos)
            # you catch the positive scored fish
            if (p1_distance == 0 and node.state.get_fish_scores()[index] > 0):
                diff += node.state.get_fish_scores()[index]
            # you catch the negative scored fish
            #if (p1_distance == 0):
            #    p1_distance = 0.01
            
            #distance = p1_distance - p2_distance
            #score += (1 / p1_distance) * node.state.get_fish_scores()[index]
            score = max(score, math.exp(-p1_distance) * node.state.get_fish_scores()[index])

        return score + diff * 2

    def distance(self, your_hook, fish_pos, oppo_hook):

        # block case 1: you oppo fish
        if (your_hook[0]<oppo_hook[0]) and (oppo_hook[0]<fish_pos[0]):
            x = your_hook[0] + (20 - fish_pos[0])
            y = abs(fish_pos[1] - your_hook[1])

        # block case 2: fish oppo you
        elif (your_hook[0]>oppo_hook[0]) and (oppo_hook[0]>fish_pos[0]):
            x = fish_pos[0] + (20 - your_hook[0])
            y = abs(fish_pos[1] - your_hook[1])
        
        else:
            x = abs(fish_pos[0] - your_hook[0])
            x = min(x, 20-x)
            y = abs(fish_pos[1] - your_hook[1])

        return math.hypot(x,y) # prefer to move vertically

    def strhash(self, state):
        # str: scores + yourhookpos + oppohookpos + fishpos + fishscore
        fish_pos_dict = dict()
        for fish_pos, fish_score in zip(state.get_fish_positions().items(), state.get_fish_scores().items()):
            x = str(fish_pos[0])
            y = str(fish_pos[1])
            fish_pos_dict.update({x+y : fish_score[1]})

        key = str(state.get_player_scores()) + str(state.get_hook_positions()) + str(fish_pos_dict)            
        return key 