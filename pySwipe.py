#!/usr/bin/python3
import imp
modules = set(["subprocess", "virtkey"])
for m in modules:
	try:
		imp.find_module(m)
	except ImportError:
		print("Dependency problem!")
		print("Can't load or missing package: " + m)
		exit()

import subprocess
import virtkey

baseDist = 0.1 # Influences Treshold
tresholdRate = 0.4
timedif = 0.4 # Zeit in Sekunden Zwischen moeglichen Aktionen

hist = [ [[],[]], [[],[]], [[],[]], [[],[]], [[],[]] ] # Array fuer History 1 bis 5, wobei 1 index 0 hat
lasttime = 0.0

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

	# eckengrenzen
	p1 = subprocess.Popen(['synclient', '-l'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', 'Edge'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['grep', '-v', '-e', 'Area', '-e', 'Motion', '-e', 'Scroll'], stdin=p2.stdout,stdout=subprocess.PIPE)
	p2.stdout.close()
	for line in p3.stdout:
		data = str(line, encoding='utf8').split()
		if data[0] == 'LeftEdge':
			LeftEdge = int(data[2])
		elif data[0] == 'RightEdge':
			RightEdge = int(data[2])
		elif data[0] == 'TopEdge':
			TopEdge = int(data[2])
		elif data[0] == 'BottomEdge':
			BottomEdge = int(data[2])
	p3.stdout.close()
	p1.wait()
	p2.wait()
	p3.wait()
	#LeftEdge
	#RightEdge
	#TopEdge
	#BottomEdge
	#TouchpadSizeH
	TouchpadSizeH = BottomEdge - TopEdge
	TouchpadSizeW = RightEdge - LeftEdge
	xMinThreshold = TouchpadSizeW * baseDist;
	yMinThreshold = TouchpadSizeH * baseDist;
	print("LeftEdge: " + str(LeftEdge))
	print("RightEdge: " + str(RightEdge))
	print("TopEdge: " + str(TopEdge))
	print("BottomEdge: " + str(BottomEdge))
	print("TouchpadSizeH: " + str(TouchpadSizeH))
	print("TouchpadSizeW: " + str(TouchpadSizeW))
	print("xMinThreshold: " + str(xMinThreshold))
	print("yMinThreshold: " + str(yMinThreshold))

	# Scrolldeltas
	p1 = subprocess.Popen(['synclient', '-l'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', 'ScrollDelta'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['grep', '-v', '-e', 'Circ'], stdin=p2.stdout,stdout=subprocess.PIPE)
	p2.stdout.close()
	for line in p3.stdout:
		data = str(line, encoding='utf8').split()
		if data[0] == 'VertScrollDelta':
			vscrolldelta = int(data[2])
		elif data[0] == 'HorizScrollDelta':
			hscrolldelta = int(data[2])
	p3.stdout.close()
	print("VScroll: " + str(vscrolldelta))
	print("HScroll: " + str(hscrolldelta))


	print("End of Initialisation")
	print()
	p1.wait()
	p2.wait()
	p3.wait()
	time = 0
	lasttime = -1
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
					pressKeys([0xffeb, 0xff55])
				elif action[0] == 'y' and action[1] == '-':	#Down
					#print("Down")
					pressKeys([0xffeb, 0xff56])
				elif action[0] == 'x' and action[1] == '+':
					#print("Left")
					pressKeys([])
				elif action[0] == 'x' and action[1] == '-':
					#print("Right")
					pressKeys([])
			elif action[2] == 4:
				if action[0] == 'y' and action[1] == '+':		#Up
					#print("Up")
					pressKeys([0xffeb, 0xff52])
				elif action[0] == 'y' and action[1] == '-':	#Down
					#print("Down")
					pressKeys([0xffeb, 0xff54])
				elif action[0] == 'x' and action[1] == '+':	#left
					#print("Left")
					pressKeys([0xffeb, 0xff51])
				elif action[0] == 'x' and action[1] == '-':	#right
					#print("Right")
					pressKeys([0xffeb, 0xff53])
			elif action[2] == 5:
				if action[0] == 'y' and action[1] == '+':		#Up
					#print("Up")
					pressKeys([])
				elif action[0] == 'y' and action[1] == '-':	#Down
					#print("Down")
					pressKeys([])
				elif action[0] == 'x' and action[1] == '+':	#left
					#print("Left")
					pressKeys([])
				elif action[0] == 'x' and action[1] == '-':	#right
					#print("Right")
					pressKeys([])

			lasttime = time
	p.stdout.close()
	p.wait()

if __name__ == "__main__":
    main()
