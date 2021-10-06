import sys

def transition(line1):
    # Transition matrix 4x4
    A = []
    for i in range(int(line1[0])):
        A.append(line1[2 + i*int(line1[1]) : 2 + (i+1)*int(line1[1])])
    #print(A)
    return A 

def emission(line2):
    # Emission matrix 4x3
    B = []
    for i in range(int(line2[0])):
        B.append(line2[2 + i*int(line2[1]) : 2 + (i+1)*int(line2[1])])
    #print(B)
    return B 

def distribution(line3):
    # distribution matrix 1x4
    pi = []
    for i in range(int(line3[0])):
        pi.append(line3[2 + i*int(line3[1]) : 2 + (i+1)*int(line3[1])])
    #print(pi)
    return pi 

def next_obs_dis(A, B, pi):
    # multiply distribution matrix with transition matrix
    tranA = list(map(list, zip(*A)))
    res = []
    for i in range(len(tranA)):
        value = 0
        for num1, num2 in zip(tranA[i], pi[0]):
            value += num1 * num2
        res.append(value)
    #print(res)

    # multiply res matrix with emission matrix
    tranB = list(map(list, zip(*B)))
    output = []
    for i in range(len(tranB)):
        value = 0
        for num1, num2 in zip(tranB[i], res):
            value += num1 * num2
        output.append(value)
    #print(output)
    return output 

if __name__ == '__main__':
    data = sys.stdin.readlines()
    line1 = list(map(float, data[0].split(" ")))
    line2 = list(map(float, data[1].split(" ")))
    line3 = list(map(float, data[2].split(" ")))

    A = transition(line1)
    B = emission(line2)
    pi = distribution(line3)
    output = next_obs_dis(A, B, pi)

    output.insert(0, len(B[0]))
    output.insert(0, len(pi))
    ans = " ".join(map(str, output))
    print(ans)
    #ans 