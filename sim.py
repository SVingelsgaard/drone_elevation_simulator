import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.uix.image import Image
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.properties import NumericProperty
import matplotlib.pyplot as plt

#windowsize
Config.set('graphics', 'width', '700')
Config.set('graphics', 'height', '700')

class Aircraft(ButtonBehavior, Image):
    velocity = NumericProperty(0)
    def on_touch_down(self, touch):
        #self.velocity = 100
        super().on_touch_down(touch)
class Environment(Widget):
    pass

class Simulation(Widget):
    pass

class Program(App):
    #variabels
    GRAVITY = -50 #pixel s^2. -35 = 1 little square
    MASS = 1 #kg
    MAXTHRUST = 100 #newton

    CYCLETIME = 0.02 #sec

    #for PID
    #ny Ku:0.15 Tu:16.26
    Kp = .3
    Ki = .037
    Kd = 1.612

    setPoint = 300
    error = 0
    integralError = 0
    errorLast = 0
    derivativeError = 0
    output = 0 #in newton
    velocity = 0
    timePassed = 0
    #for graph
    runTime = 0
    graphXrunTime = []
    graphY1 = []
    graphY2 = []
    graphY3 = []
    graphKp = []
    graphKi = []
    graphKd = []
    def cycle(self, timePassed):
        #defining AC
        AC = self.root.ids.AC
        SP = self.root.ids.SP
        SP.y = self.setPoint
        #PID inctance
        self.PID()
        #calculate and set position
        AC.y = AC.y + AC.velocity * timePassed
        #calculate and set velocety
        AC.velocity += (self.GRAVITY + (self.output/self.MASS)) * timePassed
        #integrating runtime
        self.runTime += timePassed
        #setting time passed
        self.timePassed = timePassed
        #saving graph variables in lists
        self.graphY1.append(self.setPoint)
        self.graphY2.append(AC.y)
        self.graphY3.append(self.output)
        self.graphKp.append(self.Kp * self.error)
        self.graphKi.append(self.Ki * self.integralError)
        self.graphKd.append(self.Kd * self.derivativeError)
        self.graphXrunTime.append(self.runTime)

    def PID(self):
        #calculate error
        self.error = self.setPoint - self.root.ids.AC.y
        #calculate output
        self.integralError += self.error * self.timePassed

        if self.timePassed == 0:
            self.timePassed = self.CYCLETIME
        else:
            self.derivativeError = (self.error - self.errorLast) / self.timePassed
        self.errorLast = self.error
        self.output = (self.Kp * self.error) + (self.Ki * self.integralError) + (self.Kd * self.derivativeError)
        if self.output >= self.MAXTHRUST:
            self.output = self.MAXTHRUST
        elif self.output <= 0:
            self.output = 0

    def thrustOn(self):
        self.output = self.MAXTHRUST
    def thrustOff(self):
        self.output = 0

    def showGraph(self):
        #main plot
        plt.title('Simulation logger')
        plt.xlabel('Time(s)')
        plt.ylabel('Height(m)')
        plt.grid(True)
        plt.plot(self.graphXrunTime, self.graphY1, 'r', label = 'Setpoint')
        plt.plot(self.graphXrunTime, self.graphY2, 'b', label = 'Position')
        plt.plot(self.graphXrunTime, self.graphY3, 'y', label = 'Thrust')
        plt.legend()
        plt.show()

    def showGraphPID(self):
        fig, (pltKp, pltKi, pltKd) = plt.subplots(3, sharex=True)
        pltKp.set(title = 'PID logger')

        #kp plot
        pltKp.grid(True)
        pltKp.set(ylabel = 'Kp')
        pltKp.plot(self.graphXrunTime, self.graphKp)

        #ki plot
        pltKi.grid(True)
        pltKi.set(ylabel = 'Ki')
        pltKi.plot(self.graphXrunTime, self.graphKi)

        #kd plot
        pltKd.grid(True)
        pltKd.set(ylabel = 'Kd')
        pltKd.plot(self.graphXrunTime, self.graphKd)
        plt.show()

    def runApp(self):
        Clock.schedule_interval(self.cycle, self.CYCLETIME)

    def build(self):
        return Simulation()

Program().run()
