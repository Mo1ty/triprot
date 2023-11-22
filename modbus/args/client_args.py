class ClientArgs:
    def __init__(self, host="127.0.0.1"):
        self.baudrate = 9600
        self.comm = 'tcp'
        self.framer = Framer()
        self.host = host
        self.log = 'INFO'
        self.port = 5020
        self.timeout = 10


class Framer:
    def __init__(self, method="socket", name=""):
        self.method = method
        self.name = name
