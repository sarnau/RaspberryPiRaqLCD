# Simple Python Script to demo the jog wheel on the Pi-raq from Earthlcd.com
# 
#
#
# Ken Segler
# ken@earthlcd.com
#
import RPi.GPIO as GPIO
import sys
import time
import signal
import curses
import psutil

BackLight = 27
Center = 23
Rot1 = 22
Rot2 = 24
Down = 25
Right = 20
Up = 21
Left = 26
currentMenu = 1	

def ShowMenu():
	global currentMenu
	if currentMenu == 1:
		stdscr.addstr(1, 2, " System Info     ", curses.A_REVERSE and curses.color_pair(3))
	else:
		stdscr.addstr(1, 2, " System Info     ")	

	if currentMenu == 2:
		stdscr.addstr(2, 2, " Menu Two        ", curses.A_REVERSE and curses.color_pair(3))
	else:
		stdscr.addstr(2, 2, " Menu Two        ")	
		
	if currentMenu == 3:
		stdscr.addstr(3, 2, " Menu Three      ", curses.A_REVERSE and curses.color_pair(3))
	else:
		stdscr.addstr(3, 2, " Menu Three      ")	
		
	if currentMenu == 4:
		stdscr.addstr(4, 2, " Menu Four       ", curses.A_REVERSE and curses.color_pair(3))
	else:
		stdscr.addstr(4, 2, " Menu Four       ")	
		
	if currentMenu == 5:
		stdscr.addstr(5, 2, " Backlight Level ", curses.A_REVERSE and curses.color_pair(3))
	else:
		stdscr.addstr(5, 2, " Backlight Level ")	

	stdscr.refresh()
def	JogCenter(channel):
	temp = psutil.disk_usage('/')
	if currentMenu == 1:
		stdscr.addstr(1, 20, str(temp).strip('[]'))	
	stdscr.refresh()
def	JogLeft(channel):
	stdscr.refresh()
def	JogRight(channel):
	stdscr.refresh()
def	JogUp(channel):
	global currentMenu
	currentMenu -= 1
	if  currentMenu == 0:
		currentMenu = 5
	ShowMenu()
def	JogDown(channel):
	global currentMenu
	currentMenu += 1
	if  currentMenu == 6:
		currentMenu = 1
	ShowMenu()
def	JogRot(channel):
	global currentMenu
	if (GPIO.input(Rot1) == 0 and GPIO.input(Rot2) == 1) or (GPIO.input(Rot1) == 1 and GPIO.input(Rot2) == 0):
		currentMenu += 1
		if  currentMenu == 6:
			currentMenu = 1
		ShowMenu()
	if (GPIO.input(Rot1) == 0 and GPIO.input(Rot2) == 0) or (GPIO.input(Rot1) == 1 and GPIO.input(Rot2) == 1):
		currentMenu -= 1
		if  currentMenu == 0:
			currentMenu = 5
		ShowMenu()

def signal_handler(signal, frame):
	curses.endwin()
	GPIO.cleanup()
	print('\nBYE\n')
	sys.exit(0)

stdscr = curses.initscr()
curses.start_color()
curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
curses.noecho() 
curses.curs_set(0) 
stdscr.keypad(1)


stdscr.clear()
stdscr.refresh()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BackLight, GPIO.OUT)  # backlight
GPIO.setup(Center, GPIO.IN)  # Center Button
GPIO.setup(Rot1, GPIO.IN)  # Rot1
GPIO.setup(Rot2, GPIO.IN)  # Rot2
GPIO.setup(Down, GPIO.IN)  # Down
GPIO.setup(Right, GPIO.IN)  # Right
GPIO.setup(Up, GPIO.IN)  # Up
GPIO.setup(Left, GPIO.IN)  # Left

GPIO.output(BackLight, 1)
GPIO.add_event_detect(Center, GPIO.FALLING, callback=JogCenter, bouncetime=100)
GPIO.add_event_detect(Left, GPIO.FALLING, callback=JogLeft, bouncetime=100)
GPIO.add_event_detect(Right, GPIO.FALLING, callback=JogRight, bouncetime=100)
GPIO.add_event_detect(Up, GPIO.FALLING, callback=JogUp, bouncetime=100)
GPIO.add_event_detect(Down, GPIO.FALLING, callback=JogDown, bouncetime=100)	
GPIO.add_event_detect(Rot1, GPIO.BOTH, callback=JogRot, bouncetime=10)		
signal.signal(signal.SIGINT, signal_handler)
stdscr.border(0)
ShowMenu()


while True:
	time.sleep(100)
	
	
