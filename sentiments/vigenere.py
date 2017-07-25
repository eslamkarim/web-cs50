import cs50
import sys

def main():
    key = sys.argv[1]
    key = key.lower()
    count = 0
    if len(sys.argv) != 2 or key.isalpha() == False :
        print("Usage: ./vigenere k")
        exit(1)

    print("plaintext: ", end='')
    text = cs50.get_string()
    print("ciphertext: ", end='')
    
    for c in text:
        if count == len(key):
            count = 0
        
        if (ord(c)>=65 and ord(c)<=90) :
            op = ord(c)+ ord(key[count])- 97
            if op > 90:
                op -=26
            print("{}".format(chr(op)), end='')
            count += 1
        elif (ord(c)>=97 and ord(c)<=122):  
            op = ord(c)+ ord(key[count])- 97
            if op > 122:
                op -=26
            print("{}".format(chr(op)), end='')
            count += 1
        else:
            op=ord(c)
            print("{}".format(chr(op)), end='')
        
    print()    
    
    
    
    
    
    
    
    


if __name__=="__main__":        
    main()