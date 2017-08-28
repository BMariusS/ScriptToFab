from fabric.api import *
import time

#VARIABLES

env.hosts=["localhost"]
env.user="marius"
env.password="rootTest"

SSHOPTIONS="-o ConnectTimeout=900 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=10"
TESTDEPLOYCYCLE=False
logFile = "/tmp/logFile.txt"

def deploy_tests(LOCAL_REQUIRED_FOLDER, REMOTE_IP):
	mountTry = 0
	with settings(warn_only=True):
		while (mountTry<2):
			mount = run("mount -o remout, rw /")
			run("echo '%s' >> %s" % (mount, logFile))
			if mount.return_code == 0:
				run("echo 'Mount success' >> %s" % logFile)
				break
			if mount.return_code !=0 and mountTry == 1:
				run("echo 'Error at mounting' >> %s" % logFile)
				raise SystemExit()
			mountTry += 1


		remove = run("rm -RF /media/ssd/CVTESTS && rm -RF /media/ssd/Tools && sync && mkdir -p /media/ssd/CVTESTS && mkdir -p /media/ssd/Tools")
		run("echo '%s' >> %s" % (remove, logFile))
		if remove.return_code == 0:
			run("echo 'Remove old tests ...' >> %s" % logFile)
		else:
			run("echo 'Failed to remove old tests' >> %s" % logFile)
			raise SystemExit()


		makeFileSystem = run("mkfs.btrfs -f /dev/ssd")
		run("echo '%s' >> %s" % (makeFileSystem, logFile))
		if makeFileSystem.return_code == 0:
			run("echo 'Made file system' >> %s" % logFile)
		else:
			run("echo 'Failed to make file system' >> %s" % logFile)
			raise SystemExit()
		run("sync")
		local("sync")


		with cd("%s/validation/target" % LOCAL_REQUIRED_FOLDER):
			secureCopy = local("scp %s -rv `ls | grep '"'opt'"' ` root@%s" % (SSHOPTIONS, REMOTE_IP))
			run("echo '%s' >> %s" % (secureCopy, logFile))
			if secureCopy.return_code == 0:
				run("echo 'Copied with success' >> %s" % logFile)
			else:
				run("echo 'Failed to copy' >> %s" % logFile)
				raise SystemExit()
			time.sleep(5)
			
			runScript = run("bash /opt/scripts/scriptAutoEnv.sh")
			run("echo '%s' >> %s" % (runScript, logFile))
			if runScript.return_code == 0:
				run("echo 'Ran script with success' >> %s" % logFile)
			else:
				run("echo 'Failed to run the script' >> %s" % logFile)
				raise SystemExit()
			time.sleep(3)
			
			secureCopyMedia = local("scp %s -rv `ls | grep '"'media'"' ` root@%s" % (SSHOPTIONS, REMOTE_IP))
			run("echo '%s' >> %s" % (secureCopyMedia, logFile))
			if secureCopyMedia.return_code == 0:
				run("echo 'Copied media with success' >> %s" % logFile)
			else:
				run("echo 'Failed to copy media' >> ^%s" % logFile)
				raise SystemExit()
			time.sleep(5)
			
			scriptRun = run("bash /opt/scripts/scriptAutoEnv.sh")
			run("echo '%s' >> %s" % (scriptRun, logFile))
			if scriptRun.return_code == 0:
				run("echo 'Ran script second time with success' >> %s" % logFile)
			else:
				run("echo 'Failed to run the script the second time' >> %s" % logFile)
				raise SystemExit()
		run("sync")
		local("sync")

			


def call_all(LOCAL_REQUIRED_FOLDER, REMOTE_IP):
	with settings(warn_only=True):
		mountedSSD = run("[[ `mount | grep ssd | wc -l` -ge 1 ]] && echo SSD mounted || echo SSD not mounted! ; exit 1")
		run("echo '%s' > %s" % (mountedSSD, logFile))
		if mountedSSD.return_code == 0:
			run("echo 'SSD mounted' >> %s" % logFile)
		else:
			run("echo 'Error at ssd mounting' >> %s" % logFile)
			raise SystemExit()
		while(TESTDEPLOYCYCLE == False):
			tests = deploy_tests(LOCAL_REQUIRED_FOLDER, REMOTE_IP)
			if tests.return_code == 0:
				TESTDEPLOYCYCLE = True
	run("echo 'Deploying tests & validation configurations to target!' >> %s" % logFile)
	run("sync")
	local("sync")
	time.sleep(5)
	run("echo 'Done' >> %s" % logFile)

