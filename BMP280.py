#!/usr/bin/python

import time
from Adafruit_I2C import Adafruit_I2C

# ===========================================================================
# BMP280 Class
# ===========================================================================

class BMP280 :
  i2c = None

  __BMP280_ADDRESS            = 0x77
  __BMP280_CHIPID             = 0x58

  # BMP280 Registers
  __BMP280_DIG_T1              = 0x88
  __BMP280_DIG_T2              = 0x8A
  __BMP280_DIG_T3              = 0x8C

  __BMP280_DIG_P1              = 0x8E
  __BMP280_DIG_P2              = 0x90
  __BMP280_DIG_P3              = 0x92
  __BMP280_DIG_P4              = 0x94
  __BMP280_DIG_P5              = 0x96
  __BMP280_DIG_P6              = 0x98
  __BMP280_DIG_P7              = 0x9A
  __BMP280_DIG_P8              = 0x9C
  __BMP280_DIG_P9              = 0x9E

  __BMP280_CHIPID             = 0xD0
  __BMP280_VERSION            = 0xD1
  __BMP280_SOFTRESET          = 0xE0

  __BMP280_CAL26              = 0xE1  # R calibration stored in 0xE1-0xF0

  __BMP280_STATUS             = 0xF3
  __BMP280_CONTROL            = 0xF4
  __BMP280_CONFIG             = 0xF5
  __BMP280_PRESSUREDATA       = 0xF7
  __BMP280_TEMPDATA           = 0xFA

  # Operating Modes
  __BMP280_SLEEP              = 0x00
  __BMP280_FORCED             = 0x01  # Or 0x01
  __BMP280_NORMAL             = 0x11
  

  
  # Private Fields
  _dig_T1 = 0
  _dig_T2 = 0
  _dig_T3 = 0

  _dig_P1 = 0
  _dig_P2 = 0
  _dig_P3 = 0
  _dig_P4 = 0
  _dig_P5 = 0
  _dig_P6 = 0
  _dig_P7 = 0
  _dig_P8 = 0
  _dig_P9 = 0

  unitTest = False

  read24Vals = []

  # Constructor
  def __init__(self, address=0x77, mode=3, debug=False):
    self.i2c = Adafruit_I2C(address)

    self.i2c.write8(self.__BMP280_SOFTRESET, 0xB6)
    time.sleep(0.2)
    
    self.address = address
    self.debug = debug
    # Make sure the specified mode is in the appropriate range
    if ((mode < 0) | (mode > 3)):
      if (self.debug):
        print("Invalid Mode: Using STANDARD by default")
      self.mode = self.__BMP280_NORMAL
    else:
      self.mode = mode

    # Read the chipid
    chipid = self.i2c.readU8(self.__BMP280_CHIPID)
    if(self.debug):
      print("Chip ID: 0x%04X" % chipid)

    # Read the calibration data
    self.readCalibrationData()

    control = (1 <<5) + (3 <<2) + 3

    self.i2c.write8(self.__BMP280_CONTROL, control)
    time.sleep(0.2)

    config = (7 << 5) + (1 << 2)
    self.i2c.write8(self.__BMP280_CONFIG, config)

    time.sleep(0.2)
    if(self.debug):
        print "Control: 0x%08x" % self.i2c.readU8(self.__BMP280_CONTROL)
        print "Config:  0x%08x" % self.i2c.readU8(self.__BMP280_CONFIG)

  def readS16(self, register):
    "Reads a signed 16-bit value"
    hi = self.i2c.readS8(register)
    lo = self.i2c.readU8(register+1)
    return (hi << 8) + lo

  def readS16_LE(self, register):
    "Reads a signed 16-bit value"
    hi = self.i2c.readS8(register+1)
    lo = self.i2c.readU8(register)
    return (hi << 8) + lo

  def readU16(self, register):
    "Reads an unsigned 16-bit value"
    hi = self.i2c.readU8(register)
    lo = self.i2c.readU8(register+1)
    return (hi << 8) + lo

  def readU16_LE(self, register):
    "Reads an unsigned 16-bit value little endian"
    hi = self.i2c.readU8(register+1)
    lo = self.i2c.readU8(register)
    return (hi << 8) + lo

  def read24(self, register):
    "Reads an unsigned 24-bit value"

    if(self.unitTest):
      return self.read24Vals.pop()

    value = self.i2c.readU8(register)
    value <<= 8
    value |= self.i2c.readU8(register+1)
    value <<=8
    value |= self.i2c.readU8(register+2)
    return value

  def readChipId(self):
    chipid = self.i2c.readU8(self.__BMP280_CHIPID)
    return chipid

  def readCalibrationData(self):
    "Reads the calibration data from the IC"
    self._dig_T1 = self.readU16_LE(self.__BMP280_DIG_T1)
    self._dig_T2 = self.readS16_LE(self.__BMP280_DIG_T2)
    self._dig_T3 = self.readS16_LE(self.__BMP280_DIG_T3)
    self._dig_P1 = self.readU16_LE(self.__BMP280_DIG_P1)
    self._dig_P2 = self.readS16_LE(self.__BMP280_DIG_P2)
    self._dig_P3 = self.readS16_LE(self.__BMP280_DIG_P3)
    self._dig_P4 = self.readS16_LE(self.__BMP280_DIG_P4)
    self._dig_P5 = self.readU16_LE(self.__BMP280_DIG_P5)
    self._dig_P6 = self.readS16_LE(self.__BMP280_DIG_P6)
    self._dig_P7 = self.readS16_LE(self.__BMP280_DIG_P7)
    self._dig_P8 = self.readS16_LE(self.__BMP280_DIG_P8)
    self._dig_P9 = self.readS16_LE(self.__BMP280_DIG_P9)
    
    if (self.debug):
      self.showCalibrationData()

  def showCalibrationData(self):
      "Displays the calibration values for debugging purposes"
      print "DBG: T1 = %6d" % (self._dig_T1)
      print "DBG: T2 = %6d" % (self._dig_T2)
      print "DBG: T3 = %6d" % (self._dig_T3)
      print "DBG: P1 = %6d" % (self._dig_P1)
      print "DBG: P2 = %6d" % (self._dig_P2)
      print "DBG: P3 = %6d" % (self._dig_P3)
      print "DBG: P4  = %6d" % (self._dig_P4)
      print "DBG: P5  = %6d" % (self._dig_P5)
      print "DBG: P6  = %6d" % (self._dig_P6)
      print "DBG: P7  = %6d" % (self._dig_P7)
      print "DBG: P8  = %6d" % (self._dig_P8)
      print "DBG: P9  = %6d" % (self._dig_P9)

  adc_T = 0
  adc_P = 0
  
  def readDevice(self):
    self.adc_T = self.read24(self.__BMP280_TEMPDATA)
    self.adc_T >>= 4

    self.adc_P = self.read24(self.__BMP280_PRESSUREDATA)
    self.adc_P >>= 4

  def readTFine(self):
    self.readDevice()
    "Gets the tFine value used to compute temperature and pressure"
    
    var1 = (((self.adc_T>>3) - (self._dig_T1 << 1)) * self._dig_T2) >> 11
    var2 = ((((self.adc_T>>4) - self._dig_T1) * ((self.adc_T>>4) - self._dig_T1) >> 12) * self._dig_T3) >> 14

    return (var1 + var2)

  def readTemperature(self):
    "Gets the compensated temperature in degrees celcius"
    t_fine = self.readTFine()
    T = ((t_fine * 5 + 128) >> 8) * 1.0
    return T / 100

  def readPressure(self):
    "Gets the compensated pressure in pascal"
    t_fine = self.readTFine()

    if(self.unitTest):
      print 't_fine: {0}'.format(t_fine)
      print 'adc_P: {0}'.format(self.adc_P)

    var1 = t_fine - 128000
    var2 = var1 * var1 * self._dig_P6

    if(self.unitTest):
      print 'var1: {0}'.format(var1)
      print 'var2: {0}'.format(var2)

    var2 = var2 + ((var1 * self._dig_P5) << 17)
    var2 = var2 + (self._dig_P4 << 35)
    var1 = ((var1 * var1 * self._dig_P3) >> 8) + ((var1 * self._dig_P2) << 12)
    var1 = (((1 << 47) + var1)) * self._dig_P1 >> 33

    if (var1 == 0):
      return 0  # avoid exception caused by division by zero
    
    p = 1048576 - self.adc_P
    p = (((p << 31) - var2) * 3125) / var1
    var1 = ((self._dig_P9) * ( p >> 13 ) * ( p >> 13)) >> 25
    var2 = ((self._dig_P8) * p) >> 19

    p = ((p + var1 + var2) >> 8) + (self._dig_P7 << 4)
    return (p * 1.0) / 256.0

  def testTFine(self):
    self.unitTest = True
    self._dig_T1 = 27504
    self._dig_T2 = 26435
    self._dig_T3 = -1000
    self.read24Vals.append((519888 << 4))

    t_fine = self.readTFine()

    print 'TFine Test: Expected {0} - Actual {1}'.format( 128422, t_fine )

  def testTemp(self):
    self.unitTest = True
    self._dig_T1 = 27504
    self._dig_T2 = 26435
    self._dig_T3 = -1000
    self.read24Vals.append((519888 << 4))

    temp = self.readTemperature()

    print 'Temp Test: Expected {0} - Actual {1}'.format( 25.08, temp )

  def testPressure(self):
    self.unitTest = True
    self._dig_T1 = 27504
    self._dig_T2 = 26435
    self._dig_T3 = -1000
    self._dig_P1 = 36477
    self._dig_P2 = -10685
    self._dig_P3 = 3024
    self._dig_P4 = 2855
    self._dig_P5 = 140
    self._dig_P6 = -7
    self._dig_P7 = 15500
    self._dig_P8 = -14600
    self._dig_P9 = 6000
    self.read24Vals.append(415148 << 4)
    self.read24Vals.append(519888 << 4)
    
    pressure = self.readPressure()

    print 'Pressure Test: Expected {0} - Actual {1}'.format( 25767236/256, pressure )
