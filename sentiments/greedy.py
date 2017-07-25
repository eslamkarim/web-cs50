import cs50

def main():
    change=0  
    coins=0
    while change <= 0:
        print("change: ", end="")
        change=cs50.get_float()
    change *= 100
    round(change)
    
    while change >= 100:
        change -= 100
    
    while change > 0:
        if change >= 25:
            change -= 25
            coins += 1
        elif change < 25 and change >= 10:
            change -= 10
            coins += 1
        elif change < 10 and change >= 5:
            change -= 5
            coins += 1
        else:
            change -= 1
            coins += 1
    
    print (coins)    
    
    
if __name__=="__main__":
    main()