''' In this program we need to learn the main use  of self function .
 If we want to use the variables in a funtion from the class inside a function then also we use self. 
 '''
 
 
class Car:
    name='BMW'
    color='RED'
    def speed(self):
        print('200kmph')
        print(self.name,self.color)
        
c=Car()
c.speed()
     