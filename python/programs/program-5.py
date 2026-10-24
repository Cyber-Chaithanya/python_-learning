from math import gcd

a,b=map(int,input("Enter two numbers to find GCD: ").split())
GCD=gcd(a,b)
print(f"The GCD of {a} and {b} is:   {GCD}")