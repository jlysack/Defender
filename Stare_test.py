import time
import RPi.GPIO as GPIO

import sys
sys.path.insert(0, '/home/jlysack')
from RpiMotorLib import A4988Nema
#DDS imports
import rti.connextdds as dds
from interfaces import DDS

# Production installed library import
# from RpiMotorLib import RpiMotorLib

def main():
	# ====== Tests for motor ======

	# Microstep Resolution MS1-MS3 -> GPIO Pin , can be set to (-1,-1,-1) to turn off
    GPIO_pins = (25, 8, 7)
    direction = 12  # Direction -> GPIO Pin
    step = 1  # Step -> GPIO Pin

    # Declare an named instance of class pass GPIO-PINs
    # (self, direction_pin, step_pin, mode_pins , motor_type):
    mymotortest = A4988Nema(direction, step, GPIO_pins, "A4988")

    # (1) clockwise, type = bool, default = False, help = "Turn stepper counterclockwise"
    # (2) steptype, type = string, default = Full,  (Full, Half, 1 / 4, 1 / 8, 1 / 16)
    # (3) steps, type = int, default = 200, 200 is 360deg rev in Full mode.
    # (4) stepdelay, type = float, default = 0.05
    # (5) verbose, type = bool, default = False, help = "Write pin actions",
    # (6) initdelay, type = float, default = 1mS, help = Intial delay after GPIO pins initialized but before motor is moved.

# ====================== section A ===================

# ====================== DDS setup ===================
    #Define DDS participant, hardcoded domain 1, will need to agree a domain for all systems to run on during demo. Eventually move to configuration file.
    participant = dds.DomainParticipant(domain_id=1)

    #Define topics
    scanResponse_topic = dds.Topic(participant, "ScanResponse", DDS.Scanning.ScanResponse)

    #Define Writers
    scanResponse_writer = dds.DataWriter(participant.implicit_publisher, scanResponse_topic)

    #Define Readers 
    #Add reading later, focus on publishing for a first test

    #Define message/data containers
    scanResponse_data = DDS.Scanning.ScanResponse


# ====================== DDS setup complete ===================

    # assuming calibration step is complete, which means that stepper is pointing at EZ 3 to start
    past_ez = "EZ3"
    #Set ScanResponse value and write the message, this sends it to the RTI
    scanResponse_data.ZoneNumber = 3;
    scanResponse_writer.write(scanResponse_data)

    print("Stepper motor currently pointing at EZ 3")

    # State select (DDS message input needed)
    print("Search or Stare state? (1 = Search, 2 = Stare)")
    mode_select = input()

    # Search State Selected
    if mode_select == "1":
        print("Search State Test\n")
        #Think about a better method for this past_ez past_ez2 situation, Jake thinks making use of an Array to compare previous data
        past_ez = "3"
        past_ez2 = "2"
        try:
            while True: #Create a flag here, certain KeyboardInterrupt should set the flag to false and cause it to exit the loop - Jordan
                # counterclockwise, from EZ3 to EZ1
                if past_ez == "3" and past_ez2 == "2":
                    print("Pivoting to EZ1")
                    mymotortest.motor_go(False,"1/8",100,.005,False,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 1;
                    scanResponse_writer.write(scanResponse_data)
                    time.sleep(2)
                    past_ez2 = "3"
                    past_ez = "1"
                # clockwise, from EZ1 to EZ3
                elif past_ez == "1" and past_ez2 == "3":
                    print("Pivoting to EZ3")
                    mymotortest.motor_go(True,"1/8",100,.005,False,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 3;
                    scanResponse_writer.write(scanResponse_data)
                    time.sleep(2)
                    past_ez2 = "1"
                    past_ez = "3"
                # clockwise, from EZ3 to EZ2
                elif past_ez == "3" and past_ez2 == "1":
                    print("Pivoting to EZ2")
                    mymotortest.motor_go(True,"1/8",100,.005,False,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 2;
                    scanResponse_writer.write(scanResponse_data)
                    time.sleep(2)
                    past_ez2 = "3"
                    past_ez = "2"
                # counterclockwise, from EZ2 to EZ3
                elif past_ez == "2" and past_ez2 == "3":
                    print("Pivoting to EZ3")
                    mymotortest.motor_go(False,"1/8",100,.005,False,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 3;
                    scanResponse_writer.write(scanResponse_data)
                    time.sleep(2)
                    past_ez2 = "2"
                    past_ez = "3"
                else:
                    print("Error1")
        # exit loop via control+C
        except KeyboardInterrupt:
            pass
    
    # Stare state selected
    elif mode_select == "2":
        print("Which Zone would you like to point to? (1 or 2)")
        future_ez = input()

        if future_ez=="1":
            print("Pivoting to EZ1")
            mymotortest.motor_go(False, "1/8", 100, .005, True, .05)
            time.sleep(1)
             #Set ScanResponse value and write the message, this sends it to the RTI
            scanResponse_data.ZoneNumber = 1;
            scanResponse_writer.write(scanResponse_data)

            past_ez = "1"
            print("Stepper is pointing at EZ1")
        elif future_ez == "2":
            print("Pivoting to EZ2")
            mymotortest.motor_go(True, "1/8", 100, .005, True, .05)
            time.sleep(1)
            #Set ScanResponse value and write the message, this sends it to the RTI
            scanResponse_data.ZoneNumber = 2;
            scanResponse_writer.write(scanResponse_data)
            past_ez = "2"
            print("Stepper is pointing at EZ2")
        else:
            print("Invalid entry")

        print("Would you like to continue? (y or n)")
        cont = input()

        while(cont=="y"):
            print("Which zone would you like to point to? (1, 2, or 3)")
            future_ez = input()
            if future_ez=="1":
                if past_ez=="2":
                    print("Pivoting to EZ1")
                    mymotortest.motor_go(False,"1/8",200,.005,True,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 1;
                    scanResponse_writer.write(scanResponse_data)
                    past_ez = "1"
                    print("Stepper motor is pointing at EZ")
                elif past_ez=="3":
                    print("Pivoting to EZ1")
                    mymotortest.motor_go(False,"1/8",100,.005,True,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 1;
                    scanResponse_writer.write(scanResponse_data)
                    past_ez = "1"
                    print("Stepper motor is pointing at EZ1")
                else:
                    print("Stepper motor is already pointing at EZ1")
            elif future_ez=="2":
                if past_ez=="1":
                    print("Pivoting to EZ2")
                    mymotortest.motor_go(True,"1/8",200,.005,True,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 2;
                    scanResponse_writer.write(scanResponse_data)
                    past_ez = "2"
                    print("Stepper motor is pointing at EZ2")
                elif past_ez=="3":
                    print("Pivoting to EZ2")
                    mymotortest.motor_go(True,"1/8",100,.005,True,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 2;
                    scanResponse_writer.write(scanResponse_data)
                    past_ez = "2"
                    print("Stepper motor is pointing at EZ2")
                else:
                    print("Stepper motor is already pointing at EZ2")
            elif future_ez=="3":
                if past_ez=="1":
                    print("Pivoting to EZ3")
                    mymotortest.motor_go(True,"1/8",100,.005,True,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 3;
                    scanResponse_writer.write(scanResponse_data)
                    past_ez = "3"
                    print("Stepper motor is pointing at EZ3")
                elif past_ez=="2":
                    print("Pivoting to EZ2")
                    mymotortest.motor_go(False,"1/8",100,.005,True,.05)
                    time.sleep(1)
                    #Set ScanResponse value and write the message, this sends it to the RTI
                    scanResponse_data.ZoneNumber = 3;
                    scanResponse_writer.write(scanResponse_data)
                    past_ez = "3"
                    print("Stepper motor is pointing at EZ3")
                else:
                    print("Stepper motor is already pointing at EZ3")
            else:
                print("Invalid Input\n")

            print("Would you like to continue? (y or n)")
            cont=input()
    else:
        print("Invalid entry")
	
# ===================MAIN===============================

if __name__ == '__main__':
    print("TEST START")
    main()
    GPIO.cleanup()
    print("TEST END")
    exit()

    # =====================END===============================
