pySwipe
=======

Python script to enable swipe gestures on a touchpad.

# Prerequisites
* aur/python-virtkey (to simulate shortcuts)
* aur/xf86-input-synaptics-xswipe-git (to get use of the removed "-m" option of synclient)
* python-configparser (in arch python-configobj)

# How to
1. Install prerequisites
2. Grab the pySwipe.py script
3. Place the pySwipe.ini to $HOME/.pySwipe/pySwipe.ini
4. Edit pySwipe.ini to match your shortcut keys (You can find the symkeys in /usr/include/X11/keysymdef.h or get it via the command "xev")
5. Start pySwipe

# Todo
* More comments
