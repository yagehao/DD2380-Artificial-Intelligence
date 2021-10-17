import sys
import math
import copy

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

        #  Let βT −1(i) = 1, scaled by cT −1
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

            # scale βt(i) with same scale factor as αt(i)
            for i in range(N):
                betat[i] = ct_list_rev[t] * betat[i]

            betat_list_rev.append(betat.copy())
            # print(t, betat_list_rev[t])
        # print(t,betat_list_rev)
        return betat_list_rev


    def di_gamma(self, alphat_list, betat_list, N, T):
        """Compute γt(i, j) and γt(i)"""
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


















