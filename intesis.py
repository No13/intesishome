from urllib.parse import urlparse
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from pyintesishome import IntesisHome
from os import environ
import threading,requests
import asyncio
import gc

domoticz_url = ''
domoticz_user = ''
domoticz_pass = ''
domoticz_idx = ''
intesis_user = ''
intesis_pass = ''
intesis_dev = ''
intesis_dict = {}
loop = None
old_setpoint = '0'
controller = None

def initIntesis():
    global domoticz_url,domoticz_user,domoticz_pass,domoticz_idx,intesis_user,intesis_pass,intesis_dev,intesis_dict,loop, controller
    loop = asyncio.new_event_loop()
    try:
        intesis_user = environ['INTESIS_USER']
        intesis_pass = environ['INTESIS_PASS']
        domoticz_url = environ['DOMO_URL']
        domoticz_user = environ['DOMO_USER']
        domoticz_pass = environ['DOMO_PASS']
        domoticz_idx = environ['DOMO_IDX']
    except:
        pass
    print("Looking for airco: "+intesis_user)
    controller = IntesisHome(intesis_user, intesis_pass)
    controller.poll_status()
    devices = controller.get_devices()
    if len(devices) == 0:
        print("No airco found")
        exit()
    if len(devices) > 1:
        print("Too many devices found!")
        exit()
    for i in devices:
        intesis_dev = i
    intesis_dict = devices[i]
    print("Found device: " + intesis_dev)

def doIntesisCmd(command):
    global domoticz_url,domoticz_user,domoticz_pass,intesis_user,intesis_pass,intesis_dev,intesis_dict,controller

    if not controller.is_connected:
        print("Controller not connected, reconnecting!")
        controller.connect()

    if not controller.is_connected:
        print("Error, not connected!")
        print("Attempting anyway!")
        #return

    print("Executing intesisCommand: "+command+" on "+intesis_dev)
    if command == 'on':
        controller.set_power_on(intesis_dev)
    if command == 'off':
        controller.set_power_off(intesis_dev)
    if command == 'heat':
        controller.set_mode_heat(intesis_dev)
    if command == 'fan':
        controller.set_mode_fan(intesis_dev)
    if command == 'cool':
        controller.set_mode_cool(intesis_dev)
    if command == 'dry':
        controller.set_mode_dry(intesis_dev)
    if command == 'auto':
        controller.set_mode_auto(intesis_dev)
    if command == 'fan_quiet':
        controller.set_fan_speed(intesis_dev,'quiet')
    if command == 'fan_low':
        controller.set_fan_speed(intesis_dev,'low')
    if command == 'fan_medium':
        controller.set_fan_speed(intesis_dev,'medium')
    if command == 'fan_high':
        controller.set_fan_speed(intesis_dev,'high')
    if command == 'fan_auto':
        controller.set_fan_speed(intesis_dev,'auto')
    try:
        if int(command) in range(10,40):
            controller.set_temperature(intesis_dev,int(command))
    except:
        print("Error sending temperature")
        pass

    return

class intesisServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            print (self.path)
            if self.path.startswith("/cmd"):
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                cmd = urlparse(self.path).query
                doIntesisCmd(cmd)
                return
            if self.path.startswith("/"):
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(bytearray("Hello, I am a webserver",'utf-8'))
                return
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

def getSetPoint():
    global domoticz_url, domoticz_user, domoticz_pass, domoticz_idx, old_setpoint
    cmd = None
    try:
        url = domoticz_url+'?type=devices&rid='+str(domoticz_idx)
        domo = requests.get(url, auth=(domoticz_user,domoticz_pass))
        domo_json = domo.json()
        new_setpoint = str(int(float(domo_json['result'][0]['SetPoint'])))
        if new_setpoint != old_setpoint:
            if old_setpoint != '0':
                print (" Setting setpoint to: "+ new_setpoint)
                cmd = new_setpoint
            old_setpoint = new_setpoint
    except:
        print("Polling Domoticz @ "+url)
        print("ERROR polling domoticz")
        print(domo_json)
        pass
    finally:
        if cmd != None:
            doIntesisCmd(cmd)
        threading.Timer(15, getSetPoint).start()
    
def main():
    global domoticz_user,domoticz_pass,domoticz_url,domoticz_idx
    try:
        print('Init intesisHome')
        initIntesis()
        server = TCPServer(('', 8000), intesisServer)
        print ('started httpserver...')
        if domoticz_url != '' and domoticz_idx != '':
            # Start timer to poll domoticz
            getSetPoint()

        while True:
            server.handle_request()
    except KeyboardInterrupt:
        print ('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
