# -*- coding: utf-8 -*-

import os, sys, time
import logging
import dbus

__all__ = ['Disks',]

logger = logging.getLogger("Disks")
console = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('%(name)s: %(message)s'))


def extract_string(data):
	s = None
	if len(data):
		s = ''
		for d in data:
			s += d
	return s

class Disks(object):
	INTERFACE = "org.freedesktop.UDisks"
	def __init__(self):
		self.bus = dbus.SystemBus()
		self.proxy = self.bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
		self.udisks = self.dbus.Interface(proxy, self.INTERFACE)

	def list_drives(self):
		data = []
		for dev in udisks.EnumerateDevices():
			device_obj = self.bus.get_object("org.freedesktop.UDisks", dev)
			device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
			device = {
				'model': device_props.Get(self.INTERFACED+'.Device', "DriveModel"),
				'mount_path': extract_string( device_props.Get(self.INTERFACE+'.Device', "DeviceMountPaths") ),
				'serial': device_props.Get(self.INTERFACE+'.Device', "DriveSerial"),
				'dev_file': device_props.Get(self.INTERFACE+'.Device', "DeviceFile"),
				'size': device_props.Get(self.INTERFACE+'.Device', "PartitionSize"),
				'slave_of': device_props.Get(self.INTERFACE+'.Device', 'PartitionSlave'),
				'fs': device_props.Get(self.INTERFACE+'.Device', 'IdType'),
				'uuid': device_props.Get(self.INTERFACE+'.Device', 'IdUuid'),
				'label': device_props.Get(self.INTERFACE+'.Device', 'IdLabel'),
				'flags': extract_string(device_props.Get(self.INTERFACE+'.Device', 'PartitionFlags')),
				'detach': device_props.Get(self.INTERFACE+'.Device', 'DriveCanDetach'),
			}
			data.append(device)
		return data

	def print_drives(self):
		data = self.list_drives()
		for d in data:
			print
			for k,v in d.items():
				print "%s: %s"%(k,v)


# vim:ts=3:sts=3:sw=3:noexpandtab
