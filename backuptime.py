#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#mööp

import os, sys, time
import argparse
import logging

LOGLEVEL = logging.DEBUG

logger = logging.getLogger("backuptime")
console = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(console)
logger.setLevel(LOGLEVEL)
console.setLevel(LOGLEVEL)
console.setFormatter(logging.Formatter('%(name)s: %(message)s'))

__all__ = ['']

from operations import Operations


if __name__ == "__main__":

	MOUNT_DEFAULT = '/media/backup'
	SOURCE_DEFAULT = '/usr/src/linux-3.0.3-41-obj/'
	DRIVE_DEFAULT = '/dev/sdb'

	parser = argparse.ArgumentParser(description='Do an incremental backup', prog='BackupTime')
	parser.add_argument('--version', action='version', version='%(prog)s 01')
	subparsers = parser.add_subparsers(help='Sub-Commands', dest='subcommand')

	parser_ld  = subparsers.add_parser('ld', help='List drives')

	parser_prep = subparsers.add_parser('prepare', help='Prepare Drive')
	parser_prep.add_argument('--drive', '-d', dest='drive', default=DRIVE_DEFAULT, type=str, help="Disk drive where the backups should be put to. Default: %s"%DRIVE_DEFAULT)
	parser_prep.add_argument('--mountpoint', '-m', dest='backup_dir', default=MOUNT_DEFAULT, type=str, help="Where to mount the backup volume. Default: %s"%MOUNT_DEFAULT)

	parser_back = subparsers.add_parser('backup', help='Do the Backup')
	parser_back.add_argument('--drive', '-d', dest='drive', type=str, help="Disk drive where the backups should be put to. Default: %s"%DRIVE_DEFAULT)
	parser_back.add_argument('--source', '-s', dest='source_dir', type=str, help="What to backup")
	#parser_back.add_argument('--dest', '-d', dest='backup_dir', default=MOUNT_DEFAULT, type=str, help="Mount point of the backup volume")

	parser_del  = subparsers.add_parser('delete', help='Delete a Backup')
	parser_del.add_argument('--date', '-t', dest='date', type=int, required=True, help="Unix time of the backup to delete")
	parser_del.add_argument('--dest', '-d', dest='backup_dir', default=MOUNT_DEFAULT, type=str, help="Mount point of the backup volume")

	options = parser.parse_args()
	#print
	#print "Options:",options
	#print

	op = Operations()

	if options.subcommand == 'ld':
		from disks import Disks
		disks = Disks()
		for i, dinfo in enumerate(disks.list_devices()):
			print "%2d. Device: %s   Label: %s"%(i+1, dinfo.dev_file(), dinfo.label())

	if options.subcommand == 'prepare':
		latest_dir = os.path.join(options.backup_dir, 'latest')
		if 1:
			logger.info("* Unmounting Volume")
			ret = op.unmount_backup(options.drive)
			logger.info(ret)
		if 1:
			logger.info("* Creating Volume")
			ret = op.create_btrfs(options.drive, 'backup_volume')
			logger.info(ret)
		if not os.path.exists(options.backup_dir):
			logger.info("* mkdir mountpoint")
			ret = op.mkdir_mountpoint(options.backup_dir)
			logger.info(ret)
		if 1:
			logger.info("* Mounting backup volume")
			ret = op.mount_backup(options.drive, options.backup_dir)
			logger.info(ret)
		if 1:
			logger.info("* Creating Subvolume")
			ret = op.create_subvol(latest_dir)
			logger.info(ret)

		sys.exit(0)

	if options.subcommand == 'backup':
		from disks import Disks
		disks = Disks()
		di = disks.create_disk_info( options.drive )
		if not di.mount_path():
			raise Exception("Drive %s is not mounted"%options.drive)
	
		from backup import Backup
		backup = Backup(di, options.source_dir)
		backup.do_backup()

		sys.exit(0)

	if options.subcommand == 'delete':
		voldir = "backup_%d"%int(options.date)
		voldir = os.path.join(options.backup_dir, voldir)
		logger.info("Deleting snapshot %s"%voldir)
		ret = op.delete_snapshot(voldir)
		logger.info(ret)

		sys.exit(0)

# vim:ts=3:sts=3:sw=3:noexpandtab
