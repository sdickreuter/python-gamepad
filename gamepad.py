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

    def __init__(self):
        busses = usb.busses()
        for bus in busses:
            devs = bus.devices
            for dev in devs:
                if dev.idVendor == 0x046d and dev.idProduct == 0xc21d:
                    d = dev
        conf = d.configurations[0]
        intf = conf.interfaces[0][0]
        self._dev = d.open()
        try:
            self._dev.detachKernelDriver(0)
        except usb.core.USBError:
            print("error detaching kernel driver (usually no problem)")
        #handle.interruptWrite(0, 'W')
        self._dev.claimInterface(0)

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
            try:
                data = self._dev.interruptRead(0x81,0x20,500)
                self._state = struct.unpack('<'+'B'*20, data)
                print(self._state)
                self.changed = 1
            except usb.core.USBError:
                data = None
                self.changed = 0
            #connection.send(data)
            #running = connection.recv()
        return True

    def __del__(self):
        self._worker.join(0.2)
        self._dev.releaseInterface()
        self._dev.reset()




# Unit test code
if __name__ == '__main__':
   pad = Gamepad()
   while True:
      if pad.changed == 1:
        print(pad._state[:])
