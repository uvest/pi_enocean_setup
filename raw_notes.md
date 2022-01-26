

1. DISABLE the serial console:
   1. 'sudo raspi-config' > Interfacing > Serial > "Use login shell" > "Nein" > "Enable serial interface hardware" > "Yes"

Info: This will change '/boot/cmdline.txt' and '/boot/config.txt'

This stops the system from sending debugging messages over GPIO pins and enables the use of external hardware, like an Antenna.

/boot/config.txt anpassen:
   add :
   '''
   dtoverlay=pi3-miniuart-bt
   enable_uart=1
   force_turbo=1
   '''

2. Install FHEM server to test configuration
   1. Install perl: 
   '''
    sudo apt-get install perl libdevice-serialport-perl libio-socket-ssl-perl libwww-perl
   '''
   1. wget http://fhem.de/fhem-5.6.deb
   2. Stop running interfering webservers:
      1. Check for listening servers: 'sudo netstat -tunlp'
      2. Stop any server blocking port 8083
   3. sudo dpkg -i fhem-5.6.deb
   4. Maybe also change some rights to be on the safe side:
   '''
   cd /opt
   sudo chmod -R a+w fhem
   sudo usermod -a -G tty pi && sudo usermod -a -G tty fhem
   '''

Now the FHEM server should be installed in the path '/opt/fhem'. It can be started with a demo configuration from within this folder using 'perl fhem.pl fhem.cfg.demo' (see the README there).

You can check the status of the server with: 'sudo systemctl status fhem'


sudo wget https://raw.github.com/lurch/rpi-serial-console/master/rpi-serial-console -O /usr/bin/rpi-serial-console 
sudo chmod +x /usr/bin/rpi-serial-console

in fhem.cfg:
define TCM310_0 TCM 310 /dev/ttyAMA0@576

3. enocean link middleware (not needed):
   * https://www.enocean.com/en/products/enocean-software/enocean-link/

4. Install python enocean...
    1. sudo python3 -m pip install install enocean
    2. git clone https://github.com/kipe/enocean.git


5. Run the python example script
   * stop fhem server bevore executing python example script
   * start with python 3 (no sudo required) `python3 example.py`
   * Press the learn button at the sensor => A message pops up containing partially expected data (signal strength, temperature, unit, etc.)

BUT: The temperature value never changes

6. Find the correct sensor
   * some enocean sensors:
     * RPS: Light and Blind Control
     * BS1: Single output contact
     * BS4: 10 bit temperature sensor
   * This is a BS4 sensor with specifications:
     * RORG 0xA5 (=165) - FUNC 0x04 - TYPE 0x01 - Range 0°C to +40°C and 0% to 100%
     * raw values from 0.0 to 250.0
     * interpolation linear
   * 
