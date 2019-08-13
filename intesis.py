from urllib.parse import urlparse
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from pyintesishome import IntesisHome
from os import environ

domoticz_url = ''
domoticz_user = ''
domoticz_pass = ''
intesis_user = ''
intesis_pass = ''
intesis_dev = ''
intesis_dict = {}

cmd_next = ""
cmd_do_exec = False
controller = None

def initIntesis():
    global domoticz_url,domoticz_user,domoticz_pass,intesis_user,intesis_pass,intesis_dev,intesis_dict,controller
    try:
        intesis_user = environ['INTESIS_USER']
        intesis_pass = environ['INTESIS_PASS']
        domoticz_url = environ['DOMO_URL']
        domoticz_user = environ['DOMO_USER']
        domoticz_pass = environ['DOMO_PASS']
      
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
    print(controller.is_connected)

def doIntesisCmd(command):
    global domoticz_url,domoticz_user,domoticz_pass,intesis_user,intesis_pass,intesis_dev,intesis_dict,controller
    #controller = IntesisHome(intesis_user, intesis_pass)
    if not controller.is_connected:
        print("Controller not connected, reconnecting!")
        controller.connect()
    if not controller.is_connected:
        print("Error, not connected!")
        return
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
    if command == 'quiet':
        controller.set_fan_speed(intesis_dev,'quiet')
    if command == 'low':
        controller.set_fan_speed(intesis_dev,'low')
    if command == 'medium':
        controller.set_fan_speed(intesis_dev,'medium')
    if command == 'high':
        controller.set_fan_speed(intesis_dev,'high')
    if command == 'auto':
        controller.set_fan_speed(intesis_dev,'auto')
    try:
        if int(command) in range(10,40):
            controller.set_temperature(intesis_dev,int(command))
    except:
        pass
                
    return

class intesisServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        global cmd_next, cmd_do_exec
        try:
            print (self.path)
            if self.path.startswith("/cmd"):
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                cmd = urlparse(self.path).query
                cmd_next = cmd
                cmd_do_exec = True
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



def main():
    global cmd_next,cmd_do_exec
    try:
        print('Init intesisHome')
        initIntesis()
        server = TCPServer(('', 8000), intesisServer)
        print ('started httpserver...')
        while True:
            server.handle_request()
            if cmd_do_exec:
                print("Going to exec: "+cmd_next)
                doIntesisCmd(cmd_next)
                cmd_do_exec = False
    except KeyboardInterrupt:
        print ('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
