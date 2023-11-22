from pymodbus import framer

class ClientArgs:
    def __init__(self, host="127.0.0.1"):
        self.baudrate = 9600
        self.comm = 'tcp'
        self.framer = framer
        self.host = host
        self.log = 'INFO'
        self.port = 5020
        self.timeout = 10