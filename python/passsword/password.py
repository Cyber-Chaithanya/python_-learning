
def password_strength(password):
    print("\nThe password must contain 12–32 characters,")
    print("at least one uppercase, lowercase, number,")
    print("and special character.")

    # Step 1: Check password length
    if len(password) < 12 or len(password) > 32:
        print("\nPassword is INVALID.")
        print("Password length must be between 12 and 32 characters.")
        return

    # Step 2: Check character requirements
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)

    special_characters = "!@#$%^&*()-_=+{}[]|;:',.<>/?`~\\"
    has_special = any(char in special_characters for char in password)

    # Step 3: Display results
    print("\n--- PASSWORD CHECK RESULTS ---")
    print("Uppercase letter:", has_upper)
    print("Lowercase letter:", has_lower)
    print("Number:", has_digit)
    print("Special character:", has_special)

    # Step 4: Determine password validity
    if has_upper and has_lower and has_digit and has_special:
        print(f"\nPassword meets all the requirements! \n This {password} is strong.")
    else:
        print("\nPassword is INVALID or INCOMPLETE.")

        if not has_upper:
            print("- Add at least one uppercase letter.")

        if not has_lower:
            print("- Add at least one lowercase letter.")

        if not has_digit:
            print("- Add at least one number.")

        if not has_special:
            print("- Add at least one special character.")


# Step 5: Main program and recheck loop
while True:
    password = input("\nEnter a test password: ")
    password_strength(password)

    recheck = input("\nDo you want to check another password? (yes/no): ")
    
    if recheck.strip().lower() != "yes":
        print("Program closed. Thank you!")
        break
