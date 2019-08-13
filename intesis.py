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

def updateIntesis():
    global controller
    controller.poll_status()
    devices = controller.get_devices()
    for i in devices:
        intesis_dev = i
    intesis_dict = devices[i]
    
def doIntesisCmd(command):
    global controller, intesis_dev
    print("Executing intesisCommand: "+command)
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
    if command == '1':
        controller.set_fan_speed(intesis_dev,'quiet')
    if command == '2':
        controller.set_fan_speed(intesis_dev,'low')
    if command == '3':
        controller.set_fan_speed(intesis_dev,'medium')
    if command == '4':
        controller.set_fan_speed(intesis_dev,'high')
    if command == '0':
        controller.set_fan_speed(intesis_dev,'auto')
    try:
        if int(command) in range(10,40):
            controller.set_temperature(intesis_dev,int(command))
    except:
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



def main():
    try:
        print('Init intesisHome')
        initIntesis()
        server = TCPServer(('', 8000), intesisServer)
        print ('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
