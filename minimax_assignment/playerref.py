#!/usr/bin/env python3
import random

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR,TYPE_TO_SCORE
from time import time
import math
TIME_LIMIT = 75*1e-2

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

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        """ first_msg
        { 'fish0': {'score': 11, 'type': 3}, 
          'fish1': {'score': 2, 'type': 1}, 
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }
        """
        
        # Initialize your minimax model
        #model = self.initialize_model(initial_data=first_msg)

        while True:
            msg = self.receiver() # contains caught_fish, hooks/fish positions, score ect
            self.start_time = time()
            
            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            for max_depth in range(1,5): 
                _,best_move,found = self.search_best_next_move(
                    curr_node=node, depth=max_depth, player=0, alpha=-999999, beta=999999)
                if found:
                    break
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
        
    def search_best_next_move(self, curr_node, depth, player, alpha, beta):
        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###
        
        # NOTE: Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!
        #### 
        # Implement iterative depth search 
        #  as long as there are caught fish (non negative) right now -> return
        #
        
        if time() - self.start_time >= (TIME_LIMIT*0.1):
            #print(check_time - self.start_time)
            score,found = self.heuristic(curr_node)
            move = curr_node.move if curr_node.move is not None else 0
            return score, ACTION_TO_STR[move], True
        
        children = curr_node.compute_and_get_children() #compute children node

        if depth==0 or len(children)== 0:
            score,found = self.heuristic(curr_node)
            return score, ACTION_TO_STR[curr_node.move],found
        
        if player == 0:
            maxEval = -999999
            act = ACTION_TO_STR[0]
            for c in children:
                c_eval,return_act,found = self.search_best_next_move(c,depth-1,1,alpha,beta)
                if c_eval>maxEval:
                    act = return_act
                    maxEval = c_eval
                alpha = max(maxEval,alpha)
                if beta <= alpha or found:
                    break
            return maxEval,act,found
        else:
            minEval = 999999
            random_move = random.randrange(5)
            act = ACTION_TO_STR[0]
            for c in children:
                c_eval,return_act,found = self.search_best_next_move(c,depth-1,0,alpha,beta)
                if c_eval<minEval:
                    act = return_act
                    minEval = c_eval
                beta = min(minEval,beta)
                if beta <= alpha or found:
                    break            
            return minEval,act,found   
        #random_move = random.randrange(5)
        #return ACTION_TO_STR[action],c_eval

    def heuristic(self,curr_node):
        caught = curr_node.state.get_caught()
        player_scores =  curr_node.state.get_player_scores() #p0,p1
        p0_fish_type = caught[0]
        p1_fish_type = caught[1]
        # score for hook's pos
        hook_positions = curr_node.state.get_hook_positions()
        #print("hook_pos")
        #print(hook_pos) {0:(x,y), 1:(x,y)}
        fish_positions = curr_node.state.get_fish_positions() # {0:(x,y), 1:(x,y), 2:(x,y)...} fish_index:pos
        fish_scores = curr_node.state.get_fish_scores() # {0:s1, 1:s2, 2:s3...} fish_index:score
        
        dis_score = 0

        if p0_fish_type is not None:
            p0_score = TYPE_TO_SCORE[p0_fish_type]
            found = True if p0_score>0 else False
            closest_fish_dict = 0
        else:
            hook_fish_dis = {}
            p0_score = 0
            found = False
            # fish_score doen't reove caught fish 
            #-> get index from remaining fishes (fish_positions)
            #-> return index of fish with max score
            #print(fish_positions)
            eDis = {}
            closest_fish_dict = 0
            if fish_positions:
                #print("fish pos is not none")
                for fish_number in fish_positions:
                    if fish_scores[fish_number]>0:
                        eDis[fish_number] = math.hypot(hook_positions[0][0]-fish_positions[fish_number][0],hook_positions[0][1]-fish_positions[fish_number][1])
                if eDis:
                    closest_fish_dict = min(eDis.values())                   
                
                #print("closest_fish_index")
                #print(closest_fish_index)
            
            """
            if fish_positions:
                max_fish_score_index = max(fish_positions, key=fish_scores.get)
                x =  hook_positions[0][0] - fish_positions[max_fish_score_index][0]
                y =  hook_positions[0][1] - fish_positions[max_fish_score_index][1]
                dis = x^2 + y^2
                if dis!=0:
                    dis_score = math.exp( 1/dis )
                else:
                    dis_score = 100
            else:
                dis_score = 0
            """
            

        if p1_fish_type is not None:
            p1_score = TYPE_TO_SCORE[p1_fish_type]
        else:
            p1_score = 0
        final_score = player_scores[0] + p0_score - p1_score - player_scores[1] - closest_fish_dict*0.1
        
        
        return final_score,found


        """
    def search_best_next_move(self, curr_node, depth, alpha, beta):
        
        #Use your minimax model to find best possible next move for player 0 (green boat)
        #:param model: Minimax model
        #:type model: object
        #:param initial_tree_node: Initial game tree node 
        #:type initial_tree_node: game_tree.Node 
        #(see the Node class in game_tree.py for more information!)
        #:return: either "stay", "left", "right", "up" or "down"
        #:rtype: str
        
        children = curr_node.compute_and_get_children()
        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###
        
        # NOTE: Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!
        if depth==0 or len(curr_node.children)== 0:
            score_p0, score_p1 = curr_node.state.get_player_scores()
            return (score_p0 - score_p1),ACTION_TO_STR[curr_node.move]
        player = curr_node.state.get_player()
        if player ==0:
            maxEval = -999999
            random_move = random.randrange(5)
            act = ACTION_TO_STR[random_move]
            for i,c in enumerate(children):
                c_eval,return_act = self.search_best_next_move(c,depth-1,alpha,beta)
                if c_eval>maxEval:
                    act = return_act
                    maxEval = c_eval
                alpha = max(alpha,c_eval)
                if alpha >= beta:
                    break
            return maxEval,act
        else:
            minEval = 999999
            random_move = random.randrange(5)
            act = ACTION_TO_STR[random_move]
            for i,c in enumerate(children):
                c_eval,return_act = self.search_best_next_move(c,depth-1,alpha,beta)
                if c_eval<minEval:
                    act = return_act
                    minEval = c_eval
                beta = min(beta,c_eval)
                if alpha >= beta:
                    break
            return minEval,act
        
        #random_move = random.randrange(5)
        #return ACTION_TO_STR[action],c_eval
        """