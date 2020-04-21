import sys
from datetime import datetime
import serial
import png

#start and stop marker in PCL
marker  = [0x1B, 0x2A, 0x62, 0x36, 0x38, 0x57]
stop    = [0x1B, 0x2A, 0x72, 0x42, 0x0D, 0x0A]
#68 bytes per line (68*8 columns)
cols    = 68
#show progress?
verbose = 1
#invert colors?
invert  = 1

#buffers
buff=[0]*6
line=[0]*cols
img =[]
#printed lines counter
lines = 0

now = datetime.now()
fname = now.strftime("SCR_%d%m%Y_%H%M%S.png")

#configure the serial connection
ser = serial.Serial(
    port=sys.argv[1],
    baudrate=19200,
    #timeout=1
)

if not ser.isOpen():
    ser.open()

if len(sys.argv)!=2:
    print('Usage:')
    print('python HP5400B.py COM1')

print('Set print format to ""HP print"" [Print|Utility], [Hardcopy menu]')
print('Then, press [Print|Utility], [Print Screen]')

while True:
    #wait for marker
    for i in range(5):
        buff[i]=buff[i+1]
    
    buff[5]=int.from_bytes(ser.read(1), "little")

    if buff==marker:
        for i in range(cols):
            line[i]=int.from_bytes(ser.read(1), "little")

        row = []
        for i in range(cols):
            for j in range(8):
                if invert==0:
                    v = ((line[i]>>(7-j))&1)*255
                else:
                    v = (1-((line[i]>>(7-j))&1))*255
                row.append(v)
        img.append(row)
            
        lines = lines + 1

        if verbose==1:
            print('\r', '[%3.0f%%] Printing line %3d of 280...' % (lines/2.8, lines), end='')

    if buff==stop:
        f = open(fname, 'wb')
        w = png.Writer(cols*8, 280, greyscale=True)
        w.write(f, img)
        f.close()
        ser.close()
        print('\n')
        print('Done!'),
        sys.exit()
