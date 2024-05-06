from machine import Pin, SPI, ADC
import sh1106
import freesans72
import freesans20
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
POT_MAX = 80
def map_pot_value(adc_value, in_min, in_max, out_min, out_max):
    return (adc_value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
previous_value = None
last_change_time = time.ticks_ms()

#thermistor
thermistor_pin = 35
thermistor_adc = ADC(Pin(thermistor_pin))
thermistor_adc.atten(ADC.ATTN_11DB)  # Set the attenuation level
beta = 4200
R = 50000

# Initialize Timer objects
timer1 = machine.Timer(0) #handles the float sensor and pump
timer2 = machine.Timer(1) #this one handles the screen and pot




def timer1_callback(timer):
  
    # Read the voltage in microvolts and convert it to volts
    Vr = thermistor_adc.read_uv() / 1000000

    # Calculate the resistance of the thermistor based on the measured voltage
    Rt = R * Vr / (3.3 - Vr)

    # Use the beta parameter and resistance value to calculate the temperature in Kelvin
    temp = 1 / (((math.log(Rt / R)) / beta) + (1 / (273.15 + 25)))

    # Convert to Celsius
    C = math.floor(temp - 273.15)
    potentiometer_value = potentiometer_adc.read()
    mapped_pot_value = map_pot_value(potentiometer_value, 0, 4095, POT_MIN, POT_MAX)
    
    if not switch.value() and C > mapped_pot_value:
        led.value(1)
    else:
        led.value(0)

def timer2_callback(timer):
    global previous_value, last_change_time
    
     # Read analog value from potentiometer
    potentiometer_value = potentiometer_adc.read()
    last_potentiometer_value = potentiometer_value
    
    # Map potentiometer ADC value to desired range
    mapped_pot_value = map_pot_value(potentiometer_value, 0, 4095, POT_MIN, POT_MAX)
    last_value = potentiometer_adc.read()
    #last_change_time = time.ticks_ms()
    # Read the voltage in microvolts and convert it to volts
    Vr = thermistor_adc.read_uv() / 1000000

    # Calculate the resistance of the thermistor based on the measured voltage
    Rt = R * Vr / (3.3 - Vr)

    # Use the beta parameter and resistance value to calculate the temperature in Kelvin
    temp = 1 / (((math.log(Rt / R)) / beta) + (1 / (273.15 + 25)))

    # Convert to Celsius
    C = math.floor(temp - 273.15)
    T = (temp - 273.15)
    
    if  previous_value is None or abs(potentiometer_value - previous_value) > 0.01 * previous_value:
        font_writer = writer.Writer(oled, freesans72)
        font_writer.set_textpos(20, -2)
        font_writer.printstring(str(mapped_pot_value))
        oled.show()
        print("Target Temp:", mapped_pot_value)
        previous_value = potentiometer_value
        
    elif time.ticks_diff(time.ticks_ms(), last_change_time) >= 5000:
        
        font_writer = writer.Writer(oled, freesans72)
        font_writer.set_textpos(20, -2)
        font_writer.printstring(str(C))
        #font_writer.printstring("20")
        print("temp:", C)
        oled.show()
        last_change_time = time.ticks_ms()

            
timer1.init(period=1000, mode=machine.Timer.PERIODIC, callback=timer1_callback)
timer2.init(period=500, mode=machine.Timer.PERIODIC, callback=timer2_callback)