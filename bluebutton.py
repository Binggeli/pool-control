#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import time
from asyncore import file_dispatcher, loop
from evdev import list_devices, InputDevice, ecodes
from pump import run_pump

BUTTON = "b8:27:eb:ad:f4:81"


def find_button(address):
    for fn in list_devices():
        device = InputDevice(fn)
        if device is not None and device.phys == address:
            print("Found device %s" % device.name)
            return device
    return None


class InputDeviceDispatcher(file_dispatcher):
    def __init__(self, device):
        self.device = device
        file_dispatcher.__init__(self, device)

    def recv(self, ign=None):
        return self.device.read()

    def handle_read(self):
        for event in self.recv():
            if event.type == ecodes.EV_KEY:
                if event.code == 115 and event.value == 1:
                    PoolTrigger(True, 200, 30).save()
                    run_pump(True)
                if event.code == 28 and event.value == 1:
                    PoolTrigger(False, 200, 30).save()
                    run_pump(False)
                print(repr(event))


try:
    while True:
        button = find_button(BUTTON)
        if button:
            InputDeviceDispatcher(button)
        loop()
except KeyboardInterrupt:
    print('Program stopped by Keyboard Interrupt')
    exit(0)
except Exception as exception:
    print('Program stopped by exception {0:s}'.format(exception))
    exit(1)
