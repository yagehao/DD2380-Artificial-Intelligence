# input hmm3_01.in
# output hmm3_01.ans

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


def delta_pass(delta, A, b):
    # transpose A
    mat = list(map(list, zip(*A)))
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            mat[i][j] = mat[i][j] * delta[j] * b[i]
    
    new_delta = []
    idx = []
    for row in mat:
        new_delta.append(max(row))
        #print(max(row))
        for i in range(len(row)):
            if row[i] == max(row):
                idx.append(i)
                break 

    #print(new_delta)
    #print(idx)
    return new_delta, idx 


if __name__ == '__main__':
    sample_input = sys.stdin.readlines()
    A, B, Pi, emi_seq = split_data(sample_input)
    #print(B,Pi,emi_seq)
    
    # initial state: delta1(i) = b_i(o1) * Pi_i
    o1 = emi_seq[0]
    b = []
    for row in B:
        b.append(row[o1])
    delta1 = []
    for i,j in zip(b, Pi):
        delta1.append(i*j)
    #print(delta1)

    D = [delta1]
    IDX = []
    # next emission and b
    for obs in emi_seq[1::]:
        b = []
        for row in B:
            b.append(row[obs])
        new_delta,idx = delta_pass(D[-1], A, b)
        D.append(new_delta)
        IDX.append(idx)
    
    print(D)
    print(IDX)

    # backtrack
    state_seq = [D[-1].index(max(D[-1]))] # last step 
    for ls in IDX[::-1]:
        print(ls[state_seq[0]])
        state_seq.insert(0, ls[state_seq[0]])
        #print(state_seq)
    
    print(' '.join([str(x) for x in state_seq]))

        


