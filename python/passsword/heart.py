
# Print I ❤️ U in the same height and size

height = 30
width = 30

# Create I
I = []
for y in range(height):
    row = ""
    for x in range(width):
        if y < 4 or y >= height - 4 or 12 <= x < 18:
            row += "*"
        else:
            row += " "
    I.append(row)

# Create Heart
heart = []
for y in range(15, -15, -1):
    row = ""
    y1 = y / 10

    for x in range(-30, 30):
        x1 = x / 15
        f = (x1**2 + y1**2 - 1)**3 - x1**2 * y1**3
        row += "*" if f <= 0 else " "

    heart.append(row)

# Create U
U = []
for y in range(height):
    row = ""
    for x in range(width):
        if x < 4 or x >= width - 4 or y >= height - 4:
            row += "*"
        else:
            row += " "
    U.append(row)

# Print all three side by side
for y in range(height):
    print(I[y] + "   " + heart[y] + "   " + U[y])
