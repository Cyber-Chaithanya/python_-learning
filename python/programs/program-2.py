# Program-2
# Implement a Python program to check whether the given year is a leap year or not

print("Checking whether the year you entered is a leap year or not........")
def leap_year(year):
    if year % 400 == 0:
        print(f'{year} is a leap year')
    elif year % 100 == 0:
        print(f'{year} is not a leap year')
    elif year % 4 == 0:
        print(f'{year} is a leap year')
    else:
        print(f'{year} is not a leap year')
year=int(input("Enter an year to check:  "))
leap_year(year)
recheck=input("do u want to recheck? (yes/no): ").lower()
while recheck=='yes' or recheck=='y':
    year=int(input("Enter an year to check:  "))
    leap_year(year)
    recheck=input("do u want to recheck? (yes/no): ").lower()
if recheck == 'no' or recheck == 'n':
    print("Thnak you for using the program \n EXITING.....")