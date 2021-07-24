# wiringPi 

[Wiring Pi](http://wiringpi.com/) ~ projects@drogon.net

## utility program: [gpio](https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility/)

<font color="blue">gpio [-g/-p] mode/read/write PIN# MODE/LEVEL</font>

* Show Version: **gpio -v**
* Show GPIO Table: **gpio readall**
* Set Mode: **gpio mode PIN in/out/pwm/up/down/tri**
* Use BCM_GPIO pin number: **gpio -g ...**

## Compile & Link
gcc test_gpio.c **-lwiringPi**
