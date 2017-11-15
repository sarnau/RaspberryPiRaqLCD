# Raspbian Jessie with a Pi-Raq LCD, June 2016

## Raspbian Jessie with a Pi-Raq LCD

The Pi-Raq came with an old version of Raspbian. An upgrade to e.g. Jessie will render the display non-functioning. The manufacturer sadly never got back to me, so I fixed it myself.

Download the archive with all needed files: [EarthLCDPi-Raq.zip](EarthLCDPi-Raq.zip)


There are two main things to do:

1. Provide a custom ```dt-blob.bin``` for the pin configuration. This has changed with later version of Raspbian and is the reason why the old file no longer works.
2. Update a stock ```config.txt``` to switch to the LCD.

### How to modify the dt-blob.dts

There is very little documenation for this, which is expected, considering that hooking up a custom LCD to a Raspberry is not a very common thing to do.

I used the stock ```dt-blob.dts``` as a new base. First I stripped it down, because the Pi-Raq ships with a "Pi 2 Model B rev 1.1" only, which means all other pin configurations are not used anyway and I can't test it. If you try to use it with a different Raspberry Pi (which seems possible), you have to change the ```pins_2b2``` to match your Raspberry Pi. Use the stock version as an example and transfer the changes over.

By looking at the "Pi-RAQ Hardware Schematic.pdf" you can find out all custom pin mappings:

- Pin 0 => PCLK-Out (pixel clock)
- Pin 1 => DE-Out (display enable)
- Pin 4-8 => B3-B7-Out (5 bits for blue)
- Pin 9-14 => G2-G7-Out (6 bits for blue, our eyes are more sensitive to green)
- Pin 15-19 => R3-R7-Out (5 bits for blue)
- Pin 20-26 are for the jog shuttle controls. They don't need a custom config, because they are already covered by the pin@default case.
    - Pin 20 = Right button
    - Pin 21 = Left button
    - Pin 22 = Rot1
    - Pin 23 = Center button
    - Pin 24 = Rot2
    - Pin 25 = Down button
    - Pin 26 = Left button
- Pin 27 is the output for the backlight of the LCD. It has to be an output and should have a startup_state of "active", otherwise the display stays off after boot. It can still be turned off at any time via a script.

Normal buttons are detected on a falling edge with 100ms debounce. Rotation is doing an edge-detection (both, 10ms debounce). If Rot1 changes and the Rot1 and Rot2 bits are the same, the wheel was rotated left. If both bits have a different value, it was rotated right.

Everything beyond pin 28 is not modified.


### How to modify the config.txt

The config.txt has to be modified to switch from HDMI to the LCD. Besides basic changes, like turning overscan off (the LCD doesn't have a overscan area) and set the framebuffer size to 1024x100 pixel, it is also necessary to enable dpi support (via ```enable_dpi_lcd```), switch the default over and reconfigure the timing and output format for the dpi. Check the comments for a bit more details. The timings and the output format are specific to the LCD panel, which is connected.

### Installation Step-by-Step

1. Install Raspbian on an SD Card
2. Use ApplePi-Baker to install Raspbian Jessie Lite (the normal version is not needed for this tiny display)
3. Boot Raspberry with this card. You need to have a HDMI display connected and a USB keyboard
 - sudo raspi-config => fix the keyboard layout, set a password, changed the hostname, reboot
4. Remove the card and copy the content of this folder into /home/pi
5. Put the card back into the Raspberry and boot the Pi-Raq again.
6. It is typically faster to SSH into the Pi-Raq to configure it, but not necessary.
7. Now finish the installation:


```sudo nano /boot/config.txt```

Uncomment/Modify the following lines, which should already be in the ```config.txt```

    disable_overscan=1

    framebuffer_width=1024
    framebuffer_height=100

and add this to the bottom of the file:

    #----------------------------------------------------------------------------------------------------
    #Generated on Thu Feb 19 13:20:39 2015 by Segler-HP
    #config file for None
    #Output Format -> DPI_OUTPUT_FORMAT_16BIT_565_CFG1
    #RGB Order -> DPI_RGB_ORDER_RGB
    #Output Enable Mode ->DPI_OUTPUT_ENABLE_MODE_DATA_VALID
    #Invert Pixel Clock ->RGB Data changes on falling edge and is stable at rising edge
    #Hsync Disable ->False
    #Vsync Disable ->False
    #Output Enable ->False
    #Hsync Polarity ->Inverted
    #Vsync Polarity ->Inverted
    #Output Enable Polarity ->default for HDMI mode
    #Hsync Phase ->DPI_PHASE_POSEDGE
    #Vsync Phase ->DPI_PHASE_NEGEDGE
    #Output Enable Phase ->DPI_PHASE_NEGEDGE
    #----------------------------------------------------------------------------------------------------
    hdmi_timings=1024 0 50 100 50  100 0 2 10 2 0 0 0  60 0 25000000 7
    enable_dpi_lcd=1
    display_default_lcd=1
    dpi_output_format=4194306 #6488594
    dpi_group=2
    dpi_mode=87


The pin configuration of the device tree can be compiled from source:

    sudo dtc -I dts -O dtb -o /boot/dt-blob.bin dt-blob.dts

As an alternative to you copy the ```dt-blob.bin```

    sudo cp dt-blob.bin /boot/dt-blob.bin

The Raspberry icons occupy a large amount of the vertical space during boot. They can be disabled by adding an option to the cmdline.txt:

    sudo nano /boot/cmdline.txt

Add logo.nologo to the parameters. It should look like this after it:

    dwc_otg.lpm_enable=0 logo.nologo console=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait

We should also upgrade and update our installation:

    sudo apt-get upgrade && sudo apt-get update

Now we can reboot:

    sudo reboot

The HDMI should now be off (and can it be disconnected) and the LCD is used


## Launching the demos

To get the demos to work, we need to install a few more python specific pieces:

For AlarmTest we need pygame:

    sudo apt-get install python-pygame

This demo can be launched by ```cd AlarmTest``` and then ```python main.py```


We need pip to install more Python packages

    sudo apt-get install build-essential python-dev python-pip

This is only used for rotTest:

    sudo pip install psutil

This demo can be launched by ```cd rotTest``` and then ```python main.py```. The demo can be quit via Control-C, but the display stays blank. I haven't fixed this. ```sudo reboot``` solves it...


### The full ```dt-blob.dts``` for EarthLCD Pi-Raq

    /dts-v1/;

    / {
       videocore {
          clock_routing {
            vco@PLLD { freq = <2000000000>; };
            chan@DPER { div = <8>; }; // APER will be 500MHz
          }; // clock routing

          pins_2b2 { // Pi 2 Model B rev 1.1
             pin_config {
                pin@default {
                   polarity = "active_high";
                   termination = "pull_down";
                   startup_state = "inactive";
                   function = "input";
                }; // pin

                pin@p0  { function = "dpi";    termination = "no_pulling"; drive_strength_mA = < 8 >; };	// PCLK-OUT
                pin@p1  { function = "dpi";    termination = "no_pulling"; drive_strength_mA = < 8 >; };	// DE-OUT

                pin@p2  { function = "i2c1";   termination = "pull_up";    }; // I2C 1 SDA
                pin@p3  { function = "i2c1";   termination = "pull_up";    }; // I2C 1 SCL

                pin@p4  { function = "dpi";    termination = "no_pulling"; };	// B3-Out
                pin@p5  { function = "dpi";    termination = "no_pulling"; };	// B4-Out
                pin@p6  { function = "dpi";    termination = "no_pulling"; };	// B5-Out
                pin@p7  { function = "dpi";    termination = "no_pulling"; };	// B6-Out
                pin@p8  { function = "dpi";    termination = "no_pulling"; };	// B7-Out

                pin@p9  { function = "dpi";    termination = "no_pulling"; };	// G2-Out
                pin@p10 { function = "dpi";    termination = "no_pulling"; };	// G3-Out
                pin@p11 { function = "dpi";    termination = "no_pulling"; };	// G4-Out
                pin@p12 { function = "dpi";    termination = "no_pulling"; };	// G5-Out
                pin@p13 { function = "dpi";    termination = "no_pulling"; };	// G6-Out
                pin@p14 { function = "dpi";    termination = "no_pulling"; };	// G7-Out

                pin@p15 { function = "dpi";    termination = "no_pulling"; };	// R3-Out
                pin@p16 { function = "dpi";    termination = "no_pulling"; };	// R4-Out
                pin@p17 { function = "dpi";    termination = "no_pulling"; };	// R5-Out
                pin@p18 { function = "dpi";    termination = "no_pulling"; };	// R6-Out
                pin@p19 { function = "dpi";    termination = "no_pulling"; };	// R7-Out

                // Pin 20..26 are the Jog Shuttle controls, they are all inputs, which is covered by the pin@default case
                // p20 = Right button
                // p21 = Left button
                // p22 = Rot1			(Rot1 ^ Rot2) != 0 => Right, (Rot1 ^ Rot2) == 0 => Left if an edge was detected
                // p23 = Center button
                // p24 = Rot2
                // p25 = Down button
                // p26 = Left button

                pin@p27 { function = "output"; termination = "pull_up"; startup_state = "active"; };	// LCD Backlight enable, active at boot

                // From here on it is identical to Jessie's defaults:

                // The firmware changes I2C pin functions on the fly, returning them to inputs when done. But pins 28&29 are
                // not used on a 1.1 Pi2, so the I2C0 function ends up multiply mapped (bad). therefore don't statically map.
                // pin@p28 { function = "i2c0";   termination = "pull_up";    }; // I2C 0 SDA
                // pin@p29 { function = "i2c0";   termination = "pull_up";    }; // I2C 0 SCL
                pin@p31 { function = "output"; termination = "pull_down"; }; // LAN_RUN
                pin@p32 { function = "output"; termination = "pull_down"; }; // Camera LED
                pin@p35 { function = "input";  termination = "no_pulling"; polarity = "active_low"; }; // Power low
                pin@p38 { function = "output"; termination = "no_pulling";    }; // USB current limit (0=600mA, 1=1200mA)
                pin@p40 { function = "pwm";    termination = "no_pulling"; drive_strength_mA = < 16 >; }; // Right audio
                pin@p41 { function = "output"; termination = "no_pulling";    }; // Camera shutdown
                // Communicate with the SMPS by "bit-bashing" the I2C protocol on GPIOs 42 and 43
                pin@p42 { function = "output"; termination = "pull_up";    }; // SMPS_SCL
                pin@p43 { function = "input";  termination = "no_pulling";    }; // SMPS_SDA
                pin@p44 { function = "gp_clk"; termination = "pull_down"; }; // ETH_CLK - Ethernet 25MHz output
                pin@p45 { function = "pwm";    termination = "no_pulling"; drive_strength_mA = < 16 >; }; // Left audio

                pin@p46 { function = "input";  termination = "no_pulling"; polarity = "active_low"; }; // HDMI hotplug detect (goes to pin 6 of IC1)
                pin@p47 { function = "output"; termination = "pull_down"; }; // activity LED
                pin@p48 { function = "sdcard"; termination = "pull_up";    drive_strength_mA = < 8 >; }; // SD CLK
                pin@p49 { function = "sdcard"; termination = "pull_up";    drive_strength_mA = < 8 >; }; // SD CMD
                pin@p50 { function = "sdcard"; termination = "pull_up";    drive_strength_mA = < 8 >; }; // SD D0
                pin@p51 { function = "sdcard"; termination = "pull_up";    drive_strength_mA = < 8 >; }; // SD D1
                pin@p52 { function = "sdcard"; termination = "pull_up";    drive_strength_mA = < 8 >; }; // SD D2
                pin@p53 { function = "sdcard"; termination = "pull_up";    drive_strength_mA = < 8 >; }; // SD D3
             }; // pin_config

             pin_defines {
                pin_define@HDMI_CONTROL_ATTACHED { type = "internal"; number = <46>; };

                pin_define@NUM_CAMERAS { type = "internal"; number = <1>; };
                pin_define@CAMERA_0_I2C_PORT { type = "internal"; number = <0>; };
                pin_define@CAMERA_0_SDA_PIN { type = "internal"; number = <28>; };
                pin_define@CAMERA_0_SCL_PIN { type = "internal"; number = <29>; };
                pin_define@CAMERA_0_SHUTDOWN { type = "internal"; number = <41>; };
                pin_define@CAMERA_0_UNICAM_PORT { type = "internal"; number = <1>; };
                pin_define@CAMERA_0_LED { type = "internal"; number = <32>; };

                pin_define@FLASH_0_ENABLE { type = "absent"; };
                pin_define@FLASH_0_INDICATOR { type = "absent"; };
                pin_define@FLASH_1_ENABLE { type = "absent"; };
                pin_define@FLASH_1_INDICATOR { type = "absent"; };

                pin_define@POWER_LOW { type = "internal"; number = <35>; };
                pin_define@LEDS_DISK_ACTIVITY { type = "internal"; number = <47>; };
                pin_define@LAN_RUN { type = "internal"; number = <31>; };
                pin_define@SMPS_SDA { type = "internal"; number = <43>; };
                pin_define@SMPS_SCL { type = "internal"; number = <42>; };
                pin_define@ETH_CLK { type = "internal"; number = <44>; };
                pin_define@USB_LIMIT_1A2 { type = "internal"; number = <38>; };
                pin_define@SIO_1V8_SEL { type = "absent"; };
                pin_define@PWML { type = "internal"; number = <45>; };
                pin_define@PWMR { type = "internal"; number = <40>; };
                pin_define@SAFE_MODE { type = "internal"; number = <3>; };
                pin_define@SD_CARD_DETECT { type = "absent"; };
                pin_define@ID_SDA { type = "internal"; number = <0>; };
                pin_define@ID_SCL { type = "internal"; number = <1>; };
                pin_define@DISPLAY_I2C_PORT { type = "internal"; number = <0>; };
                pin_define@DISPLAY_SDA { type = "internal"; number = <28>; };
                pin_define@DISPLAY_SCL { type = "internal"; number = <29>; };
             }; // pin_defines
          }; // pins

       };
    };


### The full ```config.txt```

    # For more options and information see
    # http://www.raspberrypi.org/documentation/configuration/config-txt.md
    # Some settings may impact device functionality. See link above for details

    # uncomment if you get no picture on HDMI for a default "safe" mode
    #hdmi_safe=1

    # uncomment this if your display has a black border of unused pixels visible
    # and your display can output without overscan
    disable_overscan=1

    # uncomment the following to adjust overscan. Use positive numbers if console
    # goes off screen, and negative if there is too much border
    #overscan_left=16
    #overscan_right=16
    #overscan_top=16
    #overscan_bottom=16

    # uncomment to force a console size. By default it will be display's size minus
    # overscan.
    framebuffer_width=1024
    framebuffer_height=100

    # uncomment if hdmi display is not detected and composite is being output
    #hdmi_force_hotplug=1

    # uncomment to force a specific HDMI mode (this will force VGA)
    #hdmi_group=1
    #hdmi_mode=1

    # uncomment to force a HDMI mode rather than DVI. This can make audio work in
    # DMT (computer monitor) modes
    #hdmi_drive=2

    # uncomment to increase signal to HDMI, if you have interference, blanking, or
    # no display
    #config_hdmi_boost=4

    # uncomment for composite PAL
    #sdtv_mode=2

    #uncomment to overclock the arm. 700 MHz is the default.
    #arm_freq=800

    # Uncomment some or all of these to enable the optional hardware interfaces
    #dtparam=i2c_arm=on
    #dtparam=i2s=on
    #dtparam=spi=on

    # Uncomment this to enable the lirc-rpi module
    #dtoverlay=lirc-rpi

    # Additional overlays and parameters are documented /boot/overlays/README

    #----------------------------------------------------------------------------------------------------
    #Generated on Thu Feb 19 13:20:39 2015 by Segler-HP
    #config file for None
    #Output Format -> DPI_OUTPUT_FORMAT_16BIT_565_CFG1
    #RGB Order -> DPI_RGB_ORDER_RGB
    #Output Enable Mode ->DPI_OUTPUT_ENABLE_MODE_DATA_VALID
    #Invert Pixel Clock ->RGB Data changes on falling edge and is stable at rising edge
    #Hsync Disable ->False
    #Vsync Disable ->False
    #Output Enable ->False
    #Hsync Polarity ->Inverted
    #Vsync Polarity ->Inverted
    #Output Enable Polarity ->default for HDMI mode
    #Hsync Phase ->DPI_PHASE_POSEDGE
    #Vsync Phase ->DPI_PHASE_NEGEDGE
    #Output Enable Phase ->DPI_PHASE_NEGEDGE
    #----------------------------------------------------------------------------------------------------
    hdmi_timings=1024 0 50 100 50  100 0 2 10 2 0 0 0  60 0 25000000 7
    enable_dpi_lcd=1
    display_default_lcd=1
    dpi_output_format=4194306 #6488594
    dpi_group=2
    dpi_mode=87
