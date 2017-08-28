from fabric.api import *


#VARIABLES

SSHOPTIONS="-o ConnectTimeout=900 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=10"
TESTDEPLOYCYCLE=False

def deploy_tests(LOCAL_REQUIRED_FOLDER):
	mountTry = 0
	with settings(warn_only=True):
		while (mountTry<2):
			mount = run("mount -o remout, rw /")
			if mount.return_code == 0:
				run("echo 'Mount success'")
				break
			if mount.return_code !=0 and mountTry == 1:
				run("echo 'Error at mounting'")
				raise SystemExit()
			mountTry += 1


		remove = run("rm -RF /media/ssd/CVTESTS && rm -RF /media/ssd/Tools && sync && mkdir -p /media/ssd/CVTESTS && mkdir -p /media/ssd/Tools")
		if remove.return_code == 0:
			run("echo 'Remove old tests ...'")
		else:
			run("echo 'Failed to remove old tests'")
			raise SystemExit()


		makeFileSystem = run("mkfs.btrfs -f /dev/ssd")
		if makeFileSystem.return_code == 0:
			run("echo 'Made file system'")
		else:
			run("echo 'Failed to make file system'")
			raise SystemExit()
		run("sync")


		with cd("%s/validation/target" % LOCAL_REQUIRED_FOLDER):
			secureCopy = run("scp %s -rv `ls | grep '"'opt'"' `" % SSHOPTIONS)
			if secureCopy.return_code == 0:
				run("echo 'Copied with success'")
			else:
				run("echo 'Failed to copy'")
				raise SystemExit()
			run("sleep 5")
			
			runScript = run("bash /opt/scripts/scriptAutoEnv.sh")
			if runScript.return_code == 0:
				run("echo 'Ran script with success'")
			else:
				run("echo 'Failed to run the script'")
				raise SystemExit()
			run("sleep 3")
			
			secureCopyMedia = run("scp %s -rv `ls | grep '"'media'"' `" % SSHOPTIONS)
			if secureCopyMedia.return_code == 0:
				run("echo 'Copied media with success'")
			else:
				run("echo 'Failed to copy media'")
				raise SystemExit()
			run("sleep 5")
			
			scriptRun = run("bash /opt/scripts/scriptAutoEnv.sh")
			if scriptRun.return_code == 0:
				run("echo 'Ran script second time with success'")
			else:
				run("echo 'Failed to run the script the second time'")
				raise SystemExit()
		run("sync")

			


def call_all(LOCAL_REQUIRED_FOLDER):
	with settings(warn_only=True):
		mountedSSD = run("[[ `mount | grep ssd | wc -l` -ge 1 ]] && echo SSD mounted || echo SSD not mounted! ; exit 1")
		if mountedSSD.return_code == 0:
			run("echo 'SSD mounted'")
		else:
			run("echo 'Error at ssd mounting'")
			raise SystemExit()
		while(TESTDEPLOYCYCLE == False):
			tests = deploy_tests(LOCAL_REQUIRED_FOLDER)
			if tests.return_code == 0:
				TESTDEPLOYCYCLE = True
	run("echo 'Deploying tests & validation configurations to target!'")
	run("sync")
	run("sleep 5")
	run("echo 'Done'")
				



