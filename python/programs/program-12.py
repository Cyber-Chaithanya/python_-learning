# program-12
# return multiple values using functions

def values(a,b):
    addition=a+b
    difference=a-b
    product=a*b
    division=a/b
    remainder=a%b
    return addition,difference,product,division,remainder
a=int(input("Enter the first number: "))
b=int(input("Enter the second number: "))
print(values(a,b))
    
    