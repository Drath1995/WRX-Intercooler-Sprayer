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

#objects for the float sensor and pump
led = machine.Pin(2, machine.Pin.OUT)
switch = Pin(4, Pin.IN)


#Pot specific stuff
potentiometer_pin = 25
potentiometer_adc = ADC(Pin(potentiometer_pin))
potentiometer_adc.atten(ADC.ATTN_11DB)  # Set the attenuation level
POT_MIN = 20
POT_MAX = 81
def map_pot_value(adc_value, in_min, in_max, out_min, out_max):
    return (adc_value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


#thermistor
thermistor_pin = 35
thermistor_adc = ADC(Pin(thermistor_pin))
thermistor_adc.atten(ADC.ATTN_11DB)  # Set the attenuation level
beta = 4200
R = 50000

# last_value = potentiometer_adc.read()

def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

previous_value = None

# Initialize Timer objects
timer1 = machine.Timer(0) #this one refreshes the screen so its smoother
timer2 = machine.Timer(1) #this one handles the sensors and outputs


    
def timer1_callback(timer):
    
    # Read the voltage in microvolts and convert it to volts
    Vr = thermistor_adc.read_uv() / 1000000

    # Calculate the resistance of the thermistor based on the measured voltage
    Rt = R * Vr / (3.3 - Vr)

    # Use the beta parameter and resistance value to calculate the temperature in Kelvin
    temp = 1 / (((math.log(Rt / R)) / beta) + (1 / (273.15 + 25)))

    # Convert to Celsius
    C = math.floor(temp - 273.15)
    
    oled.show(0)
    font_writer = writer.Writer(oled, freesans72)
    font_writer.set_textpos(20, -2)
    font_writer.printstring(str(C))
    oled.show()
            
def timer2_callback(timer):
    # Read the voltage in microvolts and convert it to volts
    Vr = thermistor_adc.read_uv() / 1000000

    # Calculate the resistance of the thermistor based on the measured voltage
    Rt = R * Vr / (3.3 - Vr)

    # Use the beta parameter and resistance value to calculate the temperature in Kelvin
    temp = 1 / (((math.log(Rt / R)) / beta) + (1 / (273.15 + 25)))

    # Convert to Celsius
    C = math.floor(temp - 273.15)
    T = (temp - 273.15)
    
     # Read analog value from potentiometer
    potentiometer_value = potentiometer_adc.read()
    
    last_potentiometer_value = potentiometer_value
    
    # Map potentiometer ADC value to desired range
    mapped_pot_value = map_pot_value(potentiometer_value, 0, 4095, POT_MIN, POT_MAX)
    last_value = potentiometer_adc.read()
    previous_value = None
    last_change_time = time.ticks_ms()
    
    while True:
        potentiometer_value = potentiometer_adc.read()
        # Map potentiometer ADC value to desired range
        mapped_pot_value = map_pot_value(potentiometer_value, 0, 4095, POT_MIN, POT_MAX)

    
        if  previous_value is None or abs(potentiometer_value - previous_value) > 0.01 * previous_value:
            font_writer = writer.Writer(oled, freesans72)
            font_writer.set_textpos(20, -2)
            font_writer.printstring(str(mapped_pot_value))
            oled.show()
            previous_value = potentiometer_value
            
        elif time.ticks_diff(time.ticks_ms(), last_change_time) >= 5000:
            
            font_writer = writer.Writer(oled, freesans72)
            font_writer.set_textpos(20, -2)
            font_writer.printstring(str(C))
            print(T)
            oled.show()
            last_change_time = time.ticks_ms()
            
timer1.init(period=5000, mode=machine.Timer.PERIODIC, callback=timer1_callback)
timer2.init(period=1000, mode=machine.Timer.PERIODIC, callback=timer2_callback)
