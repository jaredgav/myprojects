if __name__ == '__main__':
    print('Author: Ronaldo')

    x = input('First variable (num): ')
    x  = int(x) 

    y = input('Next variable (operator): ')
    
    z = input('Last variable (num): ')
    z  = int(z) 

    if y == '+' :
        answer = x + z
    elif y == '*':
        answer = x * z
    elif y == '/':
        answer = x / z
    elif y == '-':
        answer = x - z
    else:
        print('bad operator')
            
    print('Answer is ', answer)


