import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--backward", action="store_true", help="direction of the motors")
parser.add_argument("--steps", type=int, help="number of steps to turn (One revolution = 2037)")
parser.add_argument("-d", "--double", nargs="*", type=int, help="IDs of Motors to double turn")
parser.add_argument("-s", "--single", nargs="*", type=int, help="IDs of Motors to single turn")
parser.add_argument("-m", "--micro", nargs="*", type=int, help="IDs of Motors to micro turn")
parser.add_argument("-t", "--throttle", nargs="*", type=int, help="Throttle of motors from 0 to 1")

args = parser.parse_args()

d_motor_set = set(args.double) if args.double else set()
s_motor_set = set(args.single) if args.single else set()
m_motor_set = set(args.micro) if args.micro else set()


# style = stepper.DOUBLE if args.double else stepper.SINGLE
direction = stepper.BACKWARD if args.backward else stepper.FORWARD

kit1 = MotorKit(address=0x60)
kit2 = MotorKit(address=0x61)
kit3 = MotorKit(address=0x62)
kit4 = MotorKit(address=0x63)

kit1.stepper1.throttle = args.throttle[0] if args.throttle else 1 
kit1.stepper2.throttle = args.throttle[1] if args.throttle and len(args.throttle) >= 2 else 1
kit2.stepper1.throttle = args.throttle[2] if args.throttle and len(args.throttle) >= 3 else 1
kit2.stepper2.throttle = args.throttle[3] if args.throttle and len(args.throttle) >= 4 else 1
kit3.stepper1.throttle = args.throttle[4] if args.throttle and len(args.throttle) >= 5 else 1
kit3.stepper2.throttle = args.throttle[5] if args.throttle and len(args.throttle) >= 6 else 1
kit4.stepper1.throttle = args.throttle[6] if args.throttle and len(args.throttle) >= 7 else 1
kit4.stepper2.throttle = args.throttle[7] if args.throttle and len(args.throttle) >= 8 else 1

def turn_stepper(motor_set, style):
    if 0 in motor_set:
        kit1.stepper1.onestep(direction=direction, style=style)
    if 1 in motor_set:
        kit1.stepper2.onestep(direction=direction, style=style)
    if 2 in motor_set:
        kit2.stepper1.onestep(direction=direction, style=style)
    if 3 in motor_set:
        kit2.stepper2.onestep(direction=direction, style=style)
    if 4 in motor_set:
        kit3.stepper1.onestep(direction=direction, style=style)
    if 5 in motor_set:
        kit3.stepper2.onestep(direction=direction, style=style)
    if 6 in motor_set:
        kit4.stepper1.onestep(direction=direction, style=style)
    if 7 in motor_set:
        kit4.stepper2.onestep(direction=direction, style=style)

def stepper_test():
    for i in range(770 if args.steps == None else args.steps):
        turn_stepper(s_motor_set, stepper.SINGLE)
        turn_stepper(d_motor_set, stepper.DOUBLE)
        turn_stepper(m_motor_set, stepper.MICROSTEP)
        
if __name__ == "__main__":
    stepper_test()
