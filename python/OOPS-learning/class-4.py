'''  in this class we need to learn the __init__ constructor.
1. The __init__ constructor run code automatically when an object is created.
2. self stores the data inside object
3. When we use  __init__  we do not need to call the function inside a class to print the output.
'''
# example:

class Car:
    name='BMW'
    color='RED'
    def __init__(self):
        print(self.name,self.color)
        print('200kmph')
    def speed(self):
        print('speed is executed....')
c=Car()
c.speed()
