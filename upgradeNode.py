#!/usr/bin/env python



global serverIp

global login

global pwd

global logTitle

global sshNewkey

global node

global image

global session

global esxiDefaultPrompt

global shellPrompt

global mgtUl

global rtrImagePath





login = 'regress'

pwd = 'MaRtInI'

sshServer = login + '@' 

sshNewkey = 'Are you sure you want to continue connecting'

rtrImagePath = '/var/tmp'

shellPrompt = '%'

oprtnlPrompt = '>'

configPrompt = '#'







def UserPref():

	import sys

	import getpass

	import os



	node = raw_input("\n Enter node to upgrade [hostname or IP] : ")

	
	imageTag = raw_input("\n Enter image [eg: 14.2X1.1] : ")

	imagePath = raw_input("\n Enter complete image path [eg: /volume/build/junos/14.2/service/14.2X1.1/ship/jinstall-14.2X1.1-domestic-signed.tgz] : ")

	head, image = os.path.split(os.path.split(imagePath)[1])



	shellServer = raw_input("\n Enter shell server to copy image from [eg: ttsv-shell09] : ")

	linuxLogin = raw_input("\n Enter linux account username : ")

	linuxPwd  = getpass.getpass("\n Enter linux account password : ")


	#node = '192.168.183.74'
	#image = '14.2X1.1'

	#selection.rstrip()

	print "\n Logging into : ",node
	print " Required image : ",image

	return (node, imageTag, imagePath, image, shellServer, linuxLogin, linuxPwd)




def CreateLogFile():

	import datetime

	now = datetime.datetime.now() 

	logTitle = 'UpgradeLog'

	logExtnsn = '.log'

	logFile = "%s_%.2i-%.2i-%i_%.2i-%.2i-%.2i" % (logTitle,now.day,now.month,now.year,now.hour,now.minute,now.second)

	logFile = logFile + logExtnsn

	print "\t => Session captures in log file = ",logFile

	return logFile




def LoginServer(logFile, node):

		import pexpect

		global session

		sshServer = login + '@' + node

		session=pexpect.spawn("ssh %s" %sshServer)

		session.logfile= open(logFile, "w")

		chkKey=session.expect([sshNewkey,'Password:',pexpect.EOF,pexpect.TIMEOUT],90) #0 if no key, 1 if has key

		if chkKey==0 :

				print "\n\t => IP not known - Adding SSH key"

				session.sendline("yes")

				chkKey=session.expect([sshNewkey,'Password:',pexpect.EOF])

		if chkKey==1:

				print "\n\t => SSH key known - Proceeding with password authentication"

				session.sendline("%s" %pwd)

				session.expect("%s" %shellPrompt)

				session.sendline("cli")

				session.expect("%s" %oprtnlPrompt)

				session.sendline("set cli screen-width 200")

				return session

				

		elif chkKey==2:

			print "\n\t => Connection timeout"

			pass

	


def ChkVersion(session, imageTag, logFile):

		import pexpect

		import re

		import sys

		loadImage = 0

		#print "\t\t Step 1 => Check current image on the router"

		print "\t\t => Check current image on the router"

		session.timeout=250

		#chkRtr = ['show version | match Junos: ','show chassis hardware | match routing','show chassis hardware | match routing | count ' ]		

		chkVer = 'show version | match Junos:'

		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)

		#session.sendline("\r")

		session.sendline("%s \r" %chkVer)

		session.sendline("\r")		


		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)


		#handle = open ("%s" %logFile,"r")

		handle = file(logFile).read().split('\n')
		
		for i, line in enumerate(handle):

			if chkVer in line:
				
				if 'Junos' in handle[i + 1]:
					print "\t\t\t   Currently loaded image =>  ", handle[i + 1]

					if imageTag in handle[i + 1]:
						print "\n\t\t => Check desired image on the router"
						sys.exit("\t\t\t   Image loaded successfully, exiting script ...\n")

					break

				
				




def CopyImage (session, logFile, imagePath, image, shellServer, linuxLogin, linuxPwd):

		import pexpect

		import re

		import os

		fromPath = linuxLogin + '@' + shellServer + ':' + imagePath 

		#toPath =  sshServer + ':' + rtrImagePath

		print "\n\t\t Step 1 => Copy desired image to the router"

		session.timeout=250


		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)

		#session.sendline("\r")

		session.sendline("start shell \r")

		session.sendline("\r")		


		session.sendline("\r")

		session.expect("%s \r" %shellPrompt)

		session.sendline("cd %s\r" %rtrImagePath)

		session.expect("%s \r" %shellPrompt)


		session.sendline("\r")

		session.expect("%s \r" %shellPrompt)

		session.sendline("scp %s %s \r" %(fromPath,rtrImagePath))

		#session.expect("%s \r" %shellPrompt)

		chkKey=session.expect([sshNewkey,'[pP]assword:',pexpect.EOF,pexpect.TIMEOUT],90) #0 if no key, 1 if has key

		if chkKey==0 :

				print "\t\t\t=> IP not known - Adding SSH key for SCP"

				session.sendline("yes")

				chkKey=session.expect([sshNewkey,'[pP]assword:',pexpect.EOF])

		if chkKey==1:

				print "\t\t\t=> SSH key known - Proceeding with password authentication for SCP"

				session.sendline("%s" %linuxPwd)

				session.expect("%s" %shellPrompt)

		elif chkKey==2:

			print "\n\t => Connection timeout"

			pass
					
		session.expect("%s" %shellPrompt)

		session.sendline("cli")

		session.expect("%s" %oprtnlPrompt)

		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)


		#head, tail = os.path.split(os.path.split(imagePath)[1])

		tail = image

		print("\t\t\t=> Checking if file %s copied to %s on the router ..." %(tail,rtrImagePath))

		chkImage = "file list /var/tmp | match " + tail + " | no-more"


		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("\r")

		session.sendline("%s \r" %chkImage)

		session.sendline("\r")
		
		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("set cli timestamp\r")

		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("\r")


		#handle = open ("%s" %logFile,"r")

		#matchImage = r'(.*)' + re.escape(tail) + r'(.*)'

		handle = file(logFile).read().split('\n')
		
		for i, line in enumerate(handle):

			if chkImage in line:
				
				if tail in handle[i + 1]:
					print "\t\t\t\tImage copied successfully ! =>  ", handle[i + 1]
					break

				




def DisRed(session, logFile):

		import pexpect

		import re

		import sys

		loadImage = 0

		print "\n\t\t Step 2 => Disable chassis redundancy"

		session.timeout=250

		#chkRtr = ['show version | match Junos: ','show chassis hardware | match routing','show chassis hardware | match routing | count ' ]		


		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)

		#session.sendline("\r")

		session.sendline("edit \r")

		session.expect("%s \r" %configPrompt)

		session.sendline("\r")

		session.expect("%s \r" %configPrompt)


		session.sendline("deactivate chassis redundancy \r")

		session.expect("%s \r" %configPrompt)

		session.sendline("\r")

		session.expect("%s \r" %configPrompt)


		session.sendline("commit and-quit \r")

		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)


		session.sendline("show configuration chassis redundancy | no-more \r")

		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)





def UpgradeRE(session, logFile, image):

		import pexpect

		import re

		import sys

		loadImage = 0

		print "\n\t\t Step 3 => Upgrade RE with ", image

		print "\t\t\t=> Wait time approximately 10 mins ..."

		session.timeout=250

		#chkRtr = ['show version | match Junos: ','show chassis hardware | match routing','show chassis hardware | match routing | count ' ]		

		upgradePath = rtrImagePath + '/' + image

		upgradeRE = 'request system software add ' + upgradePath + ' no-validate reboot'

		session.sendline("\r")

		session.expect("%s \r" %oprtnlPrompt)


		session.sendline("%s \r" %upgradeRE)

		session.expect("%s \r" %oprtnlPrompt)

		session.sendline("\r")

		




def main ():

	import time

	(node, imageTag, imagePath, image, shellServer, linuxLogin, linuxPwd) = UserPref()

	print "\n ***** Initiating upgrade procedure  ***** \n"

	logFile = CreateLogFile()

	session = LoginServer(logFile,node)

	ChkVersion(session, imageTag, logFile)

	CopyImage (session, logFile, imagePath, image, shellServer, linuxLogin, linuxPwd)

	DisRed(session, logFile)

	UpgradeRE(session, logFile, image)

	time.sleep(600)

	logFile = CreateLogFile()

	session = LoginServer(logFile,node)

	ChkVersion(session, imageTag, logFile)

	print "\n ***** Completed upgrade ***** \n"


	



main()



