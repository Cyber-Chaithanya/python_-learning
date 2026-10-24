# Creating Different objects using self, __init__
'''  In this class we need to learn about the creating the different objects of a class  '''


''' 
1. When we use __init__ we can directly give the parameters in the object.
2. we must need to create the partion to the argument when we use __init__ like ( self.name=name )
 
'''


class Car():
    def __init__(self,name,color,speed):
        self.name=name
        self.color=color
        self.speed=speed
    
    def display(self):
        print(self.name)
        print(self.color)
        print(self.speed)
c=Car('RR','BLUE',200)
c.display()
print('\n')
c2=Car('BMW','RED',"100kmph")
c2.display()
