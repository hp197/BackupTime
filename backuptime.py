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

def progress(complete, partial):
	print "   %d\x0D"%((float(partial)/complete)*100),

if __name__ == "__main__":

	MOUNT_DEFAULT = '/media/backup'
	SOURCE_DEFAULT = '/usr/src/linux-3.0.0-39-obj'
	DRIVE_DEFAULT = '/dev/sdb'

	parser = argparse.ArgumentParser(description='Do an incremental backup', prog='BackupTime')
	parser.add_argument('--version', action='version', version='%(prog)s 01')
	subparsers = parser.add_subparsers(help='Sub-Commands', dest='subcommand')

	parser_ld  = subparsers.add_parser('ld', help='List drives')

	parser_prep = subparsers.add_parser('prepare', help='Prepare Drive')
	parser_prep.add_argument('--drive', '-d', dest='drive', default=DRIVE_DEFAULT, type=str, help="Disk drive where the backups should be put to. Default: %s"%DRIVE_DEFAULT)
	parser_prep.add_argument('--mountpoint', '-m', dest='backup_dir', default=MOUNT_DEFAULT, type=str, help="Where to mount the backup volume. Default: %s"%MOUNT_DEFAULT)

	parser_back = subparsers.add_parser('backup', help='Do the Backup')
	parser_back.add_argument('--source', '-s', dest='source_dir', default=SOURCE_DEFAULT, type=str, help="What to backup")
	parser_back.add_argument('--dest', '-d', dest='backup_dir', default=MOUNT_DEFAULT, type=str, help="Mount point of the backup volume")

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
			op.prepare_fs(options.backup_dir)

		sys.exit(0)

	if options.subcommand == 'backup':
		lines = 0
		if 1:
			logger.info("* prepare rsync")
			ok, ret = op.sync_dryrun(options.source_dir, options.backup_dir)
			lines = ret
			logger.info("Lines: %s"%ret)
		if 1:
			logger.info("* Doing rsnc")
			ret = op.sync_data(options.source_dir, options.backup_dir, lambda x: progress(lines, x))
			logger.info(ret)
		if 1:
			logger.info("* Creating snapshot")
			ret = op.create_snapshot(time.time(), options.backup_dir)
			logger.info(ret)

		sys.exit(0)

	if options.subcommand == 'delete':
		logger.info("Deleting snapshot backup_%d"%options.date)
		ret = op.delete_snapshot(options.date, options.backup_dir)
		logger.info(ret)

		sys.exit(0)

# vim:ts=3:sts=3:sw=3:noexpandtab
