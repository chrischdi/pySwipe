pySwipe
=======

Python script to enable swipe gestures on a touchpad.

# Prerequisites
* aur/python-virtkey (to simulate shortcuts)
* aur/xf86-input-synaptics-xswipe-git (to get use of the removed "-m" option of synclient)

# How to
1. Install prerequisites
2. Grab the pySwipe.py script
3. Edit the script to match your shortcut keys (You can find the symkeys in /usr/include/X11/keysymdef.h or get it via the command "xev")
4. Start pySwipe

# Todo
* Make config file to read keys from
* More comments
