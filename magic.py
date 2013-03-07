#!/usr/bin/env python 
'''
magic.py
 determines a file type by its magic number

Original version: 
 (C)opyright 2000 Jason Petrone <jp_py@demonseed.net>
 All Rights Reserved

pyIOC version: 
2014 Jeff Bryner

 Command Line Usage: running as `python magic.py file` will print
                     a description of what 'file' is.

 Module Usage:
     magic.whatis(data): when passed a string 'data' containing 
                         binary or text data, a description of
                         what the data is will be returned.

     magic.file(filename): returns a description of what the file
                           'filename' contains.
'''

import re, struct, string
import magictests

__version__ = '0.2'


magicNumbers = []

def is_number(s):
    'check if string is numeric, return bool'
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False
    return True

def numericValue(lit):
    'Return value of numeric literal string or ValueError exception'

    # Handle '0'
    if lit == '0': return 0
    if type(lit) ==int or type(lit)==float:
        return lit
    # Hex/Binary
    litneg = lit[1:] if lit[0] == '-' else lit
    if litneg[0] == '0':
        if litneg[1] in 'xX':
            return int(lit,16)
        elif litneg[1] in 'bB':
            return int(lit,2)

    # Int/Float/Complex
    try:
        return int(lit)
    except ValueError:
        pass
    try:
        return float(lit)
    except ValueError:
        pass
    return complex(lit)

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

def unescape(s):
    # replace string escape sequences
    while 1:
        m = re.search(r'\\', s)
        if not m: break
        x = m.start()+1
        if m.end() == len(s): 
            # escaped space at end
            s = s[:len(s)-1] + ' '
        elif s[x:x+2] == '0x':
            # hex ascii value
            c = chr(strToNum(s[x:x+4]))
            s = s[:x-1] + c + s[x+4:]
        elif s[m.start()+1] == 'x':
            # hex ascii value
            c = chr(strToNum(s[x:x+3]))
            s = s[:x-1] + c + s[x+3:]
        elif ord(s[x]) > 47 and ord(s[x]) < 58:
            # octal ascii value
            end = x
            while (ord(s[end]) > 47 and ord(s[end]) < 58):
                end = end + 1
                if end > len(s) - 1: break
            c = chr(strToNum(s[x-1:end]))
            s = s[:x-1] + c + s[end:]
        elif s[x] == 'n':
            # newline
            s = s[:x-1] + '\n' + s[x+1:]
        else:
            break
    return s

class magicTest:
    def __init__(self, offset, t, op, value, msg, mask = None):
        if t.count('&') > 0:
            mask = strToNum(t[t.index('&')+1:])  
            t = t[:t.index('&')]
        if type(offset) == type('a'):
            self.offset = strToNum(offset)
        else:
            self.offset = offset
        self.type = t.strip()
        self.msg = msg
        self.subTests = []
        self.op = op
        self.mask = mask
        try:
            if type(value)==type('a'):
                self.value=value.decode('string_escape')
                #some file tests escape the space like '\ '; python doesn't need this
                self.value=self.value.replace('\\ ',' ')
                self.value=self.value.replace('\ ',' ')
            else:
                self.value = value
        except:
            self.value=value


    def test(self, data):
        if self.mask:
            data = data & self.mask
        if self.op == '=': 
            if self.value == data: return self.msg
        elif self.op ==  '<':
            pass
        elif self.op ==  '>':
            pass
        elif self.op ==  '&':
            pass
        elif self.op ==  '^':
            pass
        return None

    def compare(self, data):
        #print str([self.type, self.value, self.msg])
        if self.offset< len(data):
            try:
                if self.type == 'string' and self.offset>=0:
                    c = ''; s = ''
                    for i in range(0, len(self.value)+1):
                        if i + self.offset > len(data) - 1: break
                        s = s + c
                        [c] = struct.unpack('c', data[self.offset + i])
                    data = s
                    
                elif 'string' in self.type or 'search' in self.type:
                    if '/' in self.type:
                        #limited search, usually just the first line
                        searchLimit=self.type.split('/')[1]
                        if type(searchLimit)==int:
                            [data]=data.split('\n')[0::searchLimit]
                    if data.count(self.value)>0:          
                        data=data[data.find(self.value):(data.find(self.value)+len(self.value))]
                        
                elif self.type == 'short':
                    [data] = struct.unpack('h', data[self.offset : self.offset + 2])
                    self.value=numericValue(self.value)                
                elif self.type == 'leshort':
                    [data] = struct.unpack('<h', data[self.offset : self.offset + 2])
                    self.value=numericValue(self.value)                
                elif self.type == 'beshort':
                    [data] = struct.unpack('>H', data[self.offset : self.offset + 2])
                    self.value=numericValue(self.value)
                elif self.type== 'byte':
                    [data]=struct.unpack('>B',data[self.offset:self.offset+1])
                elif self.type == 'long':
                    [data] = struct.unpack('l', data[self.offset : self.offset + 4])
                    self.value=numericValue(self.value)
                elif self.type == 'lelong':
                    [data] = struct.unpack('<l', data[self.offset : self.offset + 4])
                    self.value=numericValue(self.value)
                elif self.type == 'ulelong':
                    [data] = struct.unpack('<L', data[self.offset : self.offset + 4])
                    self.value=numericValue(self.value)
                elif self.type == 'belong':
                    [data] = struct.unpack('>l', data[self.offset : self.offset + 4])
                    self.value=numericValue(self.value)
                elif self.type == 'ubelong':
                    [data] = struct.unpack('>L', data[self.offset : self.offset + 4])
                    self.value=numericValue(self.value)
                elif self.type == 'bequad':
                    [data] = struct.unpack('>8s', data[self.offset : self.offset + 8])
                    self.value=numericValue(self.value)                    
                else:
                    print 'UNKNOWN TYPE: ' + self.type 
                    pass
            except ValueError as e :
                #print('%r %r' %(self,e))
                return None
            except Exception as e:
                print('%r %r' %(self,e))
                print str([self.type, self.value, self.msg,self.offset])
                return None
            return self.test(data)


def whatis(data):
    for test in magicNumbers:
        m = test.compare(data)
        if m: return m
    # no matching, magic number. is it binary or text?
    for c in data:
        if ord(c) > 128:
            return 'data'
    # its ASCII, now do text tests
    if string.find('The', data, 0, 8192) > -1:
        return 'English text'
    if string.find('def', data, 0, 8192) > -1:
        return 'Python Source'
    return 'ASCII text'


def testFile(afile):
    try:
        return whatis(open(afile, 'r').read(8192))
    except Exception as e:
        if '[Errno 21] Is a directory' in str(e):
            return 'directory'
        else:
            raise e

import sys
#sort the magic list so more accurate searches come first: 
#sort by 's' in match type so strings come after binary searches like belong, ulelong, etc.
#sort by length of match type string, so string/b comes before string
#sort by length of match value to more specific matches come before less specific matches.
sortedMagic = magictests.magic
sortedMagic.sort(key=lambda x:('s' in x[1][0:1] ,-1*len(x[1]),-1*len(str(x[3])) ))

for m in sortedMagic:
    magicNumbers.append(magicTest(m[0], m[1], m[2], m[3], m[4]))
if __name__ == '__main__':
    import sys
    for arg in sys.argv[1:]:
        msg = testFile(arg)
        if msg:
            print arg + ': ' + msg
        else:
            print arg + ': unknown'