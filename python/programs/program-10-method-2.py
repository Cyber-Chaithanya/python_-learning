
def calculator(numbers, choice):
    result = numbers[0]

    for i in numbers[1:]:
        if choice == "+":
            result += i
        elif choice == "-":
            result -= i
        elif choice == "*":
            result *= i
        elif choice == "/":
            if i == 0:
                return "Error: Cannot divide by zero"
            result /= i
        elif choice == "%":
            if i == 0:
                return "Error: Cannot use modulo with zero"
            result %= i
        elif choice == "**":
            result **= i
        else:
            return "Invalid operation"

    return result


numbers = list(map(int, input("Enter numbers separated by spaces: ").split()))
choice = input("Enter the operation (+, -, *, /, %, **): ")

if not numbers:
    print("Please enter at least one number.")
else:
    print("The result is:", calculator(numbers, choice))
