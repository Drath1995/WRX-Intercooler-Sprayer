from machine import Pin, SPI, ADC
import sh1106
import freesans72
import writer
import time
import math
import machine
import neopixel

#Pins for the oled
spi = SPI(1, baudrate=1000000)
oled_width = 128
oled_height = 128 #just go with it, it works, I don't know why but im not willing to upset it at this point
dc = Pin(18)
res = Pin(5)
cs  = Pin(19)
#SCLK = Pin(14)
#SDA = Pin(13)
oled = sh1106.SH1106_SPI(oled_width, oled_height, spi, dc, res, cs, rotate = 180)

#objects for the float sensor, pot and thermistor
thermistor = ADC(Pin(35, Pin.IN))
led = machine.Pin(2, machine.Pin.OUT)
switch = Pin(4, Pin.IN)
np = neopixel.NeoPixel(machine.Pin(16), 1)

#Math for the temp sensor
beta = 4200
R = 50000

# Initialize Timer objects
timer1 = machine.Timer(0) #this one refreshes the screen so its smoother
timer2 = machine.Timer(1) #this one handles the sensors and outputs


    
def timer1_callback(timer):

    # Read the voltage in microvolts and convert it to volts
    Vr = thermistor.read_uv() / 1000000

    # Calculate the resistance of the thermistor based on the measured voltage
    Rt = R * Vr / (3.3 - Vr)

    # Use the beta parameter and resistance value to calculate the temperature in Kelvin
    temp = 1 / (((math.log(Rt / R)) / beta) + (1 / (273.15 + 25)))

    # Convert to Celsius
    C = math.floor(temp - 273.15)
        
    #oled.fill(0)
    font_writer = writer.Writer(oled, freesans72)
    font_writer.set_textpos(20, -2)
    font_writer.printstring(str(C))        
    oled.show()
            
            
def timer2_callback(timer):
     # Read the voltage in microvolts and convert it to volts
    Vr = thermistor.read_uv() / 1000000

    # Calculate the resistance of the thermistor based on the measured voltage
    Rt = R * Vr / (3.3 - Vr)

    # Use the beta parameter and resistance value to calculate the temperature in Kelvin
    temp = 1 / (((math.log(Rt / R)) / beta) + (1 / (273.15 + 25)))

    # Convert to Celsius
    C = math.floor(temp - 273.15)
        
    if not switch.value():
        led.value(1)
    else:
        led.value(0)
        
timer1.init(period=5000, mode=machine.Timer.PERIODIC, callback=timer1_callback)
timer2.init(period=100, mode=machine.Timer.PERIODIC, callback=timer2_callback)
