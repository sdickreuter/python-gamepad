#!/usr/bin/python
#
# Simple class for the Logitech F310 Gamepad.
# Needs pyusb library.
#

import usb
import struct
import multiprocessing

USB_VENDOR = 0x046d
USB_PRODUCT = 0xc21d


class Gamepad(object):

    def __init__(self, callback = None):
        self.callback = callback
        busses = usb.busses()
        for bus in busses:
            devs = bus.devices
            for dev in devs:
                if dev.idVendor == 0x046d and dev.idProduct == 0xc21d:
                    d = dev
        #conf = d.configurations[0]
        #intf = conf.interfaces[0][0]
        self._dev = d.open()
        try:
            self._dev.detachKernelDriver(0)
        except usb.core.USBError:
            print("error detaching kernel driver (usually no problem)")
        #handle.interruptWrite(0, 'W')
        self._dev.claimInterface(0)

        #This value has to be send to the gamepad, or it won't start working
        # value was determined by sniffing the usb traffic with wireshark
        # getting other gamepads to work might be a simple as changing this
        self._dev.interruptWrite(0x02,struct.pack('<BBB', 0x01,0x03,0x04))

        self._state = multiprocessing.Array('i', [0,]*20 )
        self.changed = multiprocessing.Value('i', 0)

        self.master_conn, self.slave_conn = multiprocessing.Pipe()
        self._worker = multiprocessing.Process(target=self._read_gamepad, args=(self.slave_conn,))
        self._worker.daemon = True
        self._worker.start()

    def _read_gamepad(self, connection):
        running = True
        data = None
        while running:
            self.changed.value = 0
            try:
                data = self._dev.interruptRead(0x81,0x20,2000)
                data = struct.unpack('<'+'B'*20, data)
                for i in range(20):
                    self._state[i] = data[i]
                #print(self._state)
                self.changed.value = 1
                if self.callback is not None:
                    self.callback()
            except usb.core.USBError:
                data = None
            #connection.send(data)
            #running = connection.recv()
        return True

    def get_LB(self):
        return self._state[3] == 1

    def get_RB(self):
        return self._state[3] == 2

    def get_A(self):
        return self._state[3] == 16

    def get_B(self):
        return self._state[3] == 32

    def get_X(self):
        return self._state[3] == 64

    def get_Y(self):
        return self._state[3] == 128

    def get_analogL_x(self):
        return self._state[11]

    def get_analogL_y(self):
        return self._state[12]

    def get_analogR_x(self):
        return self._state[6]

    def get_analogR_y(self):
        return self._state[8]

    def __del__(self):
        self._worker.join(0.2)
        self._dev.releaseInterface()
        self._dev.reset()

# Unit test code
if __name__ == '__main__':
   pad = Gamepad()
   while True:
      if pad.changed.value == 1:
        #print(pad._state[:])
        print("analog R: {0:3}|{1:3}  analog L: {2:3}|{3:3}".format(pad.get_analogR_x(),pad.get_analogR_y(),pad.get_analogL_x(),pad.get_analogL_y()))
