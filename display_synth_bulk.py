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

if os.path.exists("min_paths.txt"):
    message1 = "Read data from \"%s\"." % os.path.abspath("min_paths.txt")
else:
    g.show("Downloading min_paths.txt...")
    with open("min_paths.txt", "w") as f:
        f.write(urlopen(URL).read())
    message1 = "Downloaded data from \"%s\"." % URL 

g.show(message1)

min_paths = {}

with open("min_paths.txt") as f:
    for s in f:
        edge = edge_from_string(s)
        min_paths[edge[1]] = edge

with open("apgcodes.txt") as f:
    for s in f:
        ss = s.split()
        g.new(ss[0])
        message2 = display_synthesis(ss[0])
        if message2.startswith("Cost"):
            g.save(ss[-1] + ".rle", "rle")
        else:
            g.exit(message2)
