
# Program 14: Surface area of two cubes using nested functions

def calculate_total_area(side1, side2):

    def surface_area(side):
        return 6 * side ** 2

    area1 = surface_area(side1)
    area2 = surface_area(side2)

    return area1 + area2


side1 = float(input("Enter the side length of the first cube: "))
side2 = float(input("Enter the side length of the second cube: "))

if side1 < 0 or side2 < 0:
    print("Side lengths cannot be negative.")
else:
    total = calculate_total_area(side1, side2)
    print("Surface area of the first cube:", 6 * side1 ** 2)
    print("Surface area of the second cube:", 6 * side2 ** 2)
    print("Total surface area:", total)
