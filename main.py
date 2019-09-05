import board
import busio
import digitalio
import adafruit_ssd1306
import adafruit_mlx90614
from analogio import AnalogIn

# default target temperature, in F
DEFAULT_TARGET_TEMP = 26
# min/max target temperatures
MIN_TARGET_TEMP = 18
MAX_TARGET_TEMP = 34

# pin mappings for the buttons
START_BUTTON_PIN = board.D5
UP_BUTTON_PIN = board.D9
DOWN_BUTTON_PIN = board.D6


# displays an error message
def error(component,msg):
    oled.fill(0)
    component_msg = "{} error".format(component)
    oled.text(component_msg,0,0,1)
    print(component_msg)
    oled.text(msg,0,10,1)
    print(msg)
    oled.show()


# set up all the OLED featherwing buttons
# create button objects
up_button = digitalio.DigitalInOut(UP_BUTTON_PIN)
down_button = digitalio.DigitalInOut(DOWN_BUTTON_PIN)
start_button = digitalio.DigitalInOut(START_BUTTON_PIN)

# set pins to input mode
up_button.direction = digitalio.Direction.INPUT
down_button.direction = digitalio.Direction.INPUT
start_button.direction = digitalio.Direction.INPUT

# make sure all the button pins have a pullup
up_button.pull = digitalio.Pull.UP
down_button.pull = digitalio.Pull.UP
start_button.pull = digitalio.Pull.UP

# initialize button states to current button values
last_up_button_state = up_button.value
last_down_button_state = down_button.value
last_start_button_state = start_button.value


# initialize battery voltage pin
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)


# set up I2C
# the mlx90614 must be run at 100k [normal speed]
# i2c default mode is is 400k [full speed]
# the mlx90614 will not appear at the default 400k speed
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)


# set up the OLED
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)


# set up the motor
# whether the slushie motor is currently running
running = False


# set up the temperature sensor
target_temp = DEFAULT_TARGET_TEMP
# initialize the mlx device
try:
    mlx = adafruit_mlx90614.MLX90614(i2c)
except Exception as e:
    # something went wrong; print an error and halt
    if hasattr(e,'message'):
        msg = e.message
    else:
        msg = str(e)
        
    error("temp sens",msg)
    while True:
        pass

# read battery voltage
def get_voltage():
    return (vbat_voltage.value * 3.3) / 65536 * 2


# convert temperature from C to F
def c_to_f(temp_c):
    return temp_c * 1.8 + 32

# update the display with current state
def update_display():
    oled.fill(0)
    motor_text = "Running"
    if not running:
        motor_text = "Stopped"
    battery_voltage = get_voltage()
    oled.text("{}  Batt: {:.1f}V".format(motor_text,battery_voltage),0,0,1)
    oled.text("Target: {}F".format(target_temp),0,10,1)
    oled.text("Temp: {:.0f}F  Amb: {:.0f}F".format(c_to_f(mlx.object_temperature),c_to_f(mlx.ambient_temperature)),0,20,1)
    oled.show()

# determine if a button is being pressed
def button_pressed(current_state,last_state):
    return current_state and not last_state

update_display()

while True:
    update_needed = False
    
    up_button_state = up_button.value
    down_button_state = down_button.value
    start_button_state = start_button.value

    if button_pressed(start_button_state,last_start_button_state):
        running = not running
        update_needed = True

    elif button_pressed(up_button_state,last_up_button_state):
        target_temp+=1
        if target_temp > MAX_TARGET_TEMP:
            target_temp = MAX_TARGET_TEMP
        update_needed = True
        
    elif button_pressed(down_button_state,last_down_button_state):
        target_temp-=1
        if target_temp < MIN_TARGET_TEMP:
            target_temp = MIN_TARGET_TEMP
        update_needed = True
        
    if update_needed:
        update_display()

    last_up_button_state = up_button_state
    last_down_button_state = down_button_state
    last_start_button_state = start_button_state
