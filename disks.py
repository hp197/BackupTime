#!/usr/bin/python
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

class DiskInfo(object):
	UDISKS_DEV_IF = 'org.freedesktop.UDisks.Device'

	def __init__(self, device_obj):
		self.device_obj = device_obj
		self.device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)

	def create_filesystem(self, fstype, options = []):
		assert(isinstance(disk_info, DiskInfo))
		device = self.get_dbus_dev(disk_info.dev_file)
		return device.FilesystemCreate(fstype, options)

	def mount_filesystem(self, mountpoint, options = []):
		fstype = 'btrfs'
		return self.device_obj.FilesystemMount(fstype, options, mountpoint)



	def model(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, "DriveModel")

	def is_mounted(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, 'DeviceIsMounted') == 1
	
	def mount_path(self):
		str_arr = self.device_props.Get(self.UDISKS_DEV_IF, "DeviceMountPaths") 
		return extract_string( str_arr )

	def serial(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, "DriveSerial")
			
	def dev_file(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, "DeviceFile")
			
	def size(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, "PartitionSize")
			
	def slave_of(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, 'PartitionSlave')
	
	def fs(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, 'IdType')
			
	def uuid(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, 'IdUuid')
	
	def label(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, 'IdLabel')

	def flags(self):
		str_arr = self.device_props.Get(self.UDISKS_DEV_IF, 'PartitionFlags')
		return extract_string(str_arr)

	def can_detach(self):
		return self.device_props.Get(self.UDISKS_DEV_IF, 'DriveCanDetach') == 1

	def is_drive(self):
		self.device_props.Get(self.UDISKS_DEV_IF, 'DeviceIsDrive') == 1

	def __repr__(self):
		ret = ""
		ret += "model: %s\n"%self.model()
		ret += "is mounted: %s\n"%self.is_mounted()
		ret += "mount path: %s\n"%self.mount_path()
		ret += "serial: %s\n"%self.serial()
		ret += "dev file: %s\n"%self.dev_file()
		ret += "size: %s\n"%self.size()
		ret += "slave of: %s\n"%self.slave_of()
		ret += "fs: %s\n"%self.fs()
		ret += "uuid: %s\n"%self.uuid()
		ret += "label: %s\n"%self.label()
		ret += "flags: %s\n"%self.flags()
		ret += "can detach: %s\n"%self.can_detach()
		ret += "is drive: %s\n"%self.is_drive()
		return ret

class Disks(object):
	UDISKS_IF = "org.freedesktop.UDisks"

	def __init__(self):
		self.bus = dbus.SystemBus()
		self.proxy = self.bus.get_object(self.UDISKS_IF, "/org/freedesktop/UDisks")
		self.udisks = dbus.Interface(self.proxy, self.UDISKS_IF)

	def list_devices(self):
		data = []
		for dev in self.udisks.EnumerateDevices():
			device_obj = self.bus.get_object(self.UDISKS_IF, dev)
			
			dinfo = DiskInfo(device_obj)
			data.append(dinfo)
		return data

	def get_dbus_dev(self, devfile):
		ret = self.udisks.FindDeviceByDeviceFile(devfile)
		return DiskInfo(device_obj)


if __name__ == '__main__':
	disks = Disks()
	drives = disks.list_devices()
	for d in drives:
		print d

# vim:ts=3:sts=3:sw=3:noexpandtab
