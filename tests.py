from random import randint, randrange


stuff = [1,2,3,4,5,6,7,8,9]


while len(stuff) > 0:
    element = random.choice(stuff)


for d1 in range(1,10) :
    used = [d1]
    num1 = d1 * 10000
    for d2 in range(1,10) :
        if d2 in used :
            continue
        num1 += d2*1000
        used.append(d2)
        for d3 in range(1,10) :
            if d3 in used :
                continue
            num1 += d3*100
            used.append(d3)
            for d4 in range(1,10) :
                if d4 in used :
                    continue
                num1 += d4*10
                used.append(d4)
                for d5 in range(1,10) :
                    if d5 in used :
                        continue
                    num1 += d5*1
                    used.append(d5)
                    for d6 in range(1,10) :
                        if d6 in used :
                            continue
                        num2 = d6*1000
                        used.append(d6)
                        for d7 in range(1,10) :
                            if d7 in used :
                                continue
                            num2 += d7*100
                            used.append(d7)
                            for d8 in range(1,10) :
                                if d8 in used :
                                    continue
                                num2 += d8*10
                                used.append(d8)
                                for d9 in range(1,10) :
                                    if d9 in used :
                                        continue
                                    num2 += d9*1
                                    used.append(d9)



        