#!/usr/bin/python3
import imp
modules = set(["subprocess", "virtkey", "configparser", "os"])
for m in modules:
	try:
		imp.find_module(m)
	except ImportError:
		print("Dependency problem!")
		print("Can't load or missing package: " + m)
		exit()

import subprocess
import virtkey
import configparser
import os

baseDist = 0.1 # Influences Treshold
tresholdRate = 0.4
timedif = 0.4 # Zeit in Sekunden Zwischen moeglichen Aktionen

hist = [ [[],[]], [[],[]], [[],[]], [[],[]], [[],[]] ] # Array fuer History 1 bis 5, wobei 1 index 0 hat
lasttime = 0.0

def stringToKeys(keys):
	ret = []
	for key in keys.split():
		ret.append(int(key, 16))
	return ret

def parseConfig():
	config = configparser.ConfigParser()
	config.read(os.environ['HOME'] + '/.pySwipe/pySwipe.ini')
	fingers = {}
	for section in config.sections():
		fingers[(section, 'down')] = stringToKeys(config.get(section, 'down'))
		fingers[(section, 'up')] = stringToKeys(config.get(section, 'up'))
		fingers[(section, 'right')] = stringToKeys(config.get(section, 'right'))
		fingers[(section, 'left')] = stringToKeys(config.get(section, 'left'))
	return fingers

def detect(finger):
	global data
	global hist
	rate = '0'
	axis = '0'
	touchstate = 0
	cleanHistButNot(finger)
	if finger > 0 and finger <= len(hist):
		hist[finger-1][0].insert(0, int(data[1]))
		hist[finger-1][1].insert(0, int(data[2]))
		del hist[finger-1][0][10:]
		del hist[finger-1][0][10:]
		axis = getAxis(hist[finger-1][0], hist[finger-1][1], 5, 0.5);
		if axis == 'x':
			rate = getRate(hist[finger-1][0])
			touchstate = finger
		elif axis == 'y':
			rate = getRate(hist[finger-1][1])
			touchstate = finger
	return [axis, rate, touchstate]

def cleanHistButNot(hn):
	global hist
	for i in range(5):
		if hn != i+1:
			hist[i][0] = []
			hist[i][1] = []			

def getAxis( histx, histy, maxim, tresholdRate):
	if len(histx) > maxim and len(histy) > maxim:
		x0 = histx[0]
		y0 = histy[0]
		xmax = histx[maxim]
		ymax = histy[maxim]
		xdist = abs(x0 - xmax)
		ydist = abs(y0 - ymax)
		if xdist > ydist:
			if xdist > xMinThreshold * tresholdRate:
				return 'x';
			else:
				return 'z'
		else:
			if ydist > yMinThreshold * tresholdRate:
				return 'y';
			else:
				return 'z'
	return '0'

def getRate(hist):
	histsrt = list(hist)
	histsrt.sort()
	histsrtrev = list(hist)
	histsrtrev.sort(reverse = True)
	if hist == histsrt:
		return '+'
	elif hist == histsrtrev:
		return '-'
	return '0'

def pressKeys(keys):
	global v
	if len(keys) > 0:
		v.press_keysym(keys[0])
		pressKeys(keys[1:])
		v.release_keysym(keys[0])
def main ():
	global data
	global TouchpadSizeH
	global TouchpadSizeW
	global xMinThreshold
	global yMinThreshold
	global vscrolldelta
	global hscrolldelta
	global v


	#def parseTouchConfig()
	synvars = {}
	p1 = subprocess.Popen(['synclient', '-l'], stdout=subprocess.PIPE)
	for line in p1.stdout:
		line = str(line, encoding='utf8').split()
		if len(line) == 3:
			synvars[line[0]] = line[2]
	p1.stdout.close()
	p1.wait()

	LeftEdge = int(synvars['LeftEdge'])
	RightEdge = int(synvars['RightEdge'])
	TopEdge = int(synvars['TopEdge'])
	BottomEdge = int(synvars['BottomEdge'])

	TouchpadSizeH = BottomEdge - TopEdge
	TouchpadSizeW = RightEdge - LeftEdge
	xMinThreshold = TouchpadSizeW * baseDist;
	yMinThreshold = TouchpadSizeH * baseDist;

	vscrolldelta = int(synvars['VertScrollDelta'])
	hscrolldelta = int(synvars['HorizScrollDelta'])

	print("LeftEdge: " + str(LeftEdge))
	print("RightEdge: " + str(RightEdge))
	print("TopEdge: " + str(TopEdge))
	print("BottomEdge: " + str(BottomEdge))
	print("TouchpadSizeH: " + str(TouchpadSizeH))
	print("TouchpadSizeW: " + str(TouchpadSizeW))
	print("xMinThreshold: " + str(xMinThreshold))
	print("yMinThreshold: " + str(yMinThreshold))
	print("VScroll: " + str(vscrolldelta))
	print("HScroll: " + str(hscrolldelta))


	print("End of Initialisation")
	print()
	time = 0
	lasttime = -1

	#Get Finger Configuration
	fingers = parseConfig()

	v = virtkey.virtkey()
	p = subprocess.Popen(['synclient -m 10'], stdout=subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
	for line in p.stdout:
		data = str(line, encoding='utf8' ).split() 
		#	0	1	2	3	4	5	6	7	8	9	10	11	12	13	14	15	16
		#	time	x	y	z	f	w	l	r	u	d	m	multi	gl	gm	gr	gdx	gdy
	#	print(data);
		if data[0] == 'time':
			continue
		elif data[0] == 'Parameter':
			continue
		else:
			time = float(data[0])
		action = ['0', '0', 0] #  [axis, rate, touchstate] 
		if data[4] == '1':
			cleanHistButNot(1)
		elif data[4] == '2':
			cleanHistButNot(2)
		elif data[4] == '3':
			action = detect(3)
		elif data[4] == '4':
			action = detect(4)
		elif data[4] == '5':
			action = detect(5)

	

		if not (action[0] == '0') and (time - lasttime) > timedif:
			cleanHistButNot(0)
			if action[2] == 3:
				if action[0] == 'y' and action[1] == '+':		#Up
					#print("Up")
					pressKeys(fingers[('3', 'up')])
				elif action[0] == 'y' and action[1] == '-':	#Down
					#print("Down")
					pressKeys(fingers[('3', 'down')])
				elif action[0] == 'x' and action[1] == '+':
					#print("Left")
					pressKeys(fingers[('3', 'left')])
				elif action[0] == 'x' and action[1] == '-':
					#print("Right")
					pressKeys(fingers[('3', 'right')])
			elif action[2] == 4:
				if action[0] == 'y' and action[1] == '+':		#Up
					#print("Up")
					pressKeys(fingers[('4', 'up')])
				elif action[0] == 'y' and action[1] == '-':	#Down
					#print("Down")
					pressKeys(fingers[('4', 'down')])
				elif action[0] == 'x' and action[1] == '+':
					#print("Left")
					pressKeys(fingers[('4', 'left')])
				elif action[0] == 'x' and action[1] == '-':
					#print("Right")
					pressKeys(fingers[('4', 'right')])
			elif action[2] == 5:
				if action[0] == 'y' and action[1] == '+':		#Up
					#print("Up")
					pressKeys(fingers[('5', 'up')])
				elif action[0] == 'y' and action[1] == '-':	#Down
					#print("Down")
					pressKeys(fingers[('5', 'down')])
				elif action[0] == 'x' and action[1] == '+':
					#print("Left")
					pressKeys(fingers[('5', 'left')])
				elif action[0] == 'x' and action[1] == '-':
					#print("Right")
					pressKeys(fingers[('5', 'right')])

			lasttime = time
	p.stdout.close()
	p.wait()

if __name__ == "__main__":
    main()
