# -*- encoding: utf-8 -*-

import sys, os, threading
import time
import subprocess as SP

class ProcessRunner(object):
	def __init__(self):
		self.thread = threading.Thread(target=self._work)
		self.thread.deamon = True
		self.running = True
		self.p = None
		self.queue = []

	def start(self, cmd):
		assert( isinstance(cmd, (list, tuple)) )
		self.p = SP.Popen(cmd, stdout=SP.PIPE)
		self.thread.start()

	def _work(self):
		while self.running:
			line = self.p.stdout.readline()
			if line != '':
				self.queue.append(line)
			else:
				if self.p.poll() != None:
					print "Process done"
					self.running = False
				#time.sleep(0.010)
		
	def stop(self):
		self.running = False
		self.thread.join()

	def ended(self):
		self.p.poll()
		return (self.p.returncode != None) and (not self.running)

	def has_line(self):
		return len(self.queue) > 0

	def get_line(self):
		return self.queue.pop(0)

	def returncode(self):
		return self.p.returncode

class Operations(object):
	LATEST_DIR = 'latest'
	def create_btrfs(self, device, label):
		assert( isinstance(device, basestring) )
		assert( device.startswith('/dev/') )
		cmd = ('mkfs.btrfs', '-L%s'%label, str(device))
		ok, ret = self._call(cmd)
		if ok:
			lines = ret.split('\n')
			ret = [x for x in lines if x.startswith('fs created')]
			return ret[0]
		else:
			return False

	def mkdir_mountpoint(self, mountpoint):
		assert( isinstance(mountpoint, basestring) )
		cmd = ('mkdir', '%s'%mountpoint)
		ok, ret = self._call(cmd)
		return ok

	def mount_backup(self, device, directory):
		assert( isinstance(device, basestring) )
		assert( device.startswith('/dev/') )
		cmd = ('mount','-tbtrfs','-ogroup,compress=lzo,user_subvol_rm_allowed,autodefrag,inode_cache', 
				device, directory)
		ok, ret = self._call(cmd)
		return ok

	def prepare_fs(self, backup_base_dir):
		cmd = ('/sbin/btrfs', 'subvolume', 'create', os.path.join(backup_base_dir, self.LATEST_DIR))
		ok, ret = self._call(cmd)
		return ok

	def unmount_backup(self, device):
		assert( isinstance(device, basestring) )
		assert( device.startswith('/dev/') )
		cmd = ('umount', device)
		ok, ret = self._call(cmd)
		return ok

	def create_snapshot(self, unix_time, backup_base):
		destname = "backup_%d"%int(unix_time)
		cmd = ('/sbin/btrfs', 'subvolume', 'snapshot', 
				os.path.join(backup_base, self.LATEST_DIR), os.path.join(backup_base, destname))
		ok, ret = self._call(cmd)
		if ok and ret == '\n':
			return True
		else:
			return False
	
	def delete_snapshot(self, unix_time, backup_base):
		volname = "backup_%d"%int(unix_time)
		volname = os.path.join(backup_base, volname)
		print "Deleting: %s"%volname
		cmd = ('/sbin/btrfs', 'subvolume', 'delete', volname)
		ok, ret = self._call(cmd)
		return ok

	def sync_dryrun(self, source_dir, backup_base_dir):
		#erst --dry-run zum berechnen des gesamtfortschritts und dann ohne
		excludes = ('foo', 'bar')
		excludes = ['--exclude=%s'%x for x in excludes]
		cmd = ['rsync','-avzpHAX','--skip-compress=jpg:mpg:avi:mp3',
				'--one-file-system', 
				'--inplace',
				'--delete',
				'--delete-excluded',
				'--exclude=backup',
				'--dry-run',
			source_dir,
			os.path.join(backup_base_dir, self.LATEST_DIR)
		      ]
		cmd.extend( excludes )	
		ok, ret = self._call(cmd)
		ret = ret.split('\n')
		return ok, len(ret)

	def sync_data(self, source_dir, backup_base_dir, progress_func):
		excludes = ('backup', 'bar')
		excludes = ['--exclude=%s'%x for x in excludes]
		cmd = ['rsync','-avzpHAX','--skip-compress=jpg:mpg:avi:mp3',
				'--one-file-system', 
				'--inplace',
				'--delete',
				'--delete-excluded',
				'--exclude=backup',
			source_dir,
			os.path.join(backup_base_dir, self.LATEST_DIR)
		      ]
		cmd.extend( excludes )	

		pr = ProcessRunner()
		pr.start(cmd)
		progress = 0
		while not pr.ended():
			while pr.has_line():
				progress_func(progress)
				line = pr.get_line()
				#print line
				progress += 1
			time.sleep(0.020)
		return pr.returncode() == 0

	def _call(self, cmd):
		p = SP.Popen(cmd, stdout=SP.PIPE)
		ret = p.communicate()[0]
		return ((p.returncode == 0), ret)


