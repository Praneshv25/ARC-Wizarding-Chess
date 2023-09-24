# Networking

### How to use:
- Clone the repo
- Install [Arduino Ide](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE) 
- Install [Arduino-pico core](https://github.com/earlephilhower/arduino-pico#Installation)
- Install [Arduino-esp8266 core](https://github.com/esp8266/Arduino#installing-with-boards-manager)
- Get [ESP8266 Programmer](https://www.amazon.com/Stemedu-ESP8266-Adapter-Programmer-Downloader/dp/B097SZMK2W/ref=sr_1_5?crid=U1AE1M3XHZB0&keywords=esp01%2Bprogrammer&qid=1694477509&sprefix=esp01%2Bprogramme%2Caps%2C109&sr=8-5&th=1)
- Upload [picoCode.ino](./picoCode/picoCode.ino) to your pico
- Upload [espCode.ino](./espCode/espCode.ino) to your esp8266 **IMPORTANT** You must change the ESP's ID number in the code to a unique value before uploading
- Connect the esp8266 to the pico as follows:
  - ESP8266 GND -> Pico GND
  - ESP8266 VCC -> Pico 3V3
  - ESP8266 EN (sometimes called CH_PD) -> Pico 3V3
  - ESP8266 RX -> Pico GP0
  - ESP8266 TX -> Pico GP1
  - ESP8266 GPIO-0 -> Status LED (optional)
- (For now, ignore the [TCPClient.cpp](./picoCode/TCPClient.cpp) and [constants.h](./picoCode/constants.h) files)
- Configure a static IP for your computer [Instructions for OSX](https://support.apple.com/guide/mac-help/use-dhcp-or-a-manual-ip-address-on-mac-mchlp2718/mac). For other OS's instructions can be found on google
  - The IP address should be `192.186.2.2`
- Run [PythonServer.py](./PythonServer.py) on your computer


### Troubleshooting:
- You must be in the basement of the Bechtel Design and Innovation Center
- The pico pi and esp8266 must be on (if the esp8266 has a status LED, it should be on)
- The pico pi and esp8266 must be connected to each other with a baud rate of 115200 (or any other baud rate, but they must match)
