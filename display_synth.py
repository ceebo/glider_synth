import golly as g
import os
from urllib2 import urlopen

URL = "http://raw.githubusercontent.com/ceebo/glider_synth/master/min_paths.txt"

GLIDERS = [(g.parse("3o$2bo$bo!", -2, 0), 1, -1),   #NE
           (g.parse("bo$2bo$3o!", -2, -2), 1, 1),   #SE
           (g.parse("bo$o$3o!", 0, -2), -1, 1),     #SW
           (g.parse("3o$o$bo!", 0, 0), -1, -1)]     #NW

def get_gliders(glider_lists, t):

    ret = []

    for (glider, vx, vy), glider_list in zip(GLIDERS, glider_lists):
        
        for lane, timing in glider_list:

            phase = (t + timing) % 4
            d = (t + timing) // 4

            ret += g.transform(g.evolve(glider, phase), lane + d * vx, d * vy)

    return ret

# return the transformation t2 o t1
def compose(t1, t2):

    x, y, a, b, c, d = g.transform(g.transform([0, 0, 1, 0, 0, 1], *t1), *t2)

    return (x, y, a-x, c-x, b-y, d-y)

# return the inverse of t
def inverse(t):

    x, y, a, b, c, d = t

    det = a * d - b * c

    # assert(det in [-1, +1])

    inv = [det * i for i in [d, -b, -c, a]]

    return g.transform([-x, -y], 0, 0, *inv) + inv

def display_edge(edge, post_transform=(0,0,1,0,0,1)):

    input_code, output_code, phase, glider_lists, transform = edge

    input_cells = decodeCanon(input_code) + get_gliders(glider_lists, 0)
    output_cells = g.evolve(decodeCanon(output_code), phase)

    new_transform = compose(inverse(transform), post_transform)

    input_cells = g.transform(input_cells, *new_transform)
    output_cells = g.transform(output_cells, *post_transform)

    g.putcells(input_cells, 0, 0)    
    g.putcells(output_cells, 100, 0)

    return new_transform

def edge_cost(edge):
    
    _, _, _, glider_lists, _ = edge
    return sum(len(l) for l in glider_lists)

def edge_from_string(s):

    t = s.split(";")

    glider_lists = []
    for gliders_string in t[3:7]:
        glider_list = []
        if gliders_string:
            gs = gliders_string.split(",")
            for i in range(0, len(gs), 2):
                glider_list.append((int(gs[i]), int(gs[i+1])))
        glider_lists.append(glider_list)

    transform = tuple(map(int, t[7].split(",")))

    return (t[0], t[1], int(t[2]), glider_lists, transform)    

def display_synthesis(apgcode):

    found = True
    cost = 0
    transform = (0,0,1,0,0,1)

    while apgcode != "0":

        if apgcode not in min_paths:
            return "Don't know how to synthesise %s" % apgcode

        edge = min_paths[apgcode]

        # move everything down 100 cells
        if g.getrect():
            cells = g.getcells(g.getrect())
            g.new('')
            g.putcells(cells, 0, 100)
            
        transform = display_edge(edge, transform)
                    
        # update cost and apgcode
        apgcode = edge[0]
        cost += edge_cost(edge)
        
    return "Cost %d gliders " % cost

# Obtains a canonical representation of any oscillator/spaceship that (in
# some phase) fits within a 40-by-40 bounding box. This representation is
# alphanumeric and lowercase, and so much more compact than RLE. Compare:
#
# Common name: pentadecathlon
# Canonical representation: 4r4z4r4
# Equivalent RLE: 2bo4bo$2ob4ob2o$2bo4bo!
#
# It is a generalisation of a notation created by Allan Weschler in 1992.
def canonise(duration):

    representation = "#"

    for _ in range(duration):
        
        g.run(1)
        rect = g.getrect()

        if len(rect) == 0:
            return "0"

        if ((rect[2] <= 40) & (rect[3] <= 40)):
            # Fits within a 40-by-40 bounding box, so eligible to be canonised.
            # Choose the orientation which results in the smallest description:
            representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0], rect[1], 1, 0, 0, 1))
            representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0]+rect[2]-1, rect[1], -1, 0, 0, 1))
            representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0], rect[1]+rect[3]-1, 1, 0, 0, -1))
            representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0]+rect[2]-1, rect[1]+rect[3]-1, -1, 0, 0, -1))
            representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0], rect[1], 0, 1, 1, 0))
            representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0]+rect[2]-1, rect[1], 0, -1, 1, 0))
            representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0], rect[1]+rect[3]-1, 0, 1, -1, 0))
            representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0]+rect[2]-1, rect[1]+rect[3]-1, 0, -1, -1, 0))
        
    if representation == '#':
        prefix = ""
    elif duration == 1:
        prefix = "xs%d_" % int(g.getpop())
    else:
        prefix = "xp%d_" % duration

    return prefix + representation

# A subroutine used by canonise:
def canonise_orientation(length, breadth, ox, oy, a, b, c, d):

    representation = ""

    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    for v in xrange(0, breadth, 5):
        zeroes = 0
        if (v != 0):
            representation += "z"
        for u in xrange(length):
            baudot = 0
            for w in xrange(v, v+5):
                x = ox + a*u + b*w
                y = oy + c*u + d*w
                baudot = (baudot >> 1) + 16*g.getcell(x, y)
            if (baudot == 0):
                zeroes += 1
            else:
                if (zeroes > 0):
                    if (zeroes == 1):
                        representation += "0"
                    elif (zeroes == 2):
                        representation += "w"
                    elif (zeroes == 3):
                        representation += "x"
                    else:
                        representation += "y"
                        representation += chars[zeroes - 4]
                zeroes = 0
                representation += chars[baudot]
    return representation

# Compares strings first by length, then by lexicographical ordering.
# A hash character is worse than anything else.
def compare_representations(a, b):

    if (a == "#"):
        return b
    elif (b == "#"):
        return a
    elif (len(a) < len(b)):
        return a
    elif (len(b) < len(a)):
        return b
    elif (a < b):
        return a
    else:
        return b

chars = "0123456789abcdefghijklmnopqrstuvwxyz"

# Based on code by Arie Paap Sept. 2014
def decodeCanon(canonPatt):

    if not canonPatt or canonPatt[0] != 'x' or '_' not in canonPatt:
        return []
    
    blank = False
    x = y = 0
    clist = []
    
    for c in canonPatt[canonPatt.find("_")+1:]:
   
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

def get_period(max_period):
    
    cells = g.getcells(g.getrect())
    cells = zip(cells[::2], cells[1::2])

    for t in range(max_period):
        
        g.run(1)

        if int(g.getpop()) != len(cells):
            continue

        if all(g.getcell(x, y) for x, y in cells):
            return t + 1

    g.show("Not still life or oscillator")
    g.exit()

if os.path.exists("min_paths.txt"):
    message1 = "Read data from \"%s\"." % os.path.abspath("min_paths.txt")
else:
    g.show("Downloading min_paths.txt...")
    with open("min_paths.txt", "w") as f:
        f.write(urlopen(URL).read())
    message1 = "Downloaded data from \"%s\"." % URL 

min_paths = {}

with open("min_paths.txt") as f:
    for s in f:
        edge = edge_from_string(s)
        min_paths[edge[1]] = edge

if g.getselrect():
    cells = g.getcells(g.getselrect())
elif g.getrect():
    cells = g.getcells(g.getrect())
else:
    g.show("Empty")
    g.exit()

g.addlayer()
g.new('')
g.putcells(cells)

apgcode = canonise(get_period(46))

g.new(apgcode)

message2 = display_synthesis(apgcode)

g.fit()
g.show(message1 + " " + message2)
