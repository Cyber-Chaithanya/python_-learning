# Program-4
# Implement a python program to print thr average of n numbers.


print("Calculating the average of n numbers......")
def average(n):
    total=0
    avg=0
    if n<=0:
        print("INPUT INVALID.... \n Please enter a valid input, greater than 0")
    else:
        for i in range(1,n+1,1):
            total+=i
        avg=total/n
        print("The average of the entered numbers is: ", avg)
n=int(int(input("Enter the number of elements to need to calculate the average:  ")))
average(n)
recalculate=input("Do you want to re-Calculate the average? (yes/no): ").lower()
while recalculate=='yes' or recalculate =='y':
    n=int(int(input("Enter the number of elements to need to calculate the average:  ")))
    average(n)
    recalculate=input("Do you want to re-Calculate the average? (yes/no): ").lower()
if recalculate =='no' or recalculate == 'n':
    print("Thank u for using the program \n EXITING......")