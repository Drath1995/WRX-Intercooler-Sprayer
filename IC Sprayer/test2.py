from machine import Pin, SPI, ADC, Timer
import sh1106
import freesans72
import time
import math
import machine
import writer

# Define OLED parameters
spi = SPI(1, baudrate=1000000)
oled_width = 128
oled_height = 128 #just go with it, it works, I don't know why but im not willing to upset it at this point
dc = Pin(18)
res = Pin(5)
cs  = Pin(19)
#SCLK = Pin(14)
#SDA = Pin(13)
oled = sh1106.SH1106_SPI(oled_width, oled_height, spi, dc, res, cs, rotate = 180)


#Pot specific stuff
potentiometer_pin = 25
potentiometer_adc = ADC(Pin(potentiometer_pin))
potentiometer_adc.atten(ADC.ATTN_11DB)  # Set the attenuation level
previous_value = None
POT_MIN = 20
POT_MAX = 60

def map_pot_value(adc_value, in_min, in_max, out_min, out_max):
    return (adc_value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


# Main loop
while True:
    
    potentiometer_value = potentiometer_adc.read()
    # Map potentiometer ADC value to desired range
    mapped_pot_value = map_pot_value(potentiometer_value, 0, 4095, POT_MIN, POT_MAX)

    
    if potentiometer_value != previous_value:
        font_writer = writer.Writer(oled, freesans72)
        font_writer.set_textpos(20, -2)
        font_writer.printstring(str(mapped_pot_value))
        oled.show()
        time.sleep(0.1)
        previous_value = potentiometer_value
    time.sleep(0.1)