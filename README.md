# Defender

## Software Architecture Description
The Defender software application is a RaspberryPi-embedded, multithreaded Python application that combines aspects of Functional and Object-Oriented Programming paradigms to achieve its key functions:
- **Communicate with External Nodes**
    - Send/receive external messages using DDS connectivity framework
    - Report system status
- **Detect Targets** 
    - Actuate stepper motor & TinyRad transceiver
    - Apply operator-commanded sensor configuration changes
    - Obtain target telemetry data for processing
- **Process Detections**
    - Set zone flags
    - Filter out spurious/irrelevant detections
    - Perform transformation to world coordinates
    - Populate Radar Detection Report message
- **Calibrate System**
    - Reset calibration-relevant configuration parameters
    - Apply manual or sensor-based methods to properly align Tactical Assembly and stepper motor
- **Perform IFF**
    - Send IFF Interrogation "signal" (message)
    - Process IFF Interrogation response
    - Populate IFF Response Report message

## Coding Standards

[Generic Python Style Guide](https://peps.python.org/pep-0008/)

### Functional versus OOP
In general, we should aim to apply the Functional Programming concept of **Pure Functions** as much as possible. We may run into some challenges here regarding keeping track of our internal state (radar state, IFF status, system health parameters, etc.), but some of the alternatives (e.g., the use of global state variables) run the risk of introducing race conditions between threads. In this particular example, we should attempt to pass the internal state information around, perhaps in alignment with the passing of any semaphores/mutexes we use to synchronize/control the execution of our software threads.

With that said, we may want to apply some aspects of OOP, perhaps passing an internal state Object around in our pure functions. In this particular example, we could additionally consider adding a variable to such an Object to keep track of which thread has the semaphore/mutex at any given moment (for help in debugging).

### Defender Naming Conventions (open to discussion):
- **Functions:** lowercase_with_underscores(args, more_args)
- **Constants:** UPPERCASE_WITH_UNDERSCORES, stored in a _constants.py_ file
- **Variables:** lowercase_with_underscores
- **Classes/Objects:** CamelCase

## Messages
| Message Name | Message Number | IN/OUT | External Node | Link |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| Radar Detection Report | | OUT | SAD-T | (these will be links to the DDS struct files)|
| IFF Interrogation Message | | OUT | Aggressor | |
| IFF Results Report | | OUT | SAD-T | |
| Radar State Change | | IN | SAD-T | |
| IFF Initiate Command | | IN | SAD-T | |
| UAV IFF Response Message | | IN | Aggressor | |

## Resources

### Logging
- Scenario #2 in this resource on [Python logging](https://medium.com/analytics-vidhya/the-python-logging-cheatsheet-easy-and-fast-way-to-get-logging-done-in-python-aa3cb99ecfe8#:~:text=The%20fastest%20way%20to%20get,it%20to%20the%20ROOT%20logger) describes an option for thread-safe logging in Python for a multithreaded application.

## Integration and Test TO-DOs
- Characterize angular behavior of TinyRad in Azimuth and Elevation
- Test TinyRad in a clear field with minimal targets

