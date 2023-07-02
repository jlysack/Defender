import time
import RPi.GPIO as GPIO
import sys
sys.path.insert(0, '/home/jlysack')
from RpiMotorLib import A4988Nema
import rti.connextdds as dds
import rti.asyncio
import asyncio #Need both
from interfaces import DDS

#Participant
participant = dds.DomainParticipant(domain_id=1)

#Topics
componentHealth_topic = dds.Topic(participant, "ComponentHealth", DDS.Metrics.ComponentHealth)
scanInstruction_topic = dds.Topic(participant, "ScanInstruction", DDS.Scanning.ScanInstruction)
scanResponse_topic = dds.Topic(participant, "ScanResponse", DDS.Scanning.ScanResponse)
RadarReport_topic = dds.Topic(participant, "RadarReport", DDS.Tracking.RadarReport)

#Define Writers
scanResponse_writer = dds.DataWriter(participant.implicit_publisher, scanResponse_topic)

#Readers
componentHealth_reader = dds.DataReader(participant.implicit_subscriber, componentHealth_topic)
scanInstruction_reader = dds.DataReader(participant.implicit_subscriber, scanInstruction_topic)
scanResponse_reader = dds.DataReader(participant.implicit_subscriber, scanResponse_topic)
RadarReport_reader = dds.DataReader(participant.implicit_subscriber, RadarReport_topic)

#Creating global data holders, these act as data pointers essentially, I wrote this code coming from a C++ background so excuse any weird-ness
componentHealth_ReceivedData = DDS.Metrics.ComponentHealth
scanInstruction_ReceivedData = DDS.Scanning.ScanInstruction
#scanInstruction_ReceivedData.radarSetting = 3
#scanInstruction_ReceivedData.manualScanSetting = 3

#Define message/data containers for sending
scanResponse_SendingData = DDS.Scanning.ScanResponse
scanResponse_SendingData.ZoneNumber = 2

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


currentStepPos = 0; #Assuming we configured it to 0 properly!
EZ1 = -99 #steps - left
EZ3 = 0 #steps - center
EZ2 = 98 #steps - right
allowRadarMovement = True #Flag to allow movement, once movement is complete we can change to false
allowRadarMovementAI = True # Flag to allow movement when in AI mode
allowNextStep = True
RadarReportReceived = False
flipFlop = False
timeout = 5;

#Functions that you just put the amount of steps required to move left/right
async def move_stepperLeft(stepsRequired):
    global currentStepPos
    global allowRadarMovement
    global allowRadarMovementAI
    global allowNextStep
    #global mymotortest
    #print("Move motor left", flush = True)
    #currentStepPos = currentStepPos - stepsRequired
    #allowRadarMovement = True
    #print(allowRadarMovement)
    mymotortest.motor_go(False,"1/8", stepsRequired,.005,False,.05)
    currentStepPos = currentStepPos - stepsRequired 
    sendScanResponse()
    print("motor scan response sent")
    time.sleep(1)
    allowRadarMovement = True
    allowRadarMovementAI = True
    allowNextStep = True
    print(f"AllowRadarMovement, expecting True: {allowRadarMovement}")
    print(currentStepPos)

async def move_stepperRight(stepsRequired):
    global currentStepPos
    global allowRadarMovement
    global allowRadarMovementAI
    global allowNextStep
    #global mymotortest
    print("Move motor right", flush = True)
    #currentStepPos = currentStepPos + stepsRequired
    #allowRadarMovement = True
    #print(allowRadarMovement)
    mymotortest.motor_go(True,"1/8", stepsRequired,.005,False,.05) 
    currentStepPos = currentStepPos + stepsRequired
    sendScanResponse()
    print("motor scan response set")
    time.sleep(1)
    allowRadarMovement = True
    allowRadarMovementAI = True
    allowNextStep = True
    print(f"AllowRadarMovement, expecting True: {allowRadarMovement}")
    print(currentStepPos)

def sendScanResponse():
    #global currentStepPos
    global scanResponse_SendingData
    #Check which zone and set the paramter
    if(currentStepPos==EZ1):
        scanResponse_SendingData.ZoneNumber = 1
    if(currentStepPos==EZ2):
        scanResponse_SendingData.ZoneNumber = 2
    if(currentStepPos==EZ3):
        scanResponse_SendingData.ZoneNumber = 3
    #Now send message
    scanResponse_writer.write(scanResponse_SendingData)

#Async updater for ComponentHealth
async def update_componentHealth():
    while True:    
        async for data in componentHealth_reader.take_data_async():
            global componentHealth_ReceivedData 
            componentHealth_ReceivedData = data

        await asyncio.sleep(0.5)

#Async updater for ScanInstruction
async def update_scanInstruction():
    while True:
        print("Hello, this is jordan scan intruction")
        async for data in scanInstruction_reader.take_data_async():
            global scanInstruction_ReceivedData 
            scanInstruction_ReceivedData = data
        
        await asyncio.sleep(0.5)

# Checks for detections
async def check_ValidDetections(timeout):
    global allowRadarMovementAI
    global RadarReportReceived
       
    while True:

        RadarReportReceived = False
        print(f"RadarReportRecevied, line152 Expecting False: {RadarReportReceived}")
        
        async for data in RadarReport_reader.take_data_async():
            RadarReportReceived = True
            print(f"RadarReportReceived, line 156 expecting True: {RadarReportReceived}")
            #start_time = time.time()
            
            #while not RadarReportReceived and (time.time() - start_time) < timeout:
                #print("WTF")

        if RadarReportReceived:
            allowRadarMovementAI = False
            print(f"AllowRadarMovementAI, line164 expecting False: {allowRadarMovementAI}")
            print(allowRadarMovementAI)
        else:
            allowRadarMovementAI = True
            print(f"AllowRadarMovementAI, line168 expecting True: {allowRadarMovementAI}")
                
        RadarReportReceived = False

        await asyncio.sleep(1)


#Custom async coroutines           
async def update_motorLogic():
    while True:
        #print("Hello, updating motor logic....")
        try:
            global allowRadarMovement
            global allowRadarMovementAI
            global allowNextStep
            global flipFlop

            # Radar/Stepper AI Mode Code
            if scanInstruction_ReceivedData.radarSetting == 0:
                if scanInstruction_ReceivedData.manualScanSetting == 0:
                    
                    # Block1 #
                    if (allowRadarMovementAI and allowNextStep):
                        print(f"flipFlop inside radarmovementAI: {flipFlop}")
                        if (currentStepPos == EZ1): #If we are looking at zone 1 already then we need to move right
                            allowNextStep = False
                            await move_stepperRight(abs(EZ1))
                            await asyncio.sleep(2)
                            print("moving right")
                            print(flipFlop)

                        if (currentStepPos == EZ2): #If we were looking at zone 2, then move left
                            allowNextStep = False
                            await move_stepperLeft(EZ2)
                            await asyncio.sleep(2)
                            print("moving left")
                            print(flipFlop)

                        if (currentStepPos == EZ3 and flipFlop == True):
                            allowNextStep = False
                            flipFlop = False
                            await move_stepperLeft(abs(EZ1))
                            await asyncio.sleep(2)
                            print("moving left")
                            print(flipFlop)

                        if (currentStepPos == EZ3 and flipFlop == False):
                            allowNextStep = False
                            flipFlop = True
                            await move_stepperRight(EZ2)
                            await asyncio.sleep(2)
                            print("moving Right")
                            print(flipFlop)


            # Radar/Stepper Manual mode Code
            if scanInstruction_ReceivedData.radarSetting == 1: 
                #Could either have all motorlogic in 1 function like this or make routines for every "setting" - discuss with wider team
                if scanInstruction_ReceivedData.manualScanSetting == 0:
                    # Block1 #

                    print(flipFlop)
                    if (allowRadarMovement):
                        print(flipFlop)
                        if (currentStepPos == EZ1): #If we are looking at zone 1 already then we need to move right
                            allowRadarMovement = False
                            await move_stepperRight(abs(EZ1))
                            await asyncio.sleep(1)
                            print("moving right")
                            print(flipFlop)

                        if (currentStepPos == EZ2): #If we were looking at zone 2, then move left
                            allowRadarMovement = False
                            await move_stepperLeft(EZ2)
                            await asyncio.sleep(1)
                            print("moving left")
                            print(flipFlop)

                        if (currentStepPos == EZ3 and flipFlop == True):
                            allowRadarMovement = False
                            flipFlop = False
                            await move_stepperLeft(abs(EZ1))
                            await asyncio.sleep(1)
                            print("moving left")
                            print(flipFlop)

                        if (currentStepPos == EZ3 and flipFlop == False):
                            allowRadarMovement = False
                            flipFlop = True
                            await move_stepperRight(EZ2)
                            await asyncio.sleep(1)
                            print("moving Right")
                            print(flipFlop)

                        
                if scanInstruction_ReceivedData.manualScanSetting == 1:
                    #print("Instructed to scan zone 1")   
                    if (allowRadarMovement):
                        #print("Radar movement allowed, attempting movement")
                        #allowRadarMovement = False #Locking radar movement
                        #print(allowRadarMovement)
                        if (currentStepPos != EZ1): #If we are not looking at zone 1 already then we need to move left
                            allowRadarMovement = False
                            await move_stepperLeft((abs(EZ1) + currentStepPos))
                            print("moving left")

                if scanInstruction_ReceivedData.manualScanSetting == 2:
                    #print("Instructed to scan zone 2")
                    if (allowRadarMovement):
                        #print("Radar movement allowed, attempting movement")
                        #allowRadarMovement = False #Locking radar movement
                        #print(allowRadarMovement)
                        if (currentStepPos!=EZ2): #If we are not lookling at zone 2 already then we need to move right
                            allowRadarMovement = False
                            await move_stepperRight((abs(currentStepPos) + EZ2))
                            print("moving right")
                
                if scanInstruction_ReceivedData.manualScanSetting == 3:
                    #print("Instructed to scan zone 3")
                    if (allowRadarMovement):
                        #print("Radar movement allowed, attempting movement")
                        #allowRadarMovement = False #Locking radar movement
                        #print(allowRadarMovement)
                        if (currentStepPos==EZ1): #If we were looking at zone, 1 then move right
                            allowRadarMovement = False
                            await move_stepperRight(abs(EZ1))
                            print("moving right")
                        if (currentStepPos==EZ2): #If we were looking at zone, 2 then move left
                            allowRadarMovement = False
                            await move_stepperLeft(EZ2)
                            print("moving left")
                    
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error in update_motorLogic(): {e}")


# Define the ma	in loop coroutine
async def main_loop():
    #Tell the main thread to use the global variables
    global componentHealth_ReceivedData 
    global scanInstruction_ReceivedData 
    global allowRadarMovement

    while True:
        #print("Main loop")
        #print(currentStepPos)
        #print(allowRadarMovement)
        #print(componentHealth_ReceivedData)     
        #print(scanInstruction_ReceivedData)

        #await update_motorLogic() #Not sure the impact of this await keyword
        #await update_componentHealth()
        #await update_scanInstruction()
        await asyncio.sleep(0.5)  # Simulating some work and slow thread so we can read it
     
        #print("Test, after Main loop sleep")


# Create and run the event loop
#loop = asyncio.get_event_loop()
#Add the async tasks to the task list
#tasks = asyncio.gather(main_loop(),
#update_componentHealth(),
#update_scanInstruction(),
#update_motorLogic()
#)
#Now loop the task list
#loop.run_until_complete(tasks)


async def run_event_loop():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(main_loop()),
        asyncio.ensure_future(update_componentHealth()),
        asyncio.ensure_future(update_scanInstruction()),
        asyncio.ensure_future(update_motorLogic()),
        asyncio.ensure_future(check_ValidDetections(timeout))
    ]
    await asyncio.gather(*tasks)


asyncio.run(run_event_loop())
