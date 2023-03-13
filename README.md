# growatt-spf5000es-modbus-offpeak-charging
Off-peak battery charging control via Linux device (e.g. Raspberry Pi) for Growatt SPF5000ES (and similar) inverters

The primary goal of this project is to facilitate scheduled off-peak charging of batteries with the Growatt SPF 5000 ES and similar "off-grid" inverters, using a Raspberry Pi or similarly capable device. Secondarily it does a bit of reporting.

In my case, this allows me to charge domestic storage batteries on UK electricty supplier Octopus's "Intelligent" tariff, featuring very cheap electricity between 2330 and 0530 hrs. My setup is batteries + inverter only and doesn't (yet) feature solar panels.

It is necessary because although this inverter unit features "Setting 49 - Utility Charging Time" which controls when the unit can use the grid to charge the batteries, it won't actually do it while "Setting 01 - Output Source Priority" is set to "Battery first" unless the battery voltage is lower than "Setting 12 - B2AC Voltage", and setting this artifially high would cause it to unwantedly switch to grid during the peak hours.

The intervention is straightforward; Setting 01 is changed to "Utility First" just after 2330 hrs and changed to "Battery First" just before 0530 hrs. Meanwhile, "Setting 49 - Utility Charging Time" is already set to 0004 (0000 hrs to 0459 - unfortunately only units of hour granularity are possible, but five hours is just about sufficient to fully charge my 16x 3.2V 280Ah battery bank at 56V/50A!).

This project requires pymodbus and Python 3. It also requires exar USB Modbus drivers. Some Linux distros come with them, others (including stock Raspbian on Raspberry Pi) don't. On Raspbian, you need to compile the exar drivers yourself, after modifying the source code a bit (as at the time of writing they don't support Linux kernel >3.0 without tweaks). Unfortunately this is too involved for this README!

The script should be called every 5 minutes from Cron or scheduled tasks.

This code is freely offered for any purpose, at your own risk. Please feel free to fork this project and tailor it to suit your own needs.
