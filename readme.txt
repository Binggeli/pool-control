Headless setup of raspbian stretch:
- create emtpy file "ssh" in the volume "boot":
  	 touch /Volumes/boot/ssh
- create wpa config file "wpa_supplicant.conf" in the volume "boot":

country=CH
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="Abahachi"
    scan_ssid=1
    psk="your_real_password"
    key_mgmt=WPA-PSK
}

- add lines  to file "config.txt" in the volume "boot":

# Enable 1-wire (e.g. for temperature sensor)
dtoverlay=w1-gpio


Install RPi Relais Board:
- Download the WiringPi libraries: git clone git://git.drogon.net/wiringPi
  (please see: https://projects.drogon.net/raspberry-pi/wiringpi/download-and-install/)
  Run commands:
  - cd wiringPi
  - ./build
- Download and Install C Library bcm2835: curl -O http://www.airspayce.com/mikem/bcm2835/bcm2835-1.55.tar.gz
  (please see: http://www.airspayce.com/mikem/bcm2835/index.html)
  Run commands:
  - # download the latest version of the library, say bcm2835-1.xx.tar.gz, then:
  - tar zxvf bcm2835-1.xx.tar.gz
  - cd bcm2835-1.xx
  - ./configure
  - make
  - sudo make check
  - sudo make install
- Python Libraries for Raspbian:
  - sudo python3 -m pip install RPi.GPIO
  - sudo python3 -m pip install spidev
- Download demo code: curl -O https://www.waveshare.com/w/upload/2/24/RPi_Relay_Board.tar.gz

Install DS18B20 Temperature Sensors:
- Edit /boot/config.txt and add line: dtoverlay=w1-gpio
- Reboot (sudo reboot)
- Test with the following commands:
  - sudo modprobe w1-gpio
  - sudo modprobe w1-therm
  - pushd /sys/bus/w1/devices
  - ls
  This will show a directory for every sensor:
  - 28-000008aa92f7
  - 28-0416a5b761ff
- Rot ist 3-5 V Spannung
- Blau / Schwarz wird mit Masse verbunden
- Gelb / Weiß ist die 1-Wire Datenleitung

Install ADS1115 analog digital converter:
- Install adafruit libraries with pip: 
  - sudo python3 -m pip install adafruit-ads1x15
- Enable I2C interface with raspi-config
- Test connectivity: sudo i2cdetect -y 1
- Test ADS1115 with sample program: sudo python simpletest.py

Start flask app:
- add entry to crontab:
  - sudo crontab -e
  - add line: @reboot /bin/bash /home/pi/bin/start_pool_app.sh &
- instead of crontab entry create a systemd service:
  - sudo cp pool_app.service /lib/systemd/system
  - sudo systemctl start pool_app
  - sudo systemctl enable pool_app

Dump pool data periodically:
- add entry to crontab:
  - sudo crontab -e
  - add line: */5 * * * * /usr/bin/python3 /home/pi/bin/dump_pooldata.py

Switch pump:
- add entries to crontab:
  - sudo crontab -e
  - add line: 0   8 * * * /usr/bin/python3 /home/pi/bin/pump.py on
  - add line: 0  20 * * * /usr/bin/python3 /home/pi/bin/pump.py off

Pair bluetooth button:
- sudo bluetoothctl
  - agent on
  - pairable on
  To get the MAC address:
  - scan on
  - wait for AB Shutter3
  - scan off
  To pair:
  - pair 62:05:40:62:04:25
  - trust 62:05:40:62:04:25
  - connect 62:05:40:62:04:25
  - info 62:05:40:62:04:25

Install event handler for bluetooth button:
- copy service description to systemd directory:
  - sudo cp bluebutton.service /lib/systemd/system
- start service:
  - sudo systemctl start bluebutton
- enable autostart of service:
  - sudo systemctl enable bluebutton
