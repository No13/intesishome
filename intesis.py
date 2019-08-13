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

def initIntesis():
    global domoticz_url,domoticz_user,domoticz_pass,intesis_user,intesis_pass,intesis_dev
    try:
        domoticz_url = environ['DOMO_URL']
        domoticz_user = environ['DOMO_USER']
        domoticz_pass = environ['DOMO_PASS']
        intesis_user = environ['INTESIS_USER']
        intesis_pass = environ['INTESIS_PASS']
    except:
        pass
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
    print("Found device: " + intesis_dev)
    
def doIntesisCmd(command):
    print("Executing intesisCommand: "+command)
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
