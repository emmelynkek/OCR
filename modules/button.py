from gpiozero import Button

button_pin = 2

def button_pressed():
    print("Pressed")

button = Button(button_pin)
button.when_pressed = button_pressed

while True:
    pass
