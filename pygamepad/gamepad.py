#!/usr/bin/python
#
# Simple class for the Logitech F310 Gamepad.
# Needs pyusb library.
#

import usb
import struct

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
        #conf = d.configurations[0]
        #intf = conf.interfaces[0][0]
        self._dev = d.open()
        #print(self._dev.dev)
        try:
            self._dev.detachKernelDriver(0)
        except usb.core.USBError:
            print("error detaching kernel driver (usually no problem)")
        except AttributeError:
            pass
        #handle.interruptWrite(0, 'W')
        self._dev.setConfiguration(1)
        self._dev.claimInterface(0)

        #This value has to be send to the gamepad, or it won't start working
        # value was determined by sniffing the usb traffic with wireshark
        # getting other gamepads to work might be a simple as changing this
        self._dev.interruptWrite(0x02,struct.pack('<BBB', 0x01,0x03,0x04))

    def _read_gamepad(self):
        self.changed = 0
        try:
            data = self._dev.interruptRead(0x81,0x20,2000)
            data = struct.unpack('<'+'B'*20, data)
            for i in range(20):
                self._old_state[i] = self._state[i]
                self._state[i] = data[i]
            #print(self._state[:])
            self.changed = 1
        except usb.core.USBError:
            pass
        return True

    def X_was_released(self):
        if (self._state[3] != 64) & (self._old_state[3] == 64):
            return True
        return False

    def Y_was_released(self):
        if (self._state[3] != 128) & (self._old_state[3] == 128):
            return True
        return False

    def A_was_released(self):
        if (self._state[3] != 16) & (self._old_state[3] == 16):
            return True
        return False

    def B_was_released(self):
        if (self._state[3] != 32) & (self._old_state[3] == 32):
            return True
        return False


    def get_state(self):
        return self._state[:]

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

    def get_analogR_x(self):
        return self._state[11]

    def get_analogR_y(self):
        return self._state[12]

    def get_analogL_x(self):
        return self._state[6]

    def get_analogL_y(self):
        return self._state[8]

    def get_dir_up(self):
        return self._state[2] in (1,5,9)

    def get_dir_down(self):
        return self._state[2] in (2,6,10)

    def get_dir_left(self):
        return self._state[2] in (4,5,6)

    def get_dir_up(self):
        return self._state[2] in (8,9,10)

    def changed(self):
        return pad.changed

    def __del__(self):
        if not self._dev is None:
            self._dev.releaseInterface()
            self._dev.reset()

# Unit test code
if __name__ == '__main__':
    pad = None

    pad = Gamepad()
    while True:
        if pad.changed == 1:
            print(pad._state[:])
            #print("analog R: {0:3}|{1:3}  analog L: {2:3}|{3:3}".format(pad.get_analogR_x(),pad.get_analogR_y(),pad.get_analogL_x(),pad.get_analogL_y()))
            #pass