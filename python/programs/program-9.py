# program- 9
# display only positive numbers

numbers=map(int,input("Enter the numbers:  ").split())
for i in numbers:
    if i<=0:
        continue
    else:
        print(i)
        