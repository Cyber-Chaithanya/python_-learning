# program-1 
# Implement a Python Program Program to Prompt for a Score between 0 and 10. If the   Score Is Out of Range, Print an Error. If the Score Is between 0 and 10, Print a Grade Using the Following Table.

# program-1
# Grade calculator

def grade(score):
    if score < 0 or score > 10:
        print("Error: Score is out of range. \n Please enter valid score between 0 to 10.")
    else:
        if score >= 9 and score < 11:
            print(" score grade A")
        elif score == 8:
            print("Scored grade B")
        elif score == 7:
            print("score grade C")
        elif score == 6:
            print("Scored grade D")
        else:
            print("FAILED.......")

score = int(input("Enter your score between 0 to 10: "))
grade(score)

retry = input("do u want to retry? (y/n): ").lower()

while retry == 'yes' or retry == 'y':
    score = int(input("Enter your score between 0 to 10: "))
    grade(score)
    retry = input("do u want to retry? (y/n): ").lower()

if retry == 'no' or retry == 'n':
    print("thank you for using the program \n EXITING.....")
