import board
import busio
import adafruit_ssd1306
import digitalio

# default target temperature, in F
DEFAULT_TARGET_TEMP = 26
# min/max target temperatures
MIN_TARGET_TEMP = 18
MAX_TARGET_TEMP = 34

# pin mappings for the buttons
START_BUTTON_PIN = board.D5
UP_BUTTON_PIN = board.D9
DOWN_BUTTON_PIN = board.D6

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


# set up I2C
i2c = busio.I2C(board.SCL, board.SDA)


# set up the OLED
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)


# set up the motor
# whether the slushie motor is currently running
running = False


# set up the temperature sensor
target_temp = DEFAULT_TARGET_TEMP


# update the display with current state
def update_display():
    oled.fill(0)
    motor_text = "Running"
    if not running:
        motor_text = "Stopped"
    oled.text("{}".format(motor_text),0,0,1)
    oled.text("Target: {}F".format(target_temp),0,10,1)
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
