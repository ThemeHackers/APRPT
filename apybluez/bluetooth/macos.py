import lightblue
from .btcommon import *

def discover_devices(duration=8, flush_cache=True, lookup_names=False,
        lookup_class=False, device_id=-1):
    btAddresIndex = 0
    namesIndex = 1
    classIndex = 2

    devices = lightblue.finddevices(getnames=lookup_names, length=duration)

    ret = list()
    for device in devices:
        item = [device[btAddresIndex], ]
        if lookup_names:
            item.append(device[namesIndex])
        if lookup_class:
            item.append(device[classIndex])

        if len(item) == 1:
            ret.append(item[0])
        else:
            ret.append(tuple(item))
    return ret


def lookup_name(address, timeout=10):
    print("TODO: implement")

def find_service(name=None, uuid=None, address=None):
    if address is not None:
        addresses = [address]
    else:
        addresses = discover_devices(lookup_names=False)

    results = []

    for address in addresses:

        dresults = lightblue.findservices(addr=address, name=name)

        for tup in dresults:
            service = {}

            service["host"] = tup[0]
            service["port"] = tup[1]
            service["name"] = tup[2]

            service["description"] = None
            service["provider"] = None
            service["protocol"] = None
            service["service-classes"] = []
            service["profiles"] = []
            service["service-id"] = None

            results.append(service)

    return results


def read_local_bdaddr():
    return [lightblue.gethostaddr()]


def advertise_service(sock, name, service_id="", service_classes=None,
        profiles=None, provider="", description="", protocols=None):

    if protocols is None or protocols == RFCOMM:
        protocols = [lightblue.RFCOMM]

    lightblue.advertise(name, sock, protocols[0], service_id)


def stop_advertising(sock):
    lightblue.stop_advertising(sock)


class BluetoothSocket:

    def __init__(self, proto=RFCOMM, _sock=None):
        if _sock is None:
            _sock = lightblue.socket()
        self._sock = _sock

        if proto != RFCOMM:
            raise NotImplementedError("Not supported protocol")
        self._proto = lightblue.RFCOMM
        self._addrport = None

    def _getport(self):
        return self._addrport[1]

    def bind(self, addrport):
        self._addrport = addrport
        return self._sock.bind(addrport)

    def listen(self, backlog):
        return self._sock.listen(backlog)

    def accept(self):
        return self._sock.accept()

    def connect(self, addrport):
        return self._sock.connect(addrport)

    def send(self, data):
        return self._sock.send(data)

    def recv(self, numbytes):
        return self._sock.recv(numbytes)

    def close(self):
        return self._sock.close()

    def getsockname(self):
        return self._sock.getsockname()

    def setblocking(self, blocking):
        return self._sock.setblocking(blocking)

    def settimeout(self, timeout):
        return self._sock.settimeout(timeout)

    def gettimeout(self):
        return self._sock.gettimeout()

    def fileno(self):
        return self._sock.fileno()

    def dup(self):
        return BluetoothSocket(self._proto, self._sock)

    def makefile(self, mode, bufsize):
        return self.makefile(mode, bufsize)


class DeviceDiscoverer:
    def __init__ (self):
        raise NotImplementedError
