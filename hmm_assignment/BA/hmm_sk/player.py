#!/usr/bin/env python3

from player_controller_hmm import PlayerControllerHMMAbstract
from constants import *
import random
#from baum_welch import Model
#from FORWARD import Forward
import copy
import math 

class PlayerControllerHMM(PlayerControllerHMMAbstract):
    def init_parameters(self):
        init_A = [[1]]
        init_B = [[1/8]*8]
        init_Pi = [1]
        self.emi_seq = None
        self.last_guess = [0]
        # self.current_model = (self.A, self.B, self.Pi)
        self.all_models = [[init_A, init_B, init_Pi]]*7
        self.indexes = 0
        self.revealed_fish = [None]*70
        self.data = [[] for x in range(70)]
        """
        In this function you should initialize the parameters you will need,
        such as the initialization of models, or fishes, among others.
        """
        pass

    """
    def get_json(self):
        filename = 'sequences.json'
        with open(filename, 'r') as f:
            data = json.load(f)

        return data
    """

    def predict(self, emission_seq):
        probabilities = []

        for model in self.all_models:
            prob = Forward(model, emission_seq).compute_prob()
            
            """
            print("_______________________")
            print("BEGINNNNNNNNNNNNNNNNN")
            print(model)
            print(prob)
            print("_______________________")
            """
            
            
            probabilities.append([prob])


        idx = probabilities.index(max(probabilities))


        return idx

    def guess(self, step, observations):
        # B = [[1/8]*8]
        # data = self.get_json()
        # self.A.pop()
        # print("HEREEEEE")
        # print(self.A)
        # model = Model([[1]], B, [1], data["sequences"][0])
    #     """
    #     This method gets called on every iteration, providing observations.
    #     Here the player should process and store this information,
    #     and optionally make a guess by returning a tuple containing the fish index and the guess.
    #     :param step: iteration number
    #     :param observations: a list of N_FISH observations, encoded as integers
    #     :return: None or a tuple (fish_id, fish_type)
    #     """        

        
        #print(step)

        if step <= 110:
            for i in range(len(observations)):
                self.data[i].append(observations[i])
            return None 

        elif (step==111):
            #print("REACHING")
            return (0, 0)

        else:
            fish_index = step-111
            type = self.predict(self.data[fish_index])
            #self.last_guess = [type]
            return (step-111, type)
    #
    #     # This code would make a random guess on each step:
    #     return None

    def reveal(self, correct, fish_id, true_type):

        #print("111111111111", correct, fish_id, true_type)
        #print(self.all_models)
        current_model = copy.deepcopy(self.all_models[true_type]) 

        if not correct:
            #self.revealed_fish[fish_id] = true_type
            emi_seq = self.data[fish_id]

            A = current_model[0]
            B = current_model[1]
            Pi = current_model[2]


            learnt_model = Model(A, B, Pi, emi_seq)
            newA, newB, newPi = learnt_model.iteration()

            current_model[0] = newA 
            current_model[1] = newB 
            current_model[2] = newPi 
        
            #self.all_models[true_type] = newA, newB, newPi

        self.all_models[true_type] = current_model
        #print(self.all_models)
        #print("____________________________")

        """
        This methods gets called whenever a guess was made.
        It informs the player about the guess result
        and reveals the correct type of that fish.
        :param correct: tells if the guess was correct
        :param fish_id: fish's index
        :param true_type: the correct type of the fish
        :return:
        """
        pass



class Model:
    def __init__(self, A, B, Pi, emi_seq):
        self.A = A
        self.B = B
        self.Pi = Pi
        self.emi_seq = emi_seq

    def alpha_pass(self, N, T):
        """alpha-pass"""
        # compute alpha0(i)
        c0 = 0
        alpha0 = [None] * N
        # print(len(alpha0))
        for i in range(N):
            alpha0[i] = self.Pi[i] * self.B[i][self.emi_seq[0]]
            c0 += alpha0[i]
        # print(alpha0)

        # scale the alpha0(i)
        c0 = 1 / (c0 + 0.00000000000000000001)
        for i in range(N):
            alpha0[i] = c0 * alpha0[i]
        # print(alpha0)

        # compute alphat[i]
        alphat = [None] * N
        alphat_list = [alpha0]
        # print(alphat_list)
        ct_list = [c0]
        for t in range(1, T):
            ct = 0
            for i in range(N):
                alphat[i] = 0
                for j in range(N):
                    alphat[i] = alphat[i] + alphat_list[t - 1][j] * self.A[j][i]
                alphat[i] = alphat[i] * self.B[i][self.emi_seq[t]]
                ct = ct + alphat[i]

            # scale alphat[i]
            ctr = 1 / (ct + 0.00000000000000000001)
            for i in range(N):
                alphat[i] = ctr * alphat[i]

            # print(ctr)
            alphat_list.append(alphat.copy())  # https://xirikm.net/2019/323-1
            ct_list.append(ctr)
            # print(len(alphat_list), len(ct_list))
        # print(alphat_list)
        return alphat_list, ct_list


    def beta_pass(self, ct_list, N, T):
        """beta-pass, inverse alpha-pass"""
        ct_list_rev = ct_list[::-1]
        emi_seq_rev = self.emi_seq[::-1]
        tranA = list(map(list, zip(*self.A)))

        #  Let ??T ???1(i) = 1, scaled by cT ???1
        beta0 = [None] * N
        for i in range(N):
            beta0[i] = ct_list_rev[0]

        # beta-pass
        betat = [None] * N
        betat_list_rev = [beta0]
        for t in range(1, T):
            for i in range(N):
                betat[i] = 0
                for j in range(N):
                    betat[i] = betat[i] + self.A[i][j] * self.B[j][emi_seq_rev[t - 1]] * betat_list_rev[t - 1][j]
            # print(t,betat)

            # scale ??t(i) with same scale factor as ??t(i)
            for i in range(N):
                betat[i] = ct_list_rev[t] * betat[i]

            betat_list_rev.append(betat.copy())
            # print(t, betat_list_rev[t])
        # print(t,betat_list_rev)
        return betat_list_rev


    def di_gamma(self, alphat_list, betat_list, N, T):
        """Compute ??t(i, j) and ??t(i)"""
        # no need to normalize digammat since using scaled alpha and beta
        digammat = [[None] * N for x in range(N)]
        gammat = [None] * N
        digammat_list = []
        gammat_list = []
        tranA = list(map(list, zip(*self.A)))
        for t in range(T - 1):
            for i in range(N):
                gammat[i] = 0
                for j in range(N):
                    digammat[i][j] = alphat_list[t][i] * self.A[i][j] * self.B[j][self.emi_seq[t + 1]] * betat_list[t + 1][j]
                    gammat[i] = gammat[i] + digammat[i][j]
            # print(t,digammat)
            digammat_list.append(copy.deepcopy(digammat))
            gammat_list.append(gammat.copy())

        # special case for gammaT_1[i]
        gammaT_1 = [None] * N
        for i in range(N):
            gammaT_1[i] = alphat_list[T - 1][i]
        gammat_list.append(gammaT_1)

        # print(len(digammat_list),len(digammat_list[0]))
        # print(len(gammat_list))
        # print(digammat_list)
        return digammat_list, gammat_list


    def re_estimate(self, gammat_list, digammat_list, M, N, T):
        """re-estimate A,B and Pi"""
        # re-estimate Pi
        for i in range(N):
            self.Pi[i] = gammat_list[0][i]

        # re-estimate A
        # print(A)
        for i in range(N):
            denom = 0
            for t in range(T - 1):
                denom = denom + gammat_list[t][i]
            for j in range(N):
                numer = 0
                for t in range(T - 1):
                    numer = numer + digammat_list[t][i][j]
                self.A[i][j] = numer / (denom + 0.00000000000000000001)
                # print(A)

        # re-estimate B
        # print(B)
        for i in range(N):
            denom = 0
            for t in range(T):
                denom = denom + gammat_list[t][i]
            for j in range(M):
                numer = 0
                for t in range(T):
                    if self.emi_seq[t] == j:
                        numer = numer + gammat_list[t][i]
                self.B[i][j] = numer / (denom + .00000000000000000001)
                # print(B)
        return self.Pi, self.A, self.B


    def compute_log(self, ct_list, T):
        """compute log[P(O|model)]"""
        logProb = 0
        for i in range(T):
            logProb = logProb + math.log(ct_list[i])
        logProb = -logProb
        return logProb

    def iteration(self):

        N = len(self.B)
        M = len(self.B[0])
        T = len(self.emi_seq)

        maxIters = 50
        iters = 0
        oldLogProb = -math.inf
        logProb = 1

        while iters < maxIters and logProb > oldLogProb:
            iters = iters + 1
            # print("Iterate:", iters)

            if iters != 1:
                oldLogProb = logProb

            alphat_list, ct_list = self.alpha_pass(N, T)
            # print(alphat_list[-1])
            betat_list_rev = self.beta_pass(ct_list, N, T)
            betat_list = betat_list_rev[::-1]
            # print(betat_list[0])
            digammat_list, gammat_list = self.di_gamma(alphat_list, betat_list, N, T)
            # print(gammat_list[-1])
            self.Pi, self.A, self.B = self.re_estimate(gammat_list, digammat_list, M, N, T)
            logProb = self.compute_log(ct_list, T)

        return self.A, self.B, self.Pi

        # A_list = []
        # for i in A:
        #     for j in i:
        #         j_round = round(j, 6)
        #         A_list.append(str(j_round))
        # A_str = ' '.join([a for a in A_list])
        # print(str(N), str(N), A_str)
        #
        # # print(B)
        # B_list = []
        # for i in B:
        #     for j in i:
        #         j_round = round(j, 6)
        #         B_list.append(str(j_round))
        # B_str = ' '.join([a for a in B_list])
        # print(str(N), str(M), B_str)




class Forward:
        def __init__(self, model, emission_sequence):

            self.transition_matrix = model[0]
            self.initial_matrix = model[2]
            self.emission_matrix = model[1]
            self.emission_sequence = emission_sequence

        def compute_alpha0(self):
            obs_0 = self.emission_sequence[0]
            alpha0 = [0.0] * len(self.initial_matrix)
            for i in range(len(alpha0)):
                alpha0[i] = self.initial_matrix[i] * self.emission_matrix[i][obs_0]

            return alpha0

        def compute_intermediate_sum(self, i, alpha):
            sum = 0
            for j in range(len(alpha)):
                sum += alpha[j] * self.transition_matrix[j][i]
            return sum

        def compute_alphas(self, prev_alpha):
            new_alpha = [0.0] * len(prev_alpha)
            num_obs = len(self.emission_sequence)
            for t in range(1, num_obs):
                for i in range(len(prev_alpha)):
                    intermediate_sum = self.compute_intermediate_sum(i, prev_alpha)
                    new_alpha[i] = intermediate_sum * self.emission_matrix[i][self.emission_sequence[t]]
                prev_alpha = new_alpha
                new_alpha = [0.0] * len(prev_alpha)
            return sum(prev_alpha)

        def compute_prob(self):
            alpha0 = self.compute_alpha0()
            prob = self.compute_alphas(alpha0)
            #print(prob)

            return prob