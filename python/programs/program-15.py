
# Program 15: Demonstrating *args and **kwargs

def display_details(*args, **kwargs):
    print("Positional arguments:")
    for item in args:
        print(item)

    print("\nKeyword arguments:")
    for key, value in kwargs.items():
        print(f"{key}: {value}")


display_details(
    "Python",
    "Linux",
    "Networking",
    name="Student",
    goal="Cybersecurity",
    level="Beginner"
)
