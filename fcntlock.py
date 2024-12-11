import os
import win32con
import pywintypes
import win32file

LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
LOCK_SH = 0  # The default value
LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
LOCK_UN = 4
__overlapped = pywintypes.OVERLAPPED()

def lock(file, flags):
    hfile = win32file._get_osfhandle(file.fileno())
    win32file.LockFileEx(hfile, flags, 0, 0xffff0000, __overlapped)

def unlock(file):
    hfile = win32file._get_osfhandle(file.fileno())
    win32file.UnlockFileEx(hfile, 0, 0xffff0000, __overlapped)

def flock(file, flags):
    if flags & LOCK_UN:
        unlock(file)
    else:
        lock(file, flags)