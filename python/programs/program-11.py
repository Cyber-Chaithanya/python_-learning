# program- 11
# Area of a trapizum

def area(a,b,c):
    area=(1/2)*(a+b)*c
    return area
a=int(input("Enter the side one length: "))
b=int(input("Enter the side two length: "))
c=int(input("Enter the trapizium height: "))
print("The area of the trapizium is:  ", area(a,b,c))
    