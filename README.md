# Dremel 3D Printer Integration
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration with Dremel 3D Printer (models 3D20, 3D40 and 3D45).

### Installation
1. Install this repository via HACS by adding this repository as a custom repository, or by copying the contents of the `custom_components` folder into your `config/custom_components`.
2. Restart your Home Assistant.
3. Go to Integrations, Add Integration, and look for Dremel 3D Printer.
4. Insert the host IP of your Dremel 3D Idea Builder Printer.

## Components

### Sensors

#### Chamber Temperature
* Shows the current temperature inside the 3D printer chamber.

#### Extruder Temperature
* Shows the current temperature of the filament extruder.

#### Platform Temperature
* Shows the current temperature of the base platform.

#### Progress
* Shows the progress from 0% to 100% of the current printing job.

#### Job Phase
##### State
Shows the current status of the 3D printer:
* Idle
* Preparing
* Building
* Abort
* Completed
* Pausing
* Paused
* Resuming

##### Attributes
1. Door Open
2. Chamber Temperature
3. Elapsed Time
4. Remaining Time
5. Estimated Total Time
6. Extruder Temperature
7. Extruder Target Temperature
8. Platform Temperature
9. Platform Target Temperature
10. Fan Speed
11. Filament
12. Job Status
13. Job Name
14. Progress
15. Current Status
16. Network Build

### Binary Sensors

#### DREMEL (3D20/3D40/3D45)
##### State
* Running
* Not Running

##### Attributes
1. Host
2. API Version
3. Connection Type
4. Ethernet IP
5. Firmware Version
6. Machine Type
7. Model
8. SN
9. Title
10. Wifi IP
11. Available Storage
12. Extruder Max Temperature
13. Platform Max Temperature
14. Hours Used

### Camera

#### Only available for model 3D45

### Buttons

#### Pause Job
Pauses the printing job.

#### Resume Job
Resumes the paused printing job.

#### Stop Job
Cancels the printing job.

### Services
