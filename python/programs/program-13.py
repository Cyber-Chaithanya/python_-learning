# program-13
# Armstrong number

num=int(input("Enter a number:  ")) # taking the input
lent=len(str(num))   # measuring the length  to perform power operation
num_str=str(num)  # converting into string format to iterate each digit easly in for loo[]
total=0   
for i in num_str:
    total+=int(i)**lent

if total==num:  # checking the condition if the total of power of each digit equals to the num or not
    print(f"{num} is an armstrong number")    # printing the output
else:
    print(f"{num} is not a armstrong number")