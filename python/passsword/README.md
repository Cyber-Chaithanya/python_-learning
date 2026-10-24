# 🔐 Password Strength Checker

## 📌 About the Project

This is a beginner-friendly Python project that checks whether a password meets specific strength requirements. I developed this project to practice my Python programming concepts and improve my logical thinking and debugging skills.

The program checks the password's length and verifies whether it contains uppercase letters, lowercase letters, numbers, and special characters.

## ✨ Features

- Checks whether the password contains between 12 and 32 characters.
- Verifies the presence of at least one uppercase letter.
- Verifies the presence of at least one lowercase letter.
- Checks whether the password contains at least one number.
- Checks whether the password contains at least one special character.
- Displays the results of individual checks.
- Identifies missing password requirements.
- Allows users to check multiple passwords in one session.

## 🛠️ Technologies Used

- **Programming Language:** Python
- **Concepts Used:**
  - Variables and data types
  - Functions
  - Conditional statements (`if`, `else`)
  - Loops (`while`)
  - String methods (`isupper()`, `islower()`, `isdigit()`)
  - `any()` function
  - User input and output

## 📋 Password Requirements

A password must satisfy all the following requirements to pass this program's checks:

1. Minimum length: 12 characters.
2. Maximum length: 32 characters.
3. At least one uppercase letter (A–Z).
4. At least one lowercase letter (a–z).
5. At least one digit (0–9).
6. At least one special character (such as `@`, `#`, `$`, or `!`).

## 🚀 How to Run the Project

### Prerequisites

Install Python 3 on your computer.

### Steps

1. Clone or download this repository.
2. Open the project folder in your terminal or code editor.
3. Run the Python source file:

   ```bash
   python password_strength_checker.py
   ```

4. Enter a test password when prompted.
5. Read the validation results.
6. Choose whether to check another password.

**Note:** Replace `password_strength_checker.py` in the command above if your actual Python file has a different name.

## 🧪 Example Output

```text
Enter a test password: River!Cloud72X

--- PASSWORD CHECK RESULTS ---
Uppercase letter: True
Lowercase letter: True
Number: True
Special character: True

Password meets all the requirements!

Do you want to check another password? (yes/no): no
Program closed. Thank you!
```

## 📚 What I Learned

While building this project, I practiced:

- Writing my own Python program using an algorithm.
- Creating and calling functions.
- Checking strings using built-in methods.
- Applying Boolean logic and conditional statements.
- Debugging syntax and logical errors.
- Using loops to allow repeated program execution.
- Organizing source code and documenting a project for GitHub.

## 🔮 Future Improvements

- Add a score-based password strength indicator.
- Improve validation for empty or whitespace-only input.
- Detect commonly used or easily guessed passwords.
- Add unit tests for different input cases.
- Develop a graphical user interface (GUI).

## ⚠️ Disclaimer

This project is intended for educational purposes. It checks a limited set of password rules and does not guarantee that a password is secure. Do not enter real or sensitive passwords while testing.

## 👨‍💻 Author

**A Python learner exploring programming, problem-solving, and cybersecurity.**

This is one of my beginner projects as I continue improving my Python skills and building my programming portfolio.

## 🌐 Personal Portfolio

Explore my personal portfolio to learn more about me, my programming journey, technical skills, projects, education, and certifications.

🔗 **Live Portfolio:** [Naga Chaithanya — Python Developer Portfolio](https://naga-portfolio.lovable.app)
