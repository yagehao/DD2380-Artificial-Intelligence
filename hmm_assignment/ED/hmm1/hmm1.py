# author: Yage Hao (yage@kth.se)

import sys

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


def alpha_pass(alpha, A, b):
    # transpose A
    mat = list(map(list, zip(*A)))
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            mat[i][j] = mat[i][j] * alpha[j] * b[i]
    
    new_alpha = []
    for row in mat:
        new_alpha.append(sum(row))
    #print(new_alpha)
    return new_alpha 


if __name__ == '__main__':
    # init A,B,Pi
    sample_input = sys.stdin.readlines()
    A, B, Pi, emi_seq = split_data(sample_input)
    #print(A,B,Pi,len(emi_seq))

    # alpha-pass
    # initial state: alpha1(i) = b_i(o1) * Pi_i
    o1 = emi_seq[0]
    b = []
    for row in B:
        b.append(row[o1])
    alpha1 = []
    for i,j in zip(b, Pi):
        alpha1.append(i*j)
    #print(alpha1) 

    Alpha = [alpha1]
    # next emission and b
    for obs in emi_seq[1::]:
        b = []
        for row in B:
            b.append(row[obs])
        new_alpha = alpha_pass(Alpha[-1], A, b)
        Alpha.append(new_alpha)
    #print(Alpha)

    likelihood = sum(Alpha[-1])
    print(likelihood)