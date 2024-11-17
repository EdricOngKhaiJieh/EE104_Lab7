
ps_gpio_design = Overlay("./ps_gpio_kv260.bit")
from pynq import GPIO

# GPIO setup
floor_input1 = GPIO(GPIO.get_gpio_pin(1), 'in')  # Encodes Floors 1 and 2 orange is 1
floor_input2 = GPIO(GPIO.get_gpio_pin(2), 'in')  # Encodes Floors 3 and 4 green is 2 
sos_request = GPIO(GPIO.get_gpio_pin(7), 'in')  # Emergency button white is 7
motor = GPIO(GPIO.get_gpio_pin(4), 'out')  # Up/Down right most LED
door_led = GPIO(GPIO.get_gpio_pin(3), 'out')  # Door left most
move = GPIO(GPIO.get_gpio_pin(0), 'out')  # Start/Stop middle
seg_1 = GPIO(GPIO.get_gpio_pin(5), 'out')  # Floor LSB left red
seg_2 = GPIO(GPIO.get_gpio_pin(6), 'out')  # Floor MSB

import time

# State variables
current_floor = 1
requests = [False, False, False, False]
emergency_request = False

# Update LEDs for the current floor
def set_floor_leds(floor):
    seg_1.write(floor & 0b01)  # LSB
    seg_2.write((floor & 0b10) >> 1)  # MSB

# Handle door operation
def door_operation(action):
    door_led.write(action)
    print("Door opening..." if action else "Door closing...")
    time.sleep(2)

# Handle elevator movement
def move_elevator(target_floor):
    global current_floor
    direction = 1 if target_floor > current_floor else 0
    motor.write(direction)
    print("Moving up..." if direction else "Moving down...")

    steps = abs(target_floor - current_floor) * 100
    for step in range(steps):
        move.write(1)
        if 10 < step < steps - 10:
            time.sleep(0.1)
            seg_1.write(1)
            print("Moving at fast speed")
        else:
            time.sleep(0.05)
            seg_1.write(0)
            print("Moving at slow speed")
    
    move.write(0)
    motor.write(0)
    current_floor = target_floor
    set_floor_leds(current_floor - 1)
    print(f"Reached Floor {current_floor}.")

# Handle emergency
def handle_emergency():
    global emergency_request
    print("Emergency! Moving to Floor 1.")
    move_elevator(1)
    door_operation(1)
    door_operation(0)


# Clear all requests
def clear_requests():
    global requests
    requests = [False, False, False, False]

# Decode requests from input pins
def decode_requests():
    global requests
    lsb = floor_input1.read()
    msb = floor_input2.read()

    # Reset requests
    clear_requests()

    if not msb and not lsb:
        requests[0] = True  # Floor 1
    elif lsb and not msb:
        requests[1] = True  # Floor 2
    elif not lsb and msb:
        requests[2] = True  # Floor 3
    elif lsb and msb:
        requests[3] = True  # Floor 4

# Main loop
while True:
    emergency_request = sos_request.read()

    # Emergency handling
    if emergency_request and current_floor != 1 :
        handle_emergency()
        emergency_request = False
        clear_requests()
        continue

    # Decode floor requests
    decode_requests()

    # Process each request
    for i, request in enumerate(requests):
        emergency_request = sos_request.read()
        if request and current_floor != i + 1 and emergency_request != 1:
            print(f"Handling request for Floor {i + 1}...")
            move_elevator(i + 1)
            time.sleep(0.5)
            door_operation(1)
            door_operation(0)
            requests[i] = False  # Clear the processed request
    
    # Idle state
    if not any(requests):
        print(f"Elevator idle at Floor {current_floor}.")
        motor.write(0)
        time.sleep(1)
