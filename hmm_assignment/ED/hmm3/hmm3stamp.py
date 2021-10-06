# author: Yage Hao (yage@kth.se)

import sys
import math 
import copy 

def split_data(sample_input):
    """split the input data to 
    transition matrix A, 
    emission matrix B,
    initial state probability distribution pi,
    and emission sequence."""
    
    data = []
    for i in range(len(sample_input)):
        data.append(list(sample_input[i].split(" ")))
    #print(data)

    # extract A
    dataA = data[0]
    for i in range(2): dataA[i] = int(dataA[i])
    for i in range(2,len(dataA)-1): dataA[i] = float(dataA[i]) # convert from str to num
    A = []
    for i in range(dataA[0]):
        A.append(dataA[2+i*dataA[1]:2+(i+1)*dataA[1]])
    #print(A)

    # B
    dataB = data[1]
    for i in range(2): dataB[i] = int(dataB[i])
    for i in range(2,len(dataB)-1): dataB[i] = float(dataB[i]) # convert from str to num
    B = []
    for i in range(dataB[0]):
        B.append(dataB[2+i*dataB[1]:2+(i+1)*dataB[1]])
    #print(B)

    # pi
    dataPi = data[2]
    for i in range(2): dataPi[i] = int(dataPi[i])
    for i in range(2,len(dataPi)-1): dataPi[i] = float(dataPi[i]) # convert from str to num
    Pi = []
    for i in range(dataPi[0]):
        Pi.append(dataPi[2+i*dataPi[1]:2+(i+1)*dataPi[1]])
    Pi = Pi[0]
    #print(Pi)

    # emission sequence
    data_emi_seq = data[3]
    emi_seq = []
    for i in range(1,len(data_emi_seq)-1):
        emi_seq.append(int(data_emi_seq[i]))
    #print(emi_seq)

    return A, B, Pi, emi_seq 


def alpha_pass(A, B, Pi, emi_seq, N, T):
    """alpha-pass"""
    # compute alpha0(i)
    c0 = 0
    alpha0 = [None]*N
    #print(len(alpha0))
    for i in range(N):
        alpha0[i] = Pi[i] * B[i][emi_seq[0]]
        c0 += alpha0[i]
    #print(alpha0)

    # scale the alpha0(i)
    c0 = 1/c0 
    for i in range(N):
        alpha0[i] = c0 * alpha0[i]
    #print(alpha0)

    # compute alphat[i]
    tranA = list(map(list, zip(*A)))
    alphat_1 = alpha0 
    alphat = [None]*N
    alphat_list = [alpha0]
    #print(alphat_list)
    ct_list = [c0]
    for t in range(1,T):
        ct = 0
        for i in range(N):
            alphat[i] = 0
            for j in range(N):
                alphat[i] = alphat[i] + alphat_list[t-1][j] * A[j][i]
            alphat[i] = alphat[i] * B[i][emi_seq[t]]
            ct = ct + alphat[i]

        # scale alphat[i]
        ctr = 1/ct 
        for i in range(N):
            alphat[i] = ctr * alphat[i]
        
        #print(ctr)
        alphat_list.append(alphat.copy()) # https://xirikm.net/2019/323-1
        ct_list.append(ctr) 
    #print(len(alphat_list), len(ct_list))
    #print(alphat_list)
    return alphat_list, ct_list 


def beta_pass(A, B, Pi, emi_seq, ct_list, N, T):
    """beta-pass, inverse alpha-pass"""
    ct_list_rev = ct_list[::-1]
    emi_seq_rev = emi_seq[::-1]
    tranA = list(map(list, zip(*A)))

    #  Let βT −1(i) = 1, scaled by cT −1
    beta0 = [None]*N
    for i in range(N):
        beta0[i] = ct_list_rev[0]

    # beta-pass 
    betat = [None]*N
    betat_list_rev = [beta0]
    for t in range(1,T):
        for i in range(N):
            betat[i] = 0
            for j in range(N):
                betat[i] = betat[i] + A[i][j] * B[j][emi_seq_rev[t-1]] * betat_list_rev[t-1][j]
        #print(t,betat)
               
        # scale βt(i) with same scale factor as αt(i)
        for i in range(N):
            betat[i] = ct_list_rev[t] * betat[i]
        
        
        betat_list_rev.append(betat.copy())
        #print(t, betat_list_rev[t])
    #print(t,betat_list_rev)
    return betat_list_rev


def di_gamma(A, B, emi_seq, alphat_list, betat_list, N, T):
    """Compute γt(i, j) and γt(i)"""
    # no need to normalize digammat since using scaled alpha and beta
    digammat = [[None]*N for x in range(N)]
    gammat = [None]*N 
    digammat_list = []
    gammat_list = [] 
    tranA = list(map(list, zip(*A)))
    for t in range(T-1):
        for i in range(N):
            gammat[i] = 0
            for j in range(N):
                digammat[i][j] = alphat_list[t][i] * A[i][j] * B[j][emi_seq[t+1]] * betat_list[t+1][j]
                gammat[i] = gammat[i] + digammat[i][j]
        #print(t,digammat)
        digammat_list.append(copy.deepcopy(digammat))
        gammat_list.append(gammat.copy())
    
    # special case for gammaT_1[i]
    gammaT_1 = [None]*N 
    for i in range(N):
        gammaT_1[i] = alphat_list[T-1][i]
    gammat_list.append(gammaT_1)

    #print(len(digammat_list),len(digammat_list[0]))
    #print(len(gammat_list))
    #print(digammat_list)
    return digammat_list, gammat_list


def re_estimate(gammat_list, digammat_list, emi_seq, M, N, T): 
    """re-estimate A,B and Pi"""
    # re-estimate Pi
    for i in range(N):
        Pi[i] = gammat_list[0][i]
    
    # re-estimate A
    #print(A)
    for i in range(N):
        denom = 0
        for t in range(T-1):
            denom = denom + gammat_list[t][i]
        for j in range(N):
            numer = 0
            for t in range(T-1):
                numer = numer + digammat_list[t][i][j]
            A[i][j] = numer/denom 
    #print(A)

    # re-estimate B
    #print(B)
    for i in range(N):
        denom = 0
        for t in range(T):
            denom = denom + gammat_list[t][i]
        for j in range(M):
            numer = 0
            for t in range(T):
                if emi_seq[t] == j:
                    numer = numer + gammat_list[t][i]
            B[i][j] = numer/denom 
    #print(B)
    return Pi, A, B 
    

def compute_log(ct_list, T):
    """compute log[P(O|model)]"""
    logProb = 0
    for i in range(T):
        logProb =  logProb + math.log(ct_list[i])
    logProb = -logProb 
    return logProb 




if __name__ == '__main__':
    """initialization"""
    sample_input = sys.stdin.readlines()
    A, B, Pi, emi_seq = split_data(sample_input)
    #print(B, Pi, emi_seq[0])

    N = len(B)
    M = len(B[0])
    T = len(emi_seq)

    maxIters = 50
    iters = 0
    oldLogProb = -math.inf 
    logProb = 1

    """
    alphat_list, ct_list, alphat_1 = alpha_pass()
    betat_list = beta_pass(ct_list)
    digammat_list, gammat_list = di_gamma(alphat_list, alphat_1, betat_list)
    A, B = re_estimate(gammat_list, digammat_list)
    logProb = compute_log(ct_list)
    """

    """iterate"""
    while iters < maxIters and logProb > oldLogProb:
        iters = iters + 1
        #print("Iterate:", iters)

        if iters != 1:
            oldLogProb = logProb

        alphat_list, ct_list = alpha_pass(A, B, Pi, emi_seq, N, T)
        #print(alphat_list[-1])
        betat_list_rev = beta_pass(A, B, Pi, emi_seq, ct_list, N, T)
        betat_list = betat_list_rev[::-1]
        #print(betat_list[0])
        digammat_list, gammat_list = di_gamma(A, B, emi_seq, alphat_list, betat_list, N, T)
        #print(gammat_list[-1])
        Pi, A, B = re_estimate(gammat_list, digammat_list, emi_seq, M, N, T)
        logProb = compute_log(ct_list, T)


    """output"""
    #print(A)
    A_list = []
    for i in A:
        for j in i:
            j_round = round(j,6)
            A_list.append(str(j_round))
    A_str = ' '.join([a for a in A_list])
    print(str(N), str(N), A_str)
    

    #print(B)
    B_list = []
    for i in B:
        for j in i:
            j_round = round(j,6)
            B_list.append(str(j_round))
    B_str = ' '.join([a for a in B_list])
    print(str(N), str(M), B_str)

    




    

        


        
            


        
