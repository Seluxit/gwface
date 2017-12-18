
# Hierarchical data representation
#
# - gateway
# + network
#   + device
#       + status
#       + service
#           + value
#       + configuration
#           + partner
#           + action
#           + calendar
#           + calculation
#           + timer
#           + statemachine


# JsonRPC representation
#
# Example:
# {"id":"1234565","jsonrpc":"2.0", "method":"POST","params":{"data":{....},"url":"/network/91f8b08a-a661-4997-973b-fd118a86d7d4/device"}}
# 

# Base class - contains data, url from jsonrpc represenation and parent 
class Item:
    def __init__(self, data, url, parent):
        self.data = data
        self.id = data[":id"]
        self.parent = parent
        self.url = url
    @property
    def id(self):
        return self.id 
    @property
    def url(self):
        return self.url
    @property
    def data(self):
        return self.data
    @data.setter
    def data(self, data):
        self.data = data
    @property
    def parent(self):
        return self.parent
    def __str__(self):
        return " url: " + self.url + "/" + self.id

# Model ------------------ 
class Gateway(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
        self.time_zone = data["time_zone"]
    def __str__(self):
        return "Gateway time_zone: '" + self.time_zone + "' " + Item.__str__(self)

class Network(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
        self.name = data["name"]
    def __str__(self):
        return "Network name: '" + self.name + "' " + Item.__str__(self)

class Device(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
        self.name = data["name"]
    def __str__(self):
        return "Device name: '" + self.name + "' " + Item.__str__(self)

class Service(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
        self.name = data["name"]
    @property
    def name(self):
        return self.name
    def __str__(self):
        return "Service name: '" + self.name + "' " + Item.__str__(self)

class Value(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
        self.data = data["data"]
    def __str__(self):
        return "Value data: " + self.data + Item.__str__(self)

class Configuration(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
        self.status = data["status"]
    @property
    def status(self):
        return self.status
    def __str__(self):
        return "Configuration status: " + self.status + Item.__str__(self)

class Partner(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
        self.partner = data["device_id"]
    @property
    def partner(self):
        return self.partner
    def __str__(self):
        return "Partner device: " + self.parent + Item.__str__(self)

class Action(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
    def __str__(self):
        return "Action " + Item.__str__(self)

class Calendar(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
    def __str__(self):
        return "Calendar " + Item.__str__(self)

class Calculation(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
    def __str__(self):
        return "Calculation " + Item.__str__(self)

class Timer(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
    def __str__(self):
        return "Timer " + Item.__str__(self)

class StateMachine(Item):
    def __init__(self, data, url, parent):
        Item.__init__(self, data, url, parent)
    def __str__(self):
        return "StateMachine " + Item.__str__(self)

