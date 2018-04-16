#!/usr/bin/env  python
import socket
import os
import sys
import json
import time
import signal
from random import randint
from Queue import Queue
from threading import Thread
import model
from time import sleep

# A thread-safe FIFO implementation           
random_ids = Queue()

gateway = None
network = None
devices = []
services = []
values = []
configurations = []
partners = []
actions = []
calendars = []
calculations = []
timers = []
statemachines = []

class Colors:
    FAIL = '\033[91m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    OKBLUE = '\033[94m'
    ENDC = '\033[0m'

class Listener(Thread):
    def __init__(self, sfile):
        Thread.__init__(self)
        self.sfile = sfile
        if os.path.exists(self.sfile):
            os.remove(self.sfile)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.server.bind(self.sfile)

    def run(self):
        print("Listening ... on '" + self.sfile + "'")
        while True:
            datagram = self.server.recv(2048)
            if not datagram:
                break
            else:
                try:
                    myobject = json.loads(datagram)  
                    if not random_ids.empty():
                        req_id = random_ids.get()
                        res_id  = myobject["id"]
                        print(Colors.WARNING + "Response and Request jsonRPC ids do not match: " + req_id + " " + res_id + Colors.ENDC if req_id != res_id else Colors.OKBLUE + "Got Response" + Colors.ENDC) 

                    if "method" in myobject and myobject["method"] == "POST":
                        print("<--- POST rpc ID: " + myobject["id"] + " url: " + myobject["params"]["url"])
                        update_lists(myobject)
                    elif "method" in myobject and myobject["method"] == "PUT":
                        print("<---- PUT rpc ID: " + myobject["id"] + " url: " + myobject["params"]["url"])
                        update_lists(myobject)
                    elif "method" in myobject and myobject["method"] == "DELETE":
                        print("<---- DELETE rpc ID: " + myobject["id"] + " url: " + myobject["params"]["url"])
                        delete_object(myobject["params"]["url"])
                    elif "result" in myobject:
                        print(Colors.OKBLUE + "Result: " + str(myobject["result"]) + Colors.ENDC)
                    elif "error" in myobject:
                        print(Colors.FAIL + "Error message: " + myobject["error"]["message"] + Colors.ENDC)
                    else:
                        print(Colors.WARNING + "Not implemented!" + Colors.ENDC + " " + myobject)

                except Exception as e:
                    reg_id = random_ids.get()
                    print(Colors.FAIL + "Invalid response: " + str(e) + Colors.ENDC)
                    print(Colors.FAIL + json.dumps(datagram) + Colors.ENDC)

    def __enter__(self):
        return self

    # clean up resources once main  process is killed.
    def __exit__(self, exc_type, exc_value, traceback):
        print("Shutting down Listener ...")
        self.server.close()
        os.remove(self.sfile)
        print("Done")

class Client:
    def __init__(self, sfile):
        self.sfile = sfile
        if not os.path.exists(self.sfile):
            raise "Can NOT find Gateway socket " + self.sfile

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket.connect(sfile)
        self.actions = [
                        self.getAll,
                        self.getDevice,
                        self.getService,
                        self.getValue,
                        self.openValve,
                        self.getConfiguration,
                        self.getPartner,
                        self.getAction,
                        self.getCalendar,
                        self.getCalculation,
                        self.getTimer,
                        self.getMachine,
                        self.getGateway,
                        self.getNetwork,
                        self.getListOfDevices,
                        self.getListOfServices,
                        self.getListOfConfigurations,
                        self.getListOfPartners,
                        self.getListOfActions,
                        self.getListOfCalendars,
                        self.getListOfCalculations,
                        self.getListOfTimers,
                        self.getListOfStatemachines,
                        self.postHomekit
                       ]
        self.iterator = enumerate(self.actions)

    def includeDevice(self, item):
        random_id = str(randint(1000, 9999))
        print("")
        print("---------------- Include device request PUT " + item.__class__.__name__ + " ------------------- jsonrpc_id: " + random_id)
        jsonmsg = {}
        jsonmsg["id"] = random_id
        jsonmsg["jsonrpc"] = "2.0"
        jsonmsg["method"] = "PUT"
        jsonmsg["params"] = {}
        jsonmsg["params"]["url"] = item.url + "/" + item.id
        jsonmsg["params"]["data"] = item.data
        self.socket.send(json.dumps(jsonmsg))


    def getAll(self):
        print("")
        print("---------------- Request REPORT ----------------------")
        print("Get all items starting from network then devices, services and values.")
        random_id = str(randint(1000, 9999))
        random_ids.put(random_id)
        self.socket.send('{"id":"' + random_id + '", "jsonrpc":"2.0", "method":"GET", "params":{"url":"/"}}')

    def getGateway(self):
        if network:
            print("---------------- Request GET gateway ------------------- jsonrpc_id: 123456789")
            self.socket.send('{"id":"123456789", "jsonrpc":"2.0", "method":"GET", "params":{"url":"' + "/gateway/" + network.id + '"}}')
        else:
            print(Colors.FAIL + "GET /gateway Error - No network object found!" + Colors.ENDC)

    def getNetwork(self):
        if network:
            self.getRequest(network)
        else:
            print(Colors.FAIL + "GET /network Error - No network object found!" + Colors.ENDC)

    def getDevice(self):
        if devices:
            device = devices[0]
            self.getRequest(device)

    def getListOfDevices(self):
        if network:
            url = network.url + "/" + network.id + "/device"
            self.getListRequest(url)
        else:
            print(Colors.FAIL + "GET /list_of_devices Error - No network object found!" + Colors.ENDC)

    def getService(self):
        if services:
            service = services[-1]
            self.getRequest(service)

    def getValue(self):
        if values:
            value = values[-1]
            self.getRequest(value)

    def getListOfServices(self):
        if devices:
            device = devices[-1]
            url = device.url + "/" + device.id + "/service"
            self.getListRequest(url)

    def getListOfConfigurations(self):
        if devices:
            device = devices[-1]
            url = device.url + "/" + device.id + "/configuration"
            self.getListRequest(url)

    def getListOfPartners(self):
        self.getListOf("partner")

    def getListOfActions(self):
        self.getListOf("action")

    def getListOfCalendars(self):
        self.getListOf("calendar")

    def getListOfCalculations(self):
        self.getListOf("calculation")

    def getListOfTimers(self):
        self.getListOf("timer")

    def getListOfStatemachines(self):
        self.getListOf("statemachine")

    def getListOf(self, item_name):
        if devices and configurations:
            device = devices[0]
            configuration = configurations[-1]
            url = device.url + "/" + device.id + "/configuration/" + configuration.id + "/" + item_name
            self.getListRequest(url)

    def openValve(self):
        # search for service with the name valve_open
        items = [srv for srv in services if srv.name == "valve_open"]
        if items:
            value = [value for value in values if items[0].id == value.parent][0]
            print("Found 'valve_open value with ID: '" + value.id + "'")
            value.data = {"data":"0"}
            self.putRequest(value)
            print("data " + str(value.data))
            time.sleep(2)
            value.data = {"data":"1"}
            self.putRequest(value)
            print("data " + str(value.data))

    def getConfiguration(self):
        if configurations:
            configuration = configurations[-1]
            self.getRequest(configuration)

    def getPartner(self):
        if partners:
            partner = partners[-1]
            self.getRequest(partner)

    def getAction(self):
        if actions:
            action = actions[-1]
            self.getRequest(action)

    def getCalendar(self):
        if calendars:
            calendar = calendars[-1]
            self.getRequest(calendar)

    def getCalculation(self):
        if calculations:
            calculation = calculations[-1]
            self.getRequest(calculation)

    def getTimer(self):
        if timers:
            timer = timers[-1]
            self.getRequest(timer)

    def getMachine(self):
        if statemachines:
            machine = statemachines[-1]
            self.getRequest(machine)

    def putRequest(self, item):
        random_id = str(randint(1000, 9999))
        random_ids.put(random_id)
        print("")
        print("---------------- Request PUT " + item.__class__.__name__ + " ------------------- jsonrpc_id: " + random_id)
        jsonmsg = {}
        jsonmsg["id"] = random_id
        jsonmsg["jsonrpc"] = "2.0"
        jsonmsg["method"] = "PUT"
        jsonmsg["params"] = {}
        jsonmsg["params"]["url"] = item.url + "/" + item.id
        jsonmsg["params"]["data"] = item.data
        self.socket.send(json.dumps(jsonmsg))

    def getRequest(self, item):
        random_id = str(randint(1000, 9999))
        random_ids.put(random_id)
        print("")
        print("---------------- Request GET " + item.__class__.__name__ + " ------------------- jsonrpc_id: " + random_id)
        print(item)
        self.socket.send('{"id":"' + random_id + '", "jsonrpc":"2.0", "method":"GET", "params":{"url":"' +
                         item.url + "/" + item.id + '"}}')

    def getListRequest(self, url):
        random_id = str(randint(1000, 9999))
        random_ids.put(random_id)
        print("")
        print("---------------- Request GET list of " + url + " ------------------- jsonrpc_id: " + random_id)
        self.socket.send('{"id":"' + random_id + '", "jsonrpc":"2.0", "method":"GET", "params":{"url":"' + url + '"}}')

    def postHomekit(self):
        random_id = str(randint(1000, 9999))
        random_ids.put(random_id)
        print("")
        print("---------------- Request POST HomeKit  ------------------- jsonrpc_id: " + random_id)
        jsonmsg = {}
        jsonmsg["id"] = random_id
        jsonmsg["jsonrpc"] = "2.0"
        jsonmsg["method"] = "POST"
        jsonmsg["params"] = {}
        jsonmsg["params"]["url"] = "/homekit"
        jsonmsg["params"]["data"] = {"payload": "X-HM://007JNU5AE7OSX"} 
        self.socket.send(json.dumps(jsonmsg))


    def execute(self):
        fun = next(self.iterator, None)
        if not fun:
            return False 
        # Execute method
        fun[1]()
        return True

# Signal handler for Ctrl-C
def signal_handler(signal, frame):
    print("Exiting")
    sys.exit(0)


def delete_object(url):
    # get UUID from url, search for that device, remove all device children, remove device.
    pass


# For POST and PUT
def update_lists(jsonrpc):
    # safety check omitted for brevity
    data = jsonrpc["params"]["data"]
    url = jsonrpc["params"]["url"]

    # Remove if exist slash at the end of url
    if url.endswith('/'):
        url = url[:-1]

    # if GW posting list of ids 
    if "id" in data:
        for i in data["id"]:
            print(i)
        return

    # else data contain object
    item_id = jsonrpc["params"]["data"][":id"]

    if jsonrpc["method"] == "PUT":
        # url contain UUID at the end
        item = url.split('/')[-2]
        # TODO check what kingd of item and update item
        print(Colors.WARNING + "TODO --- Update item: " + item + Colors.ENDC)
        return

    # else - POST
    item = url.split('/')[-1]  
    parent_id = url.split('/')[-2] 

    if item == "gateway":
        global gateway
        gateway = model.Gateway(data, url, None)
        print(gateway)

    if item == "network":
        global network
        network = model.Network(data, url, None)
        print(network)

    if item == "device":
        device = model.Device(data, url, parent_id)
        if device.data["included"] == "0":
            device.data["included"] = "1"
            client = Client("/tmp/zero_interface")
            client.includeDevice(device)
        else:
            create_update_item(device, devices)
            if device.data['product']:
                print('product: {}'.format(device.data['product']))
            if device.data['version_hardware']:
                print("version_hardware: {}".format(device.data['version_hardware']))
            if device.data['version_stack']:
                print("version_stack: {}".format(device.data['version_stack']))
            if device.data['version_boot']:
                print("version_boot: {}".format(device.data['version_boot']))
            if device.data['version_application']:
                print("version_application: {}".format(device.data['version_application']))


    if item == "service":
        service = model.Service(data, url, parent_id)
        create_update_item(service, services)

    if item == "value":
        value = model.Value(data, url, parent_id)
        create_update_item(value, values)

    if item == "status":
        level = data["level"]
        status_type = data["type"]
        message = data["message"]
        print(Colors.OKGREEN + "Status level: '" + level + "' type: '" + status_type + "' message: '" + message + "'" + Colors.ENDC)

    if item == "configuration":
        configuration = model.Configuration(data, url, parent_id)
        create_update_item(configuration, configurations)

    if item == "partner":
        partner = model.Partner(data, url, parent_id)
        create_update_item(partner, partners)

    if item == "action":
        action = model.Action(data, url, parent_id)
        create_update_item(action, actions)

    if item == "calendar":
        calendar = model.Calendar(data, url, parent_id)
        create_update_item(calendar, calendars)

    if item == "calculation":
        calculation = model.Calculation(data, url, parent_id)
        create_update_item(calculation, calculations)

    if item == "timer":
        timer = model.Timer(data, url, parent_id)
        create_update_item(timer, timers)

    if item == "statemachine":
        machine = model.StateMachine(data, url, parent_id)
        create_update_item(machine, statemachines)


def create_update_item(item, item_list):
    exist = [idx for idx, i in enumerate(item_list) if i.id == item.id]
    name = item.__class__.__name__ 
    if exist:
        print('Replacing ' + name + ' id: ' + item.id)
        item_list[exist[0]] = item 
    else:
        print('Appending '+ name + ' id: ' + item.id)
        item_list.append(item)


def start_listener():
    # initiate constructor using 'with' clause 
    with Listener("/tmp/home_interface") as listener:
        listener.daemon = True
        listener.start()

        time.sleep(1)
        client = Client("/tmp/zero_interface")
        while True:
            if not client.execute():
                break
            time.sleep(1)

        print("")
        print("GET and SET test finished - listen only on incoming messages.")
        while True:
            time.sleep(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    start_listener()
    print("End of Main")

