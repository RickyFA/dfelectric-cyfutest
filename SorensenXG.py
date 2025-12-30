#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

import serial


class SorensenXG(object):
    def __init__(self, port, address=1, baudrate=9600, timeout=1):
        self.port = port
        self.address = address
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        time.sleep(0.5)  # allow device to settle

        # CRITICAL: flush stale data
        # self.ser.reset_input_buffer()
        # self.ser.reset_output_buffer()

        # Force remote mode cleanly
        # self.write("SYST:REM")
        # time.sleep(0.2)

        self.write("*ADR %d" % self.address)

    def disconnect(self):
        if self.ser:
            self.ser.close()
            self.ser = None

    def write(self, cmd):
        """
        Send SCPI command with CR termination.
        """
        if not self.ser:
            raise Exception("Not connected")
        self.ser.write((cmd + "\r").encode("ascii"))
        time.sleep(0.2)

    def query(self, cmd):
        """
        Send SCPI query and read response.
        """
        self.write(cmd)
        time.sleep(0.1)
        response = self.ser.readline()
        return response.decode("ascii").strip()

    # -------- PSU Commands --------

    def identify(self):
        return self.query("*IDN?")

    def set_voltage_limit(self, volts):
        self.write("SOUR:VOLT %.3f" % volts)

    def get_voltage_limit(self):
        return self.query("SOUR:VOLT?")

    def set_current_limit(self, amps):
        self.write("SOUR:CURR %.3f" % amps)

    def get_current_limit(self):
        return self.query("SOUR:CURR?")

    def read_voltage(self):
        return self.query("MEAS:VOLT?")

    def read_current(self):
        return self.query("MEAS:CURR?")

    # def output_on(self):
    #     self.write("OUTP ON")

    # def output_off(self):
    #     self.write("OUTP OFF")
