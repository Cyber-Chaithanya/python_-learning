n=int(input("Enter the number of elements need to calculate: "))
even_sum=0
odd_sum=0
for i in range(0,n+1,1):
    if i%2==0:
        even_sum+=i
    else:
        odd_sum+=i
print(f" The sum of even numbers is: {even_sum} \n The sum of odd numbers is: {odd_sum}")
