from pymodbus.exceptions import ModbusIOException
from pymodbus.client import ModbusSerialClient as ModbusClient
from datetime import datetime, time

#Input Registers
IN_STATUS = 0
IN_CHG_KWH_TODAY = 57
IN_BAT_KWH_TODAY = 61
IN_BYP_KWH_TODAY = 65

#Holding Registers
HO_OUTPUT_CONFIG = 1
HO_OUTPUT_T_Y = 45
HO_OUTPUT_T_MO = 46
HO_OUTPUT_T_D = 47
HO_OUTPUT_T_H = 48
HO_OUTPUT_T_MI = 49
HO_OUTPUT_T_S = 50

#Statuses
STATUS_STANDBY = 0
STATUS_NOUSE = 1
STATUS_DISCHARGE = 2
STATUS_FAULT = 3
STATUS_FLASH = 4
STATUS_PV_CHG = 5
STATUS_AC_CHG = 6
STATUS_COM_CHG = 7
STATUS_COM_CHG_BYP = 8
STATUS_PV_CHG_BYP = 9
STATUS_AC_CHG_BYP = 10
STATUS_BYPASS = 11
STATUS_PV_CHG_DISCHG = 12

#Output configs
OUTPUT_CONFIG_BATTS = 0
OUTPUT_CONFIG_UTIL = 2

#Cheap mains electricity times
cheapLeccyStart = time(23, 40)
cheapLeccyEnd = time(5, 20)
timenow = datetime.now()

statDump1Start = time(5, 25)
statDump1End = time(5, 30)
statDump2Start = time(23, 25)
statDump2End = time(23, 30)
statDump3Start = time(23, 54)
statDump3End = time(23, 59)

print("System clock: " + timenow.strftime("%H:%M:%S"))

inverterport = "/dev/ttyXRUSB0"
input_lines = 100
columns = 5
column_inc = int(input_lines / columns)

try:
  client = ModbusClient(method='rtu', port=inverterport, baudrate=9600, stopbits=1, parity='N', bytesize=8, timeout=1)
  client.connect()

  inregs = client.read_input_registers(0, input_lines, 1)
  horegs = client.read_holding_registers(0, input_lines, 1)

  if type(inregs) is ModbusIOException:
    raise inregs

  if type(horegs) is ModbusIOException:
    raise horegs

  outputConfig = horegs.registers[HO_OUTPUT_CONFIG]
  year = horegs.registers[HO_OUTPUT_T_Y]
  month = horegs.registers[HO_OUTPUT_T_MO]
  day = horegs.registers[HO_OUTPUT_T_D]
  hour = horegs.registers[HO_OUTPUT_T_H]
  min = horegs.registers[HO_OUTPUT_T_MI]
  sec = horegs.registers[HO_OUTPUT_T_S]

  print("Inverter clock: " + str(year) + "-" + str(month) + "-" + str(day) + " " + str(hour) + ":" + str(min) + ":" + str(sec))

  #TO DO: CHECK AND WARN IF SYSTEM CLOCK DIFFERS TO INVERTER CLOCK

  #Output mode switching logic.
  if outputConfig == OUTPUT_CONFIG_BATTS:
    #Output set to battery first. Switch to utility at cheap leccy o'clock.
    print("We're on batts.")

    if timenow.time() > cheapLeccyStart or timenow.time() < cheapLeccyEnd:
      print("Cheap leccy o'clock. Switching to grid.")
      client.write_register(HO_OUTPUT_CONFIG, OUTPUT_CONFIG_UTIL, 1)

  elif outputConfig == OUTPUT_CONFIG_UTIL:
    #Output set to utility first. Switch to battery at expensive leccy o'clock.
    print("We're on utility.")

    if timenow.time() < cheapLeccyStart and timenow.time() > cheapLeccyEnd:
      print("Expensive leccy o'clock. Switching to batteries.")
      client.write_register(HO_OUTPUT_CONFIG, OUTPUT_CONFIG_BATTS, 1)

  else:
    #Output setting unexpected.
    print("Output setting" + str(outputConfig) + "unexpected!")

  #Dump stats at electricity rate changes.
  if ((timenow.time() > statDump1Start and timenow.time() < statDump1End) or
      (timenow.time() > statDump2Start and timenow.time() < statDump2End) or
      (timenow.time() > statDump3Start and timenow.time() < statDump3End)):
    with open("/home/pi/invlogs/stats-" + timenow.strftime("%Y%m%d") + ".csv", 'a') as f:
      f.write(timenow.strftime("%Y-%m-%d %H:%M:%S,"))
      f.write(str(inregs.registers[IN_CHG_KWH_TODAY]) + ",")
      f.write(str(inregs.registers[IN_BAT_KWH_TODAY]) + ",")
      f.write(str(inregs.registers[IN_BYP_KWH_TODAY]) + "\n")

except Exception as e:
  print("Failed: " + str(e))
else:
  print("Done.")

