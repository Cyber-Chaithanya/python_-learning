# program-7
# this is a python program to check the factorial of the given number 

from math import factorial
number=int(input("Enter the number to find the factorial:  "))
if number<0:
    print("please enter the number greater than 0")
else:
    print(factorial(number))