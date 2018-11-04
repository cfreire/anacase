# ANACASE

Counter and random sampler of moving objects, using python computer vision (opencv). 

## Requirements

* Raspberry Pi 3 B
* Touch 10" (800x480)
* Buzzer (12v)
* Leds (bicolor red/green)

## Installing

### Create USB Stick
    Format USB STICK em FAT
    $ sudo dd if=2018-06-27-raspbian-stretch.img of=/dev/mmcblk0 bs=4M
    
### Removing unwanted apps in raspi
    $ sudo apt update
    $ sudo apt purge libreoffice*
    $ sudo apt purge wolfram*
    $ sudo apt upgrade
    
### python require libs for opencv
    $ sudo apt-get install build-essential cmake git pkg-config
    $ sudo apt install -y libatlas-base-dev gfortran libjpeg-dev  \ 
      libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libqt4-dev
    $ sudo pip3 install imutils
---
**Verify python libs**  

    $ sudo pip3 freeze -l
    imutils==0.4.6
    opencv-python==3.4.0.12
    
### obtain anacase from github
    git clone https://github.com/cfreire/anacase.git

### Leds 
    sudo pip install gpiozero

### Buzzer 
    sudo apt install python3-rpi.gpio
    
## Usage   
    cd anacase
    ./anacase.sh

## Running the tests

TODO

## Built With

* python 3.5

## Contributing

TODO

## Authors

* César Freire
* Luis Antunes

## License

This project is licensed under the GPL License - see the [LICENSE.md](LICENSE.md) file for details
