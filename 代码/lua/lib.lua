-- coding:GB 2312

function ReadGpio(gpio)
  status, table = sensorReq("SensorInput", { gpio }, 3600)
  if status ~= 0 then
    return -255
  end
  return table[1]
end

function ReadGpioP()
  status, table = sensorReq("REQ", { 1 }, 3600)
  if status ~= 0 then
    return -255
  end
  return table[1]
end

function readVolt()
  local gpio = (ReadGpio(5) / 255) * 5
  if ((gpio > 2) or (gpio < 0)) then
    return -1
  else
    return gpio
  end
end

function getDistance()
  local volt = readVolt()
  if (volt == -1) then
    return 0
  else
    return 60.374 * (volt^(-1.16))
  end
end

function WriteGpio(gpio, status)
  sensorReq("IOout", { gpio, status }, 25)
end

function ReadGeomagneticSensor()
  status, table = sensorReq("SensorInput", { 8 }, 3600)
  if status ~= 0 then
    return -255
  end
  return table[1]
end

function ReadColours(r, g, b)
  status, table = sensorReq("ImageIdent", { {r, g, b} }, 3600)
  if status ~= 0 then
    return status, {}
  end
  return status, table[1]
end

function ReadColoursInDelta(r, g, b, delta)
  status, table = sensorReq("ColorRange", { {r, g, b}, delta }, 3600)
  if status ~= 0 then
    return status, {}
  end
  return status, table[1]
end
  
function IsColourOfRGB(r, g, b)
  status, table = ReadColours(r, g, b)
  if status ~= 0 then
    return false
  end
  if table[3] < 1 then
    return false
  end
  return true
end

function IsColourOfRGBInDelta(r, g, b, delta)
  status, table = ReadColoursInDelta(r, g, b, delta)
  if status ~= 0 then
    return false
  end
  if table[3] < 1 then
    return false
  end
  return true
end

function IsColourOfRGBInPosition(r, g, b, positon)
  status, table = ReadColours(r, g, b)
  if status ~= 0 then
    return false
  end
  if table[3] < 1 then
    return false
  end
  result = table[4]
  if result == 0x01 and positon == "left" then
    return true
  end
  if result == 0x02 and positon == "center" then
    return true
  end
  if result == 0x03 and positon == 'right' then
    return true
  end
  return false
end

function getColourOfAxis(r, g, b, axis)
  status, table = ReadColours(r, g, b)
  if status ~= 0 then
    return 0
  end
  if axis == 'X' then
    return table[1]
  end
  if axis == 'Y' then
    return table[2]
  end
  return 0
end

function getColourOfParameter(r, g, b, name)
  status, table = ReadColours(r, g, b)
  if status ~= 0 then
    return 0
  end
  if name == 'X' then
    return table[1]
  end
  if name == 'Y' then
    return table[2]
  end
  if name == 'W' then
    return table[5]
  end
  if name == 'H' then
    return table[6]
  end
  return 0
end

function getColourOfAreaSize(r, g, b)
  status, table = ReadColours(r, g, b)
  if status ~= 0 then
    return 0
  end
  return table[3]
end

function ReadFaceData(time)
  status = 0x01
  table = {}
  for i = time, 1, -1 do
    status, table = sensorReq("FaceReg", { 2 }, 3000)
    if status == 0x00 and table[1] ~= nil and  table[1][1] ~= 0x00 then
      break
    end
  end
  if status ~= 0 then
    return status, {}
  end
  return status, table[1]
end

function IsPersonIncamera(time, sex, age, emotion)
  sexs = {
    ['male'] = 0x01,
    ['female'] = 0x02,
  }
  ages = {
    ['child'] = 0x01,
    ['teen'] = 0x02,
    ['youth'] = 0x03,
    ['middle-age'] = 0x04,
    ['elder'] = 0x05,
  }
  emotions = {
    ['sadness'] = 0x02,
    ['neutral'] = 0x01,
    ['contempt'] = 0x08,
    ['disgust'] = 0x04,
    ['anger'] = 0x05,
    ['surprise'] = 0x06,
    ['fear'] = 0x07,
    ['happiness'] = 0x03,
  }
  status, table = ReadFaceData(time)
  if status ~= 0 or table[1] == 0x00 then
    return false
  end
  if sex == 'any' and age == 'any' and emotion == 'any' then
    return true
  end
  if sex == 'any' and age == 'any' then
    if table[3] == emotions[emotion] then
      return true
    end
    return false
  end
  if sex == 'any' and emotion == 'any' then
    if table[2] == ages[age] then
      return true
    end
    return false
  end
  if age == 'any' and emotion == 'any' then
    if table[1] == sexs[sex] then
      return true
    end
    return false
  end
  if sex == 'any' then
    if table[2] == ages[age] and table[3] == emotions[emotion] then
      return true
    end
    return false
  end
  if age == 'any' then
    if table[1] == sexs[sex] and table[3] == emotions[emotion] then
      return true
    end
    return false
  end
  if emotion == 'any' then
    if table[1] == sexs[sex] and table[2] == ages[age] then
      return true
    end
    return false
  end
  if table[1] == sexs[sex] and table[2] == ages[age] and table[3] == emotions[emotion] then
    return true
  end
  return false
end

function IsFaceIncamera(time)
  status, table = ReadFaceData(time)
  if status ~= 0 or table[1] == 0x00 then
    return false
  end
  if table[1] ~= 0x00 then
    return true
  end
  return false
end

function IsSexInCase(time, sex)
  sexs = {
    ['male'] = 0x01,
    ['female'] = 0x02,
  }
  status, table = ReadFaceData(time)
  if status ~= 0 or table[1] == 0x00 then
    return false
  end
  if table[1] == sexs[sex] then
    return true
  end
  return false
end

function IsAgeInRange(time, age)
  ages = {
    ['child'] = 0x01,
    ['teen'] = 0x02,
    ['youth'] = 0x03,
    ['middle-age'] = 0x04,
    ['elder'] = 0x05,
  }
  status, table = ReadFaceData(time)
  if status ~= 0 or table[2] == 0x00 then
    return false
  end
  if table[2] == ages[age] then
    return true
  end
  return false
end

function IsEmotionInCase(time, emotion)
  emotions = {
    ['sadness'] = 0x02,
    ['neutral'] = 0x01,
    ['contempt'] = 0x08,
    ['disgust'] = 0x04,
    ['anger'] = 0x05,
    ['surprise'] = 0x06,
    ['fear'] = 0x07,
    ['happiness'] = 0x03,
  }
  status, table = ReadFaceData(time)
  if status ~= 0 or table[3] == 0x00 then
    return false
  end
  if table[3] == emotions[emotion] then
    return true
  end
  return false
end

function ReadCustomColoursByHSV(hmin, hmax, smin, smax, vmin, vmax)
  status, table = sensorReq("CustomColor", { {hmin, hmax, smin, smax, vmin, vmax} }, 3600)
  if status ~= 0 then
    return status, {}
  end
  return status, table[1]
end

function IsColourOfHSV(hmin, hmax, smin, smax, vmin, vmax)
  status, table = ReadCustomColoursByHSV(hmin, hmax, smin, smax, vmin, vmax)
  if status ~= 0 then
    return false
  end
  if table[3] < 1 then
    return false
  end
  return true
end

function IsColourOfHSVInPosition(hmin, hmax, smin, smax, vmin, vmax, positon)
  status, table = ReadCustomColoursByHSV(hmin, hmax, smin, smax, vmin, vmax)
  if status ~= 0 then
    return false
  end
  if table[3] < 1 then
    return false
  end
  result = table[4]
  if result == 0x01 and positon == "left" then
    return true
  end
  if result == 0x02 and positon == "center" then
    return true
  end
  if result == 0x03 and positon == 'right' then
    return true
  end
  return false
end

function getColourOfAxisByHSV(hmin, hmax, smin, smax, vmin, vmax, axis)
  status, table = ReadCustomColoursByHSV(hmin, hmax, smin, smax, vmin, vmax)
  if status ~= 0 then
    return 0
  end
  if axis == 'X' then
    return table[1]
  end
  if axis == 'Y' then
    return table[2]
  end
  return 0
end

function getColourOfParameterByHSV(hmin, hmax, smin, smax, vmin, vmax, name)
  status, table = ReadCustomColoursByHSV(hmin, hmax, smin, smax, vmin, vmax)
  if status ~= 0 then
    return 0
  end
  if name == 'X' then
    return table[1]
  end
  if name == 'Y' then
    return table[2]
  end
  if name == 'W' then
    return table[5]
  end
  if name == 'H' then
    return table[6]
  end
  return 0
end

function getColourOfAreaSizeByHSV(hmin, hmax, smin, smax, vmin, vmax)
  status, table = ReadCustomColoursByHSV(hmin, hmax, smin, smax, vmin, vmax)
  if status ~= 0 then
    return 0
  end
  return table[3]
end

function fast_forward_step(cnt)
  MOTOrigid16(25, 25, 25, 55, 65, 60, 60, 50, 25, 25, 25, 55, 65, 60, 60, 50)
  MOTOsetspeed(85)
  MOTOmove16(80, 30, 100, 99, 93, 50, 124, 95, 120, 170, 100, 98, 107, 150, 78, 99)
  MOTOwait()

  for var = 1, cnt, 1 do
    MOTOsetspeed(100)
    MOTOmove16(80, 30, 80, 99, 115, 99, 102, 100, 120, 170, 80, 101, 109, 134, 90, 98)
    MOTOwait()
    MOTOmove16(80, 30, 80, 99, 110, 74, 120, 100, 120, 170, 80, 101, 114, 137, 90, 100)
    MOTOwait()
    MOTOmove16(80, 30, 80, 99, 110, 61, 125, 104, 120, 170, 80, 101, 100, 127, 95, 100)
    MOTOwait()
    MOTOmove16(80, 30, 120, 99, 91, 66, 110, 102, 120, 170, 120, 101, 85, 101, 98, 100)
    MOTOwait()
    MOTOmove16(80, 30, 120, 99, 86, 63, 110, 100, 120, 170, 120, 101, 90, 126, 80, 100)
    MOTOwait()
    MOTOmove16(80, 30, 120, 99, 100, 73, 105, 100, 120, 170, 120, 101, 90, 139, 75, 96)
    MOTOwait()
  end

  MOTOsetspeed(75)
  MOTOmove16(80, 30, 80, 96, 120, 100, 105, 95, 120, 170, 80, 102, 109, 146, 78, 96)
  MOTOwait()
  MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)
  MOTOwait()
end

function fast_backward_step(cnt)
  MOTOrigid16(45, 45, 45, 55, 65, 60, 60, 50, 45, 45, 45, 55, 65, 60, 60, 50)
  MOTOsetspeed(75)
  MOTOmove16(80, 30, 100, 99, 88, 55, 124, 95, 120, 170, 100, 98, 112, 145, 78, 99)
  MOTOwait()

  for var = 1, cnt, 1 do
    MOTOsetspeed(110)
    MOTOmove16(80, 30, 120, 99, 113, 100, 99, 100, 120, 170, 120, 101, 100, 142, 74, 99)
    MOTOwait()
    MOTOmove16(80, 30, 120, 99, 95, 70, 107, 100, 120, 170, 120, 101, 95, 138, 74, 99)
    MOTOwait()
    MOTOmove16(80, 30, 120, 99, 90, 70, 104, 105, 120, 170, 120, 101, 95, 118, 91, 99)
    MOTOwait()
    MOTOmove16(80, 30, 80, 99, 100, 58, 126, 101, 120, 170, 80, 101, 87, 100, 101, 100)
    MOTOwait()
    MOTOmove16(80, 30, 80, 99, 105, 62, 126, 101, 120, 170, 80, 101, 105, 130, 93, 100)
    MOTOwait()
    MOTOmove16(80, 30, 80, 99, 105, 82, 109, 101, 120, 170, 80, 101, 110, 130, 96, 95)
    MOTOwait()
  end

  MOTOsetspeed(75)
  MOTOmove16(80, 30, 80, 96, 120, 100, 105, 95, 120, 170, 80, 102, 109, 146, 78, 96)
  MOTOwait()
  MOTOsetspeed(75)
  MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)
  MOTOwait()
end

function slow_forward_step(cnt)
  MOTOrigid16(30, 30, 30, 65, 65, 65, 65, 65, 30, 30, 30, 65, 65, 65, 65, 65)
  MOTOsetspeed(8)
  MOTOmove16(80, 35, 100, 90, 91, 48, 129, 88, 120, 165, 100, 94, 107, 146, 76, 92)
  MOTOwait()
  MOTOsetspeed(30)
  MOTOmove16(80, 35, 90, 86, 105, 85, 100, 90, 120, 165, 90, 94, 107, 146, 78, 87)
  MOTOwait()

  for var = 1, cnt, 1 do
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 90, 86, 113, 37, 156, 90, 120, 165, 90, 94, 107, 146, 77, 90)
    MOTOwait()
    MOTOsetspeed(10)
    MOTOmove16(80, 35, 90, 107, 100, 56, 124, 110, 120, 165, 90, 112, 129, 155, 93, 110)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 110, 106, 93, 54, 123, 111, 120, 165, 110, 114, 90, 105, 100, 110)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 110, 106, 93, 54, 123, 110, 120, 165, 110, 114, 87, 163, 44, 110)
    MOTOwait()
    MOTOsetspeed(10)
    MOTOmove16(80, 35, 110, 88, 71, 45, 107, 90, 120, 165, 110, 93, 100, 144, 76, 90)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 90, 86, 110, 95, 100, 90, 120, 165, 90, 94, 107, 146, 77, 89)
    MOTOwait()
  end

  MOTOsetspeed(30)
  MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)
  MOTOwait()
end

function slow_backward_step(cnt)
  MOTOrigid16(30, 30, 30, 65, 65, 65, 65, 65, 30, 30, 30, 65, 65, 65, 65, 65)
  MOTOsetspeed(8)
  MOTOmove16(80, 35, 100, 90, 91, 48, 129, 88, 120, 165, 100, 94, 107, 146, 76, 92)
  MOTOwait()
  MOTOsetspeed(30)
  MOTOmove16(80, 35, 90, 86, 105, 85, 105, 90, 120, 165, 90, 94, 107, 146, 78, 87)
  MOTOwait()

  for var = 1, cnt, 1 do
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 90, 88, 71, 53, 104, 85, 120, 165, 90, 93, 100, 144, 72, 91)
    MOTOwait()
    MOTOsetspeed(10)
    MOTOmove16(80, 35, 90, 106, 93, 53, 127, 110, 120, 165, 90, 114, 87, 163, 42, 110)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 110, 106, 93, 53, 125, 112, 120, 165, 110, 114, 90, 105, 96, 110)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 110, 107, 100, 56, 128, 109, 120, 165, 110, 112, 129, 147, 96, 115)
    MOTOwait()
    MOTOsetspeed(10)
    MOTOmove16(80, 35, 110, 86, 113, 37, 158, 90, 120, 165, 110, 94, 107, 147, 73, 90)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 35, 90, 86, 110, 95, 104, 90, 120, 165, 90, 94, 107, 147, 75, 88)
    MOTOwait()
  end

  MOTOsetspeed(30)
  MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)
  MOTOwait()
end

function left_move_step(cnt)
  MOTOrigid16(30, 30, 30, 65, 65, 65, 65, 65, 30, 30, 30, 65, 65, 65, 65, 65)

  for var = 1, cnt, 1 do
    MOTOsetspeed(65)
    MOTOmove16(80, 40, 100, 85, 112, 95, 105, 90, 120, 160, 100, 110, 107, 146, 76, 100)
    MOTOwait()
    DelayMs(50)
    MOTOsetspeed(75)
    MOTOmove16(80, 30, 100, 95, 93, 53, 121, 105, 120, 155, 100, 120, 116, 160, 68, 130)
    MOTOwait()
    DelayMs(50)
    MOTOsetspeed(75)
    MOTOmove16(80, 30, 100, 100, 93, 54, 124, 98, 120, 170, 100, 103, 107, 146, 76, 105)
    MOTOwait()
  end
end

function right_move_step(cnt)
  MOTOrigid16(30, 30, 30, 65, 65, 65, 65, 65, 30, 30, 30, 65, 65, 65, 65, 65)

  for var = 1, cnt, 1 do
    MOTOsetspeed(65)
    MOTOmove16(80, 40, 100, 90, 93, 54, 124, 100, 120, 160, 100, 115, 88, 105, 95, 110)
    MOTOwait()
    DelayMs(50)
    MOTOsetspeed(75)
    MOTOmove16(80, 45, 100, 80, 84, 40, 132, 70, 120, 170, 100, 105, 107, 147, 79, 95)
    MOTOwait()
    DelayMs(50)
    MOTOsetspeed(65)
    MOTOmove16(80, 30, 100, 97, 93, 54, 124, 95, 120, 170, 100, 100, 107, 146, 76, 102)
    MOTOwait()
    DelayMs(50)
  end
end

function left_turn_step(cnt)
  MOTOrigid16(30, 30, 30, 65, 65, 65, 65, 65, 30, 30, 30, 65, 65, 65, 65, 65)

  for var = 1, cnt, 1 do
    MOTOsetspeed(24)
    MOTOmove16(80, 30, 115, 95, 63, 55, 94, 95, 120, 170, 115, 105, 77, 145, 46, 105)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 30, 115, 95, 63, 55, 94, 93, 120, 170, 115, 105, 77, 145, 46, 107)
    MOTOwait()
    MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)
    MOTOwait()
  end
end

function right_turn_step(cnt)
  MOTOrigid16(30, 30, 30, 65, 65, 65, 65, 65, 30, 30, 30, 65, 65, 65, 65, 65)

  for var = 1, cnt, 1 do
    MOTOsetspeed(24)
    MOTOmove16(80, 30, 85, 95, 123, 55, 154, 95, 120, 170, 85, 105, 137, 145, 106, 105)
    MOTOwait()
    MOTOsetspeed(30)
    MOTOmove16(80, 30, 85, 95, 123, 55, 154, 93, 120, 170, 85, 105, 137, 145, 106, 107)
    MOTOwait()
    MOTOmove16(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100)
    MOTOwait()
  end
end

