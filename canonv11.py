# canon.py, version 1.l
# Changes from 1.0:
#   added auto-creation of InfectLife.rule when necessary

import golly as g
import os
from os import listdir

SUCCESS = 0
FAIL = 1
UNKNOWN = 2

try:
  oldrule = g.setrule("InfectLife")
  g.setrule(oldrule)
except:
  with open(os.path.join(g.getdir("rules"), "InfectLife.rule"),"w" ) as f:
    f.write("""@RULE InfectLife

@TABLE

n_states:5
neighborhood:Moore
symmetries:permute

var a1 = {0,1,2,3,4}
var a2 = {0,1,2,3,4}
var a3 = {0,1,2,3,4}
var a4 = {0,1,2,3,4}
var a5 = {0,1,2,3,4}
var a6 = {0,1,2,3,4}
var a7 = {0,1,2,3,4}

var b1 = {1,2,3}
var b2 = {1,2,3}

var c = {1,2}

var d = {3,4}

c,d,a1,a2,a3,a4,a5,a6,a7,3
0,3,b1,b2,a3,a4,a5,a6,a7,4""")

# Shortcut to place cells in a new rule
def putcells(rule, cells):
    g.new('')
    g.setrule(rule)
    g.putcells(cells)

# Arguments lists extracted from the original apgsearch code
def rect_to_args_list(rect):

    return [(rect[2], rect[3], rect[0], rect[1], 1, 0, 0, 1),
            (rect[2], rect[3], rect[0]+rect[2]-1, rect[1], -1, 0, 0, 1),
            (rect[2], rect[3], rect[0], rect[1]+rect[3]-1, 1, 0, 0, -1),
            (rect[2], rect[3], rect[0]+rect[2]-1, rect[1]+rect[3]-1, -1, 0, 0, -1),
            (rect[3], rect[2], rect[0], rect[1], 0, 1, 1, 0),
            (rect[3], rect[2], rect[0]+rect[2]-1, rect[1], 0, -1, 1, 0),
            (rect[3], rect[2], rect[0], rect[1]+rect[3]-1, 0, 1, -1, 0),
            (rect[3], rect[2], rect[0]+rect[2]-1, rect[1]+rect[3]-1, 0, -1, -1, 0)]

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
    latest = 0
    transforms = []

    # We need to compare each phase to find the one with the smallest
    # description:

    # Also, for the latest phase that has a minimal representation we
    # return all transformations giving that minimal representation.
    for t in xrange(duration):

        rect = g.getrect()
        if (len(rect) == 0):
            return "0", 0, [[0,0,0,0,1,0,0,1]]

        if ((rect[2] <= 40) & (rect[3] <= 40)):

            # Fits within a 40-by-40 bounding box, so eligible to be canonised.
            # Choose the orientation which results in the smallest description:

            for args in rect_to_args_list(rect):

                next_rep = canonise_orientation(*args)

                if next_rep == representation:
                    # If match is later than previous matches reset list, otherwise append.
                    if t > latest:
                        latest = t
                        transforms = [args]
                    else:
                        transforms.append(args)
                else:
                    
                    representation = compare_representations(representation, next_rep)
                    
                    # New best representation so reset the list
                    if next_rep == representation:
                        latest = t
                        transforms = [args]

        g.run(1)

    if representation != '#':
        prefix = "xs" + g.getpop() if duration == 1 else "xp%d" % duration
        representation = prefix + "_" + representation

    return representation, latest, transforms

# A subroutine used by canonise:
def canonise_orientation(length, breadth, ox, oy, a, b, c, d):

    representation = ""

    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    for v in xrange(int((breadth-1)/5)+1):
        zeroes = 0
        if (v != 0):
            representation += "z"
        for u in xrange(length):
            baudot = 0
            for w in xrange(5):
                x = ox + a*u + b*(5*v + w)
                y = oy + c*u + d*(5*v + w)
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

# Find the period and maximum dimensions of an object
def analyse_object(max_period):
    
    rect = g.getrect()

    if not rect:
        return 1, None

    cells = to_pairs(g.getcells(rect))

    dimensions = [rect[0], rect[1], rect[0] + rect[2] - 1, rect[1] + rect[3] - 1]

    for t in range(max_period):
        
        g.run(1)

        if int(g.getpop()) == len(cells) and all(g.getcell(x, y) for x, y in cells):
            return t + 1, dimensions

        rect = g.getrect()

        if not rect:
            return None, None
        
        dimensions[0] = min(dimensions[0], rect[0])
        dimensions[1] = min(dimensions[1], rect[1])
        dimensions[2] = max(dimensions[2], rect[0] + rect[2] - 1)
        dimensions[3] = max(dimensions[3], rect[1] + rect[3] - 1)
 
    return None, None


# Convert cell list to pairs
def to_pairs(x):
    return zip(x[::2], x[1::2])

# Convert cell list to pairs and ensure (0, 0) is one of those pairs
def to_pairs_and_shift(x):
    return [(x[i]-x[0], x[i+1]-x[1]) for i in range(0, len(x), 2)]    

# Take boundary of pairs
def boundary(pairs):

    s = set()

    for x, y in pairs:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                s.add((x+dx, y+dy))

    return list(s - set(pairs))

GLIDERS = [(g.parse("3o$2bo$bo!", -2, 0), 1, -1),   #NE
           (g.parse("bo$2bo$3o!", -2, -2), 1, 1),   #SE
           (g.parse("bo$o$3o!", 0, -2), -1, 1),     #SW
           (g.parse("3o$o$bo!", 0, 0), -1, -1)]     #NW

# Remove gliders from the pattern and return all timing information
def remove_gliders():

    cells = g.getcells(g.getrect())
    cells = zip(cells[::2], cells[1::2])

    lists = []

    for glider, vx, vy in GLIDERS:

        sub_list = []

        for phase in range(4):

            wanted = to_pairs(glider)
            unwanted = boundary(wanted)

            for x, y in cells:

                if not all(g.getcell(x+dx, y+dy) for dx, dy in wanted):
                    continue

                if any(g.getcell(x+dx, y+dy) for dx, dy in unwanted):
                    continue

                for dx, dy in wanted:
                    g.setcell(x+dx, y+dy, 0)

                sub_list.append((x - y * vx // vy, 4 * y // vy + phase))
    
            glider = g.evolve(glider, 1)

        lists.append(sub_list)

    return lists

# Calculate the time at which the the gliders first enter the
# "forbidden" zone. Can be positive or negative.
def canonical_time1(glider_lists, dimensions):

    min_x, min_y, max_x, max_y = dimensions
    
    args = [(min_x - 2, max_y + 2, 1, -1),   #NE
            (min_x - 2, min_y - 2, 1, 1),    #SE
            (max_x + 2, min_y - 2, -1, 1),   #SW
            (max_x + 2, max_y + 2, -1, -1)]  #NW
    
    t = None
    
    for (x, y, vx, vy), glider_list in zip(args, glider_lists):
        
        for lane, timing in glider_list:
            
            tx = 4 * (x - lane) // vx - timing - 1
            ty = 4 * y // vy - 3 - timing
            
            if t is None or min(tx, ty) < t:
                t = min(tx, ty)

    return t

# Calculate the canonical time for a pure glider synthesis.
def canonical_time2(glider_lists):

    args = [(1, -1), (1, 1), (-1, 1), (-1, -1)]
    
    t_e, t_w, t_s, t_n = None, None, None, None
    
    for (vx, vy), glider_list in zip(args, glider_lists):
        
        for lane, timing in glider_list:
            
            tx = 4 * lane // vx + timing - 2
            ty = timing
            
            if vx > 0:
                t_e = tx if t_e is None else max(t_e, tx)
            else:
                t_w = tx if t_w is None else max(t_w, tx)
                
            if vy > 0:
                t_s = ty if t_s is None else max(t_s, ty)
            else:
                t_n = ty if t_n is None else max(t_n, ty)
                
    t_ew, t_ns = None, None
    
    if t_e is not None and t_w is not None:
        t_ew = (-12 - t_w - t_e) // 2
        
    if t_s is not None and t_n is not None:
        t_ns = (-12 - t_n - t_s) // 2

    if t_ew is not None and t_ns is not None:
        return min(t_ew, t_ns)
    elif t_ew is not None:
        return t_ew
    elif t_ns is not None:
        return t_ns
    else:
        return 0


# Place gliders into the pattern where they would be at time t
def place_gliders(glider_lists, t):

    for (glider, vx, vy), glider_list in zip(GLIDERS, glider_lists):
        
        for lane, timing in glider_list:

            phase = (t + timing) % 4
            x = lane + (t + timing - phase) // 4 * vx
            y = (t + timing - phase) // 4 * vy

            g.putcells(g.evolve(glider, phase), x, y)
    
def canonise_synthesis():

    start_cells = g.getcells(g.getrect())

    # Remove gliders from pattern and get all timing information
    glider_lists = remove_gliders()

    # Find pattern period and maximum dimensions
    period, dimensions = analyse_object(46)

    if period is None:
        return UNKNOWN, start_cells

    # Case where synthesis is not just gliders
    if dimensions:

        # Calculate when gliders first encroach
        t = canonical_time1(glider_lists, dimensions)

        # Put the input into the phase it would be in at that time
        g.run(t % period)

        # Find the latest phase that can be transformed to canonical form
        input_code, phase, transforms = canonise(period)

        if input_code == "#":
            return UNKNOWN, start_cells

        # Move to that phase.
        g.run(phase)

        # Canonical time is the lastest valid time before t
        canonical_t = t - period + phase
        place_gliders(glider_lists, canonical_t)

    else:

        # Other case
        input_code = "0"
        canonical_t = canonical_time2(glider_lists)
        place_gliders(glider_lists, canonical_t)
        transforms = rect_to_args_list(g.getrect())

    canonical_cells = g.getcells(g.getrect())

    if canonical_t < 0:
        g.run(-canonical_t)
        g.putcells(start_cells, 0, 0, 1, 0, 0, 1, "xor")
    else:
        g.putcells(g.evolve(start_cells, canonical_t), 0, 0, 1, 0, 0, 1, "xor")

    if not g.empty():
        return FAIL, start_cells

    # Check glider salvos are well spaced
    place_gliders(glider_lists, canonical_t - 4)
    g.run(4)
    pop = int(g.getpop())

    if pop != 5 * sum(len(glider_list) for glider_list in glider_lists):
        return FAIL, start_cells

    place_gliders(glider_lists, canonical_t)

    if pop != int(g.getpop()):
        return FAIL, start_cells

    best_gliders = None
    best_cells = None

    # Analyse each possible transform and return canonical synthesis
    for tr in transforms:

        # This could be done by applying the transformations to the
        # glider lists directly but instead we apply them to the cells
        # and call remove_gliders each time.
        _, _, ox, oy, a, b, c, d = tr
        
        det = a * d - b * c
        
        assert(det in [-1, +1])

        cells = g.transform(canonical_cells, -ox, -oy)
        cells = g.transform(cells, 0, 0, d * det, -b * det, -c * det, a * det)

        putcells('Life', cells)

        glider_lists = remove_gliders()
        
        for glider_list in glider_lists:
            glider_list.sort()

        if best_gliders is None or glider_lists < best_gliders:
            best_gliders = glider_lists[:]
            best_cells = cells[:]

    putcells('Life', best_cells)
    g.run(1024)
    period, dimensions = analyse_object(46)

    if period is None:
        return FAIL, start_cells

    # Put output into the same phase that it would be in at generation 1
    g.run(-1023 % period)

    # Find latest period that has canonical representation
    output_code, phase, transforms = canonise(period)

    # Need this many generations for the canonical representation of
    # the output to match the phase of the canonical synthesis
    phase = period - (phase + 1)

    transform = transforms[0][2:]

    edge = (input_code, output_code, phase, best_gliders, transform)

    return SUCCESS, edge

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
            if c == "z":
                x += 35
            else:
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


def display_edge(edge, delay=False):

    g.new('')
    
    input_code, output_code, phase, glider_lists, transform = edge

    input_cells = decodeCanon(input_code)

    g.putcells(input_cells)
    
    output_cells = decodeCanon(output_code)
    output_cells = g.evolve(output_cells, phase)
    output_cells = g.transform(output_cells, *transform)
    
    g.putcells(output_cells, 100, 0)

    place_gliders(glider_lists, 0)

    g.select(g.getrect())
    g.copy()
    g.select([])
    g.fit()
    g.update()

    while delay and g.getkey() == '':
        pass


# Find all occurences of cells1 in cells2 and append all matches to results
def find(results, cells1, cells2):
    
    if not cells1 or not cells2:
        return

    wanted = to_pairs_and_shift(cells1)
    unwanted = boundary(wanted)

    putcells("Life", cells2)

    for i in range(0, len(cells2), 2):

        x, y = cells2[i], cells2[i+1]

        if not all(g.getcell(x+dx, y+dy) for dx, dy in wanted):
            continue

        if any(g.getcell(x+dx, y+dy) for dx, dy in unwanted):
            continue

        results.append([(x+dx, y+dy) for dx, dy in wanted])


# Spread an infection then remove it and return it
def infect_and_remove(germ):

    for x, y in germ:
        g.setcell(x, y, 3)

    g.setrule("InfectLife")
    g.setbase(2)
    g.setstep(10)
    g.step()

    chunk = []
    cells = g.getcells(g.getrect())
    for i in range(0, len(cells)-2, 3):
        if cells[i+2] >= 3:
            g.setcell(cells[i], cells[i+1], 0)
            chunk.append((cells[i], cells[i+1]))

    return chunk


# Return ON cells that are a subset of the given pairs
def get_subset(pairs):
    
    cells = []

    for x, y in pairs:
        if g.getcell(x, y):
            cells.append(x)
            cells.append(y)

    return cells

# Generates what it thinks are all the relevant glider syntheses in the
# current pattern
def get_syntheses():

    g.setrule("Life")
    start_cells = g.getcells(g.getrect())

    g.setrule("LifeHistory")
    g.setbase(2)
    g.setstep(10)
    g.step()
    
    history_cells = g.getcells(g.getrect())
    
    g.setrule("InfectLife")
    g.setbase(2)
    g.setstep(10)
    
    chunks = []

    while not g.empty():
        cells = g.getcells(g.getrect())
        germ = [(cells[0], cells[1])]
        chunks.append(infect_and_remove(germ))
        
    putcells("Life", start_cells)
        
    synths = []
    inputs = []
    
    for chunk in chunks:
        inputs.append(get_subset(chunk))
        
    end_cells = g.evolve(start_cells, 840)
    
    seen = set()

    while inputs:
        
        input_cells = inputs.pop()
        
        hashable = tuple(sorted(to_pairs(input_cells)))
        if hashable in seen:
            continue
        
        seen.add(hashable)

        output_cells = g.evolve(input_cells, 840)
        putcells("Life", input_cells)

        if not any(remove_gliders()):
            continue

        # The current chunk contains gliders so add it to the list
        synths.append(input_cells)
        
        input_cells = g.getcells(g.getrect())

        # Search for the input of the current chunk in the output of
        # the full pattern and then search for the output of the
        # current chunk in the full pattern.
        germs = []
        find(germs, input_cells, end_cells)
        find(germs, output_cells, start_cells)

        for germ in germs:

            putcells("InfectLife", history_cells)
            chunk = infect_and_remove(germ)
            putcells("Life", start_cells)
            inputs.append(get_subset(chunk))

    return synths


count = 0

for filename in listdir("synths"):

    err_count = 0

    g.open("synths/" + filename)
    pats = get_syntheses()

    offset = 0
    g.new('')
    g.setrule("Life")
    for pat in pats:
        g.putcells(pat, offset-min(pat[::2]), -min(pat[1::2]))
        offset += 100
    g.fit()
    g.update()

    for pat in pats:

        putcells("Life", pat)
        status, result = canonise_synthesis()

        if status == SUCCESS:

            #display_edge(result)
            pass

        else: 

            prefix = "fail" if status == FAIL else "unknown"

            g.new('')
            g.putcells(result)
            g.save("errors/%s%d_%s" % (prefix, err_count, filename), "rle")
            err_count += 1
        
    count += 1
    g.show(str(count))
