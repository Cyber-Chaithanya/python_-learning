# prime number or not
number=int(input("Enter the number: "))
is_prime=True
if number<2:
    print("It is not a prime number.....")
else:
    for i in range(2,number):
        if number%i==0:
            is_prime=False
            break
    if is_prime:
        print(f"{number} is the prime number")
    else:
        print(f"{number} is not a prime number")