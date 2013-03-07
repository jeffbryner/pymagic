#!/usr/bin/env python2
import os
import sys
import re
import string 

"""
Builds a reasonable version of a magic list from sys-apps/file's Magdir/magic files
to build, steal Magdir from the unix file program and point this program to it: 
makemagic.py Magdir/* >magictests.py

Warning: This doesn't handle all cases. Only handles the initial search bits like this: 
0	belong		0x00010008	GEM Image data

Not this with subsequent searches: 
0	string/b	MZ
!:mime	application/x-dosexec
# All non-DOS EXE extensions have the relocation table more than 0x40 bytes into the file.
>0x18	leshort <0x40 MS-DOS executable
# These traditional tests usually work but not always.  When test quality support is
# implemented these can be turned on.
#>>0x18	leshort	0x1c	(Borland compiler)
#>>0x18	leshort	0x1e	(MS compiler)

Hand edit anything obvious that's missing (like MZ) or tests you don't want

"""
def strToNum(n):
    val = 0
    col = long(1)
    if n[:1] == 'x': n = '0' + n
    if n[:2] == '0x':
        # hex
        n = string.lower(n[2:])
        while len(n) > 0:
            l = n[len(n) - 1]
            val = val + string.hexdigits.index(l) * col
            col = col * 16
            n = n[:len(n)-1]
    elif n[0] == '\\':
        # octal
        n = n[1:]
        while len(n) > 0:
            l = n[len(n) - 1]
            if ord(l) < 48 or ord(l) > 57: break
            val = val + int(l) * col
            col = col * 8
            n = n[:len(n)-1]
    else:
        val = string.atol(n)
    return val

files=sys.argv[1::]
print('magic = [')
for afile in files: 
    f=open(afile)
    magics=f.readlines()
    for m in magics:
        if len(m.strip())>1 and m[0] not in ('#','>','<','!'):
            if '\t' in m:
                mguts=m.split('\t')
                pos=mguts[0]
                datatype=mguts[1]
                desc=mguts[::-1][0]
                try:
                    mguts.remove(pos)
                    mguts.remove(datatype)
                    mguts.remove(desc)            
                    magic=''.join(mguts)
                    magic=magic.replace("'","\'")
                    desc=desc.strip()
                    desc=desc.replace("'","")
                    if len(magic.strip())>0 and len(desc.strip())>0:
                        if datatype in ('long'):
                            print("[%dL ,'%s', '=',%dL , '%s'],"%(strToNum(pos),datatype,magic.encode('string_escape'),desc))
                        else:
                            print("[%dL ,'%s', '=','%s' , '%s'],"%(strToNum(pos),datatype,magic.encode('string_escape'),desc))
                            
                except Exception as e:
                    sys.stderr.write('%r handling %r\n'%(e,m))
                    continue
    f.close()

print(']')