# HMM0
# encoding: utf-8

import sys

def data(IN0):
    """store input data in list IN00"""

    IN00 = []
    for i in range(len(IN0)):
        IN00.append(list(IN0[i].split()))
        #print(IN00)
    return(IN00)

def tranA(IN00):
    """implement transition matrix A"""

    dataA = IN00[0]
    for i in range(2): dataA[i] = int(dataA[i])
    for i in range(2,len(dataA)): dataA[i] = float(dataA[i]) # convert from str to num

    A = []
    for i in range(dataA[0]):
        #print(i)
        A.append(dataA[2+i*dataA[1]:2+(i+1)*dataA[1]])

    return(A)

def emiB(IN00):
    """implement emission matrix B"""

    dataB = IN00[1]
    for i in range(2): dataB[i] = int(dataB[i])
    for i in range(2,len(dataB)): dataB[i] = float(dataB[i]) # convert from str to num

    B = []
    for i in range(dataB[0]):
        #print(i)
        B.append(dataB[2+i*dataB[1]:2+(i+1)*dataB[1]])

    return(B)

def distPi(IN00):
    """implement initial state probability distribution Pi"""

    dataPi = IN00[2]
    for i in range(2): dataPi[i] = int(dataPi[i])
    for i in range(2,len(dataPi)): dataPi[i] = float(dataPi[i]) # convert from str to num

    Pi = []
    for i in range(dataPi[0]):
        #print(i)
        Pi.append(dataPi[2+i*dataPi[1]:2+(i+1)*dataPi[1]])

    return(Pi)

def Q2(Pi, A):
    """HMM0 Question2"""
    # preset result matrix
    result0 = []
    for i in range(len(Pi)*len(A[0])): result0.append(0)
    #print(result0)

    result = []

    m1 = len(Pi)
    n1 = len(A[0]) # index of result matrix is m1Xn1

    for i in range(m1):
        result.append(result0[i*n1:(i+1)*n1])
    #print(result)


    for i in range(len(Pi)):
        for j in range(len(Pi[0])):
            for k in range(len(A[0])):
                result[i][k] += Pi[i][j] * A[j][k]
    #print(result)

    return(result)

def Q3(result, B):
    """HMM0 Question3"""
    # preset emission probability distribution matrix
    dist0 = []
    for i in range(len(result)*len(B[0])): dist0.append(0)
    #print(dist0)


    dist = []

    m2 = len(result)
    n2 = len(B[0]) # index of dist matrix is m2Xn2

    for i in range(m2):
        dist.append(dist0[i*n2:(i+1)*n2])

    #print(dist)


    for i in range(len(result)):
        for j in range(len(result[0])):
            for k in range(len(B[0])):
                dist[i][k] += result[i][j] * B[j][k]
    #print(dist)

    return(dist, m2, n2)

def finalmat(dist, m2, n2):
    a = len(dist)
    b = len(dist[0])
    output = [a,b]

    for i in range(m2):
        for j in range(n2):
            output.append(dist[i][j])
    #print(output)

    for i in range(len(output)): output[i] = str(output[i])
    answer = " ".join(map(str, output)) # convert content of list into str
    print(answer)

    return(answer)

if __name__ == '__main__':
    IN0 = sys.stdin.readlines()
    #print(IN0)
    IN00 = data(IN0)
    A = tranA(IN00)
    B = emiB(IN00)
    Pi = distPi(IN00)
    result = Q2(Pi, A)
    dist, m2, n2 = Q3(result, B)
    finalmat(dist, m2, n2)


# check
#f = open('kth.ai.hmm0/sample_00.ans','r')
#f.read()