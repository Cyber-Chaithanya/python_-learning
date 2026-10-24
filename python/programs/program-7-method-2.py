# method 2 of program 7
# factorial of number without using built in functions


def factorial(n):
    if n<0:
        print("please enter the number is non-negative")
    else:
        fact=1
        for i in range(1,n+1):
            fact*=i
        print(fact)
n=int(input("Enter the number:  "))
factorial(n)