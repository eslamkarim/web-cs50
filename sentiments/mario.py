import cs50

def main():
    height=0
    while height > 23 or height <= 0:
        print("height: ", end='')
        height=cs50.get_int()
        
    for i in range(1, height+1, 1):
        j=height-1
        
        for j in range(j, 0, -1 ):
            print(" ", end='')
        
        for x in range(0, i, 1):
            print("#", end='')
        
        print("  ", end='')
        height-=1
        
        for x in range(0, i, 1):
            print("#", end='')
        print()
    
    
if __name__=="__main__":
    main()
