

x = "LOW"
y = "LOW"


# Loop for modifying GPIO outputs
for i in range(4):  # Replace '4' with the desired number of iterations
    GPIO.output(27, GPIO.HIGH)
    GPIO.output(17, GPIO.HIGH)
    subprocess.call(["irsend", "SEND_ONCE", "Technics_EUR646497", "KEY_POWER"])

    #x = "HIGH"
    #y = "HIGH"

    #print(i)
    #print(x, y)

    # Delay or perform any other operations here if needed
    GPIO.output(27, GPIO.LOW)
    GPIO.output(17, GPIO.HIGH if i == 2 else GPIO.LOW)

    x = "LOW" if i == 0 or i == 2 else "HIGH"
    y = "LOW" if i == 1 or i == 2 else "HIGH"

    if i == 2:
        x = "HIGH"
        y = "HIGH"
    
