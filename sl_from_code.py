import golly as g
import gzip

chars = "0123456789abcdefghijklmnopqrstuvwxyz"

def decodeCanon(apgcode):
   
    blank = False
    x = y = 0
    clist = []
   
    for c in apgcode[apgcode.find("_")+1:]:
        if blank:
            x += chars.index(c)
            blank = False
        else:
            if (c == 'y'):
                x += 4
                blank = True
            elif (c == 'x'):
                x += 3
            elif (c == 'w'):
                x += 2
            elif (c == 'z'):
                x = 0
                y += 5
            else:
                v = chars.index(c)
                for i in range(5):
                    if v & (1 << i):
                        clist += [x, y+i]
                x += 1

    return clist

code = g.getstring("Enter code:")

for s in gzip.open("translate17.txt.gz"):
    niemiec, apg = s.split()
    if code == apg or code == niemiec:
        g.new('')
        g.putcells(decodeCanon(apg))
        g.show(s)
        g.exit()

g.show("Didn't find code")
