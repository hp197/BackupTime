#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, time
import argparse
import logging
import pprint
#from dbus import glib
#import gobject
import dbus

logger = logging.getLogger("foo")
console = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('%(name)s: %(message)s'))

__all__ = ['']

def extract_string(data):
	s = None
	if len(data):
		s = ''
		for d in data:
			s += d
	return s

def dbus_handler(*args, **keywords):
	print args, keywords

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Does something', prog='ProgName')
	parser.add_argument('--version', action='version', version='%(prog)s 01')
	parser.add_argument('--source', '-s', dest='source_dir', default='foo', type=str, help="Foo Bar")

	options = parser.parse_args()
	
	bus = dbus.SystemBus()
	proxy = bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
	udisks = dbus.Interface(proxy, 'org.freedesktop.UDisks')

	data = []
	for dev in udisks.EnumerateDevices():
		device_obj = bus.get_object("org.freedesktop.UDisks", dev)
		device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
		device = {
			'model': device_props.Get('org.freedesktop.UDisks.Device', "DriveModel"),
			'mount_path': extract_string( device_props.Get('org.freedesktop.UDisks.Device', "DeviceMountPaths") ),
			'serial': device_props.Get('org.freedesktop.UDisks.Device', "DriveSerial"),
			'dev_file': device_props.Get('org.freedesktop.UDisks.Device', "DeviceFile"),
			'size': device_props.Get('org.freedesktop.UDisks.Device', "PartitionSize"),
			'slave_of': device_props.Get('org.freedesktop.UDisks.Device', 'PartitionSlave'),
			'fs': device_props.Get('org.freedesktop.UDisks.Device', 'IdType'),
			'uuid': device_props.Get('org.freedesktop.UDisks.Device', 'IdUuid'),
			'label': device_props.Get('org.freedesktop.UDisks.Device', 'IdLabel'),
			'flags': extract_string(device_props.Get('org.freedesktop.UDisks.Device', 'PartitionFlags')),
			'detach': device_props.Get('org.freedesktop.UDisks.Device', 'DriveCanDetach'),
		}
		data.append(device)

	for d in data:
		print
		for k,v in d.items():
			print "%s: %s"%(k,v)

	system_bus.add_signal_receiver(vpn_connection_handler,
    dbus_interface="org.freedesktop.UDisks",
        signal_name="/org/freedesktop/UDisks")


# vim:ts=3:sts=3:sw=3:noexpandtab
