import time
import network
import socket
import oled
import valve
import MotorDriver
from machine import Pin
import uasyncio as asyncio




m = 0
#m = MotorDriver.MotorDriver()


valveList = []
valveList.append(valve.valve("DruppelSlang"	,m,"MA"))
valveList.append(valve.valve("Voortuin"		,m,"MB"))
valveList.append(valve.valve("Achtertuin_1"	,m,"MC"))
valveList.append(valve.valve("Achtertuin_2"	,m,"MD"))

onboard = Pin("LED", Pin.OUT, value=0)
button = Pin(15, Pin.IN, Pin.PULL_UP)

WaterAllSequence = False















OLED = oled.OLED_1inch3()

ssid = 'Achten'
password = 'internet&snoepjes4layka!'
wlan = network.WLAN(network.STA_IF)


def connect_to_network():
    wlan.active(True)
    wlan.config(pm = 0xa11140)  # Disable power-save mode
    wlan.connect(ssid, password)

    max_wait = 300
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        OLED.fill(0x0000)
        OLED.text("connecting " + str(max_wait),1,10,OLED.white)
        OLED.show()
        time.sleep(1)
        time.sleep(1)

    if wlan.status() != 3:
        OLED.fill(0x0000)
        OLED.text("CONNECT FAILED:",1,27,OLED.white)
        OLED.show()
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        OLED.fill(0x0000)
        OLED.text("CONNECTION OK:",1,10,OLED.white)
        OLED.text(status[0],1,27,OLED.white)
        OLED.show()
        
        
        
async def serve_client(reader, writer):
    global WaterAllSequence
    global valve
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    request = str(request_line)
    for valve in valveList:
        index = request.find(valve.getName()+'=on')
        if index == 8:
            print( 'Enable valve ' + valve.getName())
            valve.setState(True)
        index = request.find(valve.getName()+'=off')
        if index == 8:
            print( 'Disable valve ' + valve.getName())
            valve.setState(False)
            
    if request.find('WaterAllSequence=on') == 8:
        WaterAllSequence = True
        
    if request.find('WaterAllSequence=off') == 8:    
        WaterAllSequence = False
        
    
    html = generateHTML(valveList,WaterAllSequence)
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(html)

    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")
        





HTML_head = """<!DOCTYPE html><html>
<head><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
.buttonGreen { background-color: #4CAF50; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
.buttonRed { background-color: #D11D53; border: 2px solid #000000;; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; }
text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
</style></head>
<body><center><h1>Control Panel</h1></center><br><br>
<form><center>
<center>"""

HTML_tail = """

</form>
<br><br>
<br><br>
</body></html>"""


def generateHTML(valveList, WaterAllSequence):
    HTML = HTML_head
    if WaterAllSequence == False:
        for valve in valveList:
            if valve.getState() == True:
                HTML += '<button class="buttonGreen" name="'+ valve.getName()+'" value="off" type="submit">'+ valve.getName()+'</button>'
            else:
                HTML += '<button class="buttonRed" name="'+ valve.getName()+'" value="on" type="submit">'+ valve.getName()+'</button>'
        
        HTML += '<br><button class="buttonRed" name="WaterAllSequence" value="on" type="submit">Automatisch elke zone 30 min</button>'
    else:
        HTML += '<br><button class="buttonGreen" name="WaterAllSequence" value="off" type="submit">Stop automatische run</button>'
            
    HTML += HTML_tail
    return HTML




























async def main():
    print('Connecting to Network...')
    connect_to_network()

    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 1234))
    while True:
        onboard.on()
        print("heartbeat")
        await asyncio.sleep(0.25)
        onboard.off()
        await asyncio.sleep(5)
        
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()

