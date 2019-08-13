from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from pyintesishome import IntesisHome
from os import environ

def initIntesis():
    domoticz_url = environ['DOMO_URL']
    domoticz_user = environ['DOMO_USER']
    domoticz_pass = environ['DOMO_PASS']
    intesis_user = environ['INTENSIS_USER']
    intesis_pass = environ['INTENSIS_PASS']
    controller = IntesisHome(intesis_user, intesis_pass)
    controller.poll_status()
    devices = controller.get_devices()
    if len(devices) == 0:
        print("No airco found")
        exit()
    if len(devices) > 1:
        print("Too many devices found!")
        exit()
    intesis    


class intesisServer(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print (self.path)
            if self.path.startswith("/cmd"):
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write("Command received! "+self.path )
                return
            if self.path.startswith("/"):
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write("Hello, I am a webserver")
                return
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)



def main():
    try:
        server = HTTPServer(('', 80), intesisServer)
        print ('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
