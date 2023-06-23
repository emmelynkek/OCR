import time
import math
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

down = True

REVOLUTION = 2038
MOTOR_STEPS = 6
ELEVATOR_STEPS = 170
MOTOR_COUNT = 3

def send_motor_instructions(motor_instructions, kit1, kit2, kit3, kit4):
  global down
  print(f"Motor Instructions: {motor_instructions}")

  motors_executed_count = 0
  while motors_executed_count != MOTOR_COUNT:
    
    print(motor_instructions)
    motors_done_count = 0

    while motors_done_count != MOTOR_COUNT:
      motors_done_count = 0
      motors_to_turn = {
        0: False,
        1: False,
        2: False,
        3: False,
        4: False,
        5: False,
        6: False
      }

      for i in range(len(motor_instructions)):
        motor_instruction = motor_instructions[i]

        # For motor to stop turning and wait for elevator
        if motor_instruction == "" or (down and motor_instruction[0] == "1") or (not down and motor_instruction[0] == "0"):
          motors_done_count += 1
          continue

        # For motor to turn when elevator is in the right order
        if down and motor_instruction[0] == "0":
          motors_to_turn[i] = True
          motor_instructions[i] = motor_instruction[1:]
        if not down and motor_instruction[0] == "1":
          motors_to_turn[i] = True
          motor_instructions[i] = motor_instruction[1:]

        # Determine number of motors that have finished turning
        if motor_instructions[i] == "":
          motors_executed_count += 1

      if not down: # Edit elevator microstepping here
        turn_elevator_motor(kit4, style=stepper.MICROSTEP)

      turn_motors(motors_to_turn, kit1, kit2, kit3)

    if down:
      print("Raising elevator")
      turn_elevator_motor(kit4, direction=stepper.BACKWARD)
      down = False
      print("Elevator Raised")
    else:
      print("Lowering elevator")
      turn_elevator_motor(kit4)
      down = True
      print("Elevator Lowered")

  print("End")

def turn_elevator_motor(kit4, direction=stepper.FORWARD, style=stepper.SINGLE):
  for i in range(ELEVATOR_STEPS):
    kit4.stepper2.onestep(direction=direction, style=style) # Edit elevator motors here
    kit4.stepper1.onestep(direction=direction, style=style)

def turn_motors(motor_ids, kit1, kit2, kit3):
  for i in range(math.ceil(REVOLUTION/MOTOR_STEPS)):
    # Map motor id 0 to A0 M1
    if (motor_ids[0]):
      kit1.stepper1.onestep()

    # Map motor id 1 to A0 M3
    if (motor_ids[1]):
      kit1.stepper2.onestep()

    # Map motor id 2 to A1 M1
    if (motor_ids[2]):
      kit2.stepper1.onestep()

    # # Uncomment this if motor ids 3, 4, 5 are used
    # if (motor_ids[3]):
    #   kit2.stepper2.onestep()
    # if (motor_ids[4]):
    #   kit3.stepper1.onestep()
    # if (motor_ids[5]):
    #   kit3.stepper2.onestep()

if __name__ == "__main__":
  motor_instructions = ['001010', '001110', '011010']
  kit1 = MotorKit(address=0x60)
  kit2 = MotorKit(address=0x61)
  kit3 = MotorKit(address=0x62)
  kit4 = MotorKit(address=0x63)

  send_motor_instructions(motor_instructions, kit1, kit2, kit3, kit4)
  exit()
