#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from pprint import pprint
from pprint import pformat
import copy
import operator


# pruning/optimization ideas:
#
# all pieces must start at 000, even if this means they have negative z values
# then only empty spaces in the board will be valid starting places
# -- this ended up reqiring a copy, but that doesn't seem to expensive
# -- doesn't even show up in the profiler
#
# memoize move or maybe even move_piece
# -- doesn't seem to help...
#
# make can_place faster
#  - vectorize pieces and locs so adding them is faster
#  - somehow do the set operations more quickly.
#
# use out-of-bounds checks instead of just in-board-spaces checks
#  - this actually made things slower
#
# use oob checks in a spot-by-spot basis instead of piece by piece
#
# prune by checking for too-small sections of the open spaces left?
# that might dramatically remove some branches
#
# put all the single-spot-on-a-layer pieces at the beginning of the list
# prune if we get into a condition where there are single-spots left after they're used
#



# Memoization
# http://stackoverflow.com/questions/1988804/what-is-memoization-and-how-can-i-use-it-in-python
class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}
    def __call__(self, *args):
        targs = [args[1]].append(args[0]) # [a b c] [d] -> [d a b c]
        if not targs in self.memo:
            self.memo[targs] = self.f(*args)
        return self.memo[targs]



ITERATION = 0

# the hexagonal board is an 'offset' 2d grid in a triangle shape with 3 layers
#
#  (0,0) (1,0) (2,0) (3,0) (4,0)
#     (0,1) (1,1) (2,1) (3,1)
#  ----- (1,2) (2,2) (3,2)
#     ----- (1,3) (2,3)
#  ----- ----- (2,4)
#

# three triangular layers
ALL_SPACES = set([
    (0,0,0), (1,0,0), (2,0,0), (3,0,0), (4,0,0),
        (0,1,0), (1,1,0), (2,1,0), (3,1,0),
            (1,2,0), (2,2,0), (3,2,0),
                (1,3,0), (2,3,0),
                    (2,4,0),
    (0,0,1), (1,0,1), (2,0,1), (3,0,1), (4,0,1),
        (0,1,1), (1,1,1), (2,1,1), (3,1,1),
            (1,2,1), (2,2,1), (3,2,1),
                (1,3,1), (2,3,1),
                    (2,4,1),
    (0,0,2), (1,0,2), (2,0,2), (3,0,2), (4,0,2),
        (0,1,2), (1,1,2), (2,1,2), (3,1,2),
            (1,2,2), (2,2,2), (3,2,2),
                (1,3,2), (2,3,2),
                    (2,4,2)
])


PRINT_GRID = """
000 100 200 300 400   001 101 201 301 401   002 102 202 302 402
  010 110 210 310       011 111 211 311       012 112 212 312
    120 220 320           121 221 321           122 222 322
      130 230               131 231               132 232
        240                   241                   242
"""





ALL_PIECES = [
        # all pieces are 'centered' (rotate around) 000 or 001
        #
        # - lower hex
        # | upper hex
        # + both lower and upper hexes

        # - +
        #  - -
        [(0,0,0), (0,1,0), (1,0,0), (1,1,0), (1,0,1)],

        # - +
        #  - -
        [(0,0,0), (0,1,0), (1,0,0), (1,1,0), (1,0,1)], #duplicate piece

        #  + - -
        #
        [(0,0,0), (1,0,0), (2,0,0), (0,0,1)],

        #  - + |
        #
        [(0,0,0), (1,0,0), (1,0,1), (2,0,1)],

        #  - + -
        #
        [(0,0,0), (1,0,0), (2,0,0), (1,0,1)],

        # - |
        #  +
        [(0,0,0), (0,1,0), (0,1,1), (1,0,1)],

        # - -
        #  +
        [(0,0,0), (1,0,0), (0,1,0), (0,1,1)],

        # -
        #  + |
        [(0,0,0), (0,1,0), (0,1,1), (1,1,1)],

        # -
        #  - +
        [(0,0,0), (0,1,0), (1,1,0), (1,1,1)]
]
'''

        # +
        #  - -
        [(0,0,0), (0,1,0), (1,1,0), (0,0,1)]

        # |
        #  + -
        [(0,0,0), (0,1,-1), (1,1,-1), (0,1,0)]

'''



class Board:

    def __init__(self):
        self.empty_spaces = copy.deepcopy(ALL_SPACES)
        self.pieces = [] #list of (xyz locations, pieces)


    # prints coords and a visual grid representation of the board
    def __repr__(self):
        moved_pieces = [move_piece(piece[1], piece[0]) for piece in self.pieces]
        return pformat(moved_pieces) + self.format_grid(moved_pieces)

    #  3 layers
    #  (0,0) (1,0) (2,0) (3,0) (4,0)
    #     (0,1) (1,1) (2,1) (3,1)
    #  ----- (1,2) (2,2) (3,2)
    #     ----- (1,3) (2,3)
    #  ----- ----- (2,4)
    # these are s little irregular, so it's not worth abstracting
    def in_bounds(self, spot):

        z = spot[2]
        if z < 0 or 2 < z:
            return False

        y = spot[1]
        if y < 0 or 4 < y:
            return False

        x = spot[0]
        if y == 4:
            if x != 2:
                return False
        elif y == 3:
            if x < 1 or 2 < x:
                return False
        elif y == 2:
            if x < 1 or 3 < x:
                return False
        elif y == 1:
            if x < 0 or 3 < x:
                return False
        elif y == 0:
            if x < 0 or 4 < x:
                return False

        return True


    def format_grid(self, moved_pieces):
        # ~ is the 10th piece
        # zip will discard extra length
        grid = PRINT_GRID

        for piece, identifier in zip(moved_pieces, ["0","1","2","3","4","5","6","7","8","9","~"]):
            for spot in piece:
                sigyl = "<"+identifier+">" # three chars long
                placeholder = str(spot[0]) + str(spot[1]) + str(spot[2])

                grid = grid.replace(placeholder, sigyl)

        return grid


    # place a piece on the board, can-place must be true for the piece
    def place(self, piece, loc):
        moved_spots = move_piece(piece, loc)

        for spot in moved_spots:
            self.empty_spaces.remove(spot)

        self.pieces.append((loc, piece))

    # removes a piace at a location from the board,
    # the pieces must already be on the board at the given location
    def remove(self, piece, loc):
        moved_spots = move_piece(piece, loc)

        for spot in moved_spots:
            self.empty_spaces.add(spot)

        self.pieces.remove((loc, piece))

    # can a piece be placed on a board?
    def can_place(self, piece, loc):
        for spot in piece:
            moved_spot = move(spot, loc)
            if not moved_spot in self.empty_spaces:
                return False
        return True





def move(spot, loc):
    return tuple(map(operator.add, spot, loc))

def move_piece(piece, loc):
    return [move(spot, loc) for spot in piece]

### amazing
#move_piece = Memoize(move_piece)



### PIECE ###
# a piece is just a list of 3-D coords
# the first spot in any piece must be 000 or 001
# negative x and y coords are allowed, since positioning is relative
# pieces are only ever 2 slots high, so z coords can only ever be 0 or 1
#
# all modifications of pieces are functional, they return new pieces
#
# the term 'spot' means an individual 3d coordinate within a piece.
# pieces are made of spots


# there are 6 directions of orientation for hexagonal pieces
# 360/6 = 60
# rotates a piece 60*rotations degrees clockwise
#  - - +
#  goes to
#  -
#   -
#    +
#  goes to
#    -
#   -
#  +
#  goes to
#  + - -
#  goes to
#  +
#   -
#    -
#  goes to
#    +
#   -
#  -
#  etc.
def rotate(piece, rotations):
    return [rotate_spot(spot, rotations) for spot in piece]
    # rotate around 00


# same as rotate, but also
# flips a piece 180 degrees around the x axis
#  +
# -
#  -
# goes to
#  -
# -
#  +
def rotate_and_flip(piece, rotations):
    return [rotate_flip_spot(spot, rotations) for spot in piece]


# rotate a spot 60*rotations degrees around 000
def rotate_spot(spot, rotations):
    for r in range(rotations):
        # TODO is it inefficient to do 5 lookups here sometimes?
        spot = ROTATION_DICT[spot]
    return spot

# rotate a spot by 60*rotations degrees 
# and flip it 180 degrees around the x axis
def rotate_flip_spot(spot, rotations):
    spot = FLIP_DICT[rotate_spot(spot, rotations)]
    return spot



# "Sphere" of rotation for pieces being transformed (rotated/flipped) in 2d
# no transformation will take a piece outside of this sphere
# (this set is a 'group' under the rotation/flip operations,
#  and all initial spots are in this set)
#   ----- ----- ----- ----- -----
# ----- (-1-2) ( 0-2) ( 1-2) -----
#   (-2-1) (-1-1) ( 0-1) ( 1-1) -----
# (-2 0) (-1 0)   00   ( 1 0) ( 2 0) 
#   (-2 1) (-1 1) ( 0 1) ( 1 1) -----
# ----- (-1 2) ( 0 2) ( 1 2) -----
#   ----- ----- ----- ----- -----


# this precomputes all the simple spot rotations/flips around 000
# so a runtime we can just do lookups instead of calculations
def create_transformations():

    # how a point rotates around 00
    # (0,0) stays the same
    # (1,0) -> (0,1) -> (-1,1) -> (-1,0) -> (-1,-1) -> (0,-1)
    # (2,0) -> (1,2) -> (-1,2) -> (-2,0) -> (-1,-2) -> (1,-2)
    # (1,1) -> (0,2) -> (-2,1) -> (-2,-1) -> (0,-2) -> (1,-1)
    CYCLE_0 = [(0,0)]
    CYCLE_1 = [(1,0), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1)]
    CYCLE_2 = [(2,0), (1,2), (-1,2), (-2,0), (-1,-2), (1,-2)]
    CYCLE_3 = [(1,1), (0,2), (-2,1), (-2,-1), (0,-2), (1,-1)]

    noflip = {}
    flip = {}

    for z in [-1, 0, 1]:
        for cycle in [CYCLE_0, CYCLE_1, CYCLE_2, CYCLE_3]:
            for index in range(len(cycle)):
                # each point maps to the next point in the cycle
                # if you go over the end wrap around to 0
                point2D = cycle[index]
                next_point2D = cycle[(index+1)%len(cycle)]

                x = point2D[0]
                y = point2D[1]

                xn = next_point2D[0]
                yn = next_point2D[1]

                # add z coords in
                point3D = (x, y, z)
                next_point3D = (xn, yn, z)

                # rotate 180 degrees around x axis
                flip_next_point3D = (x, -y, -z)

                noflip[point3D] = next_point3D
                flip[point3D] = flip_next_point3D

    return noflip, flip

ROTATION_DICT, FLIP_DICT = create_transformations()
#pprint(sorted(zip(ROTATION_DICT.keys(), ROTATION_DICT.values())))
#pprint(sorted(zip(FLIP_ROTATION_DICT.keys(), FLIP_ROTATION_DICT.values())))




# iterations per layer
# pieces * rotations * flip * locations
# 6 * 2 * 15
# 180



# tries to place all the remaining pieces
# returns either a finished board or False if there is no solution for that branch
# depth first
def place_remaining(board, remaining_pieces):
    global ITERATION

    if len(remaining_pieces)==0:
        return board

    piece = remaining_pieces[0]
    remaining_pieces = remaining_pieces[1:]

    # copy so we can modify the board recursivly while still iterating over this
    # each piece (even when transformed) contains 000,
    # so we can only place them as locations which are empty
    available_spaces = copy.copy(board.empty_spaces)

    #print(("trying piece: ", piece))

    # rotation and flipping give all possible orientations
    for n in [0,1,2,3,4,5]:      # all 6 possible rotations
        for f in [True, False]:  # whether to flip

            if f: rotated = rotate_and_flip(piece, n)
            else: rotated = rotate(piece, n)

            #print(("rotation: ", rotated))

            if ITERATION % 100000 == 0:
                print(("iteration", ITERATION))

            for location in available_spaces:
                ITERATION += 1

                if board.can_place(rotated, location):

                    #print(("placing", rotated, location))
                    board.place(rotated, location)
                    #print(board)

                    solution = place_remaining(board, remaining_pieces)

                    if not solution:
                        #print(("removing", rotated, location))
                        board.remove(rotated, location) #keep looping
                    else:
                        return solution

                else:
                    pass

    #if (len(remaining_pieces) > 2):
    #    pprint({"backtracking remaining pieces:": len(remaining_pieces),
    #            "number on board": len(board.pieces),
    #            "board": board})
    return False #if no placement for the piece works return false



def depth_first_search():
    board = Board()
    pieces = ALL_PIECES
    return place_remaining(board, pieces)


if __name__ == "__main__":
    print(depth_first_search())
    print(("ITERATIONS", ITERATION))






import unittest

class TestTransformations(unittest.TestCase):

    def test_flip_rotate(self):
        self.assertEqual(rotate_flip_spot((0,0,0), 1), (0,0,0))

        self.assertEqual(rotate_flip_spot((1,0,1), 2), (-1,-1,-1))
        self.assertEqual(rotate_flip_spot((-1,2,-1), 3), (1,2,1))
        self.assertEqual(rotate_flip_spot((1,-1,0), 1), (1,-1,0))


    def test_rotate(self):
        self.assertEqual(rotate_spot((0,0,0), 2), (0,0,0))

        self.assertEqual(rotate_spot((1,0,1), 2), (-1,1,1))
        self.assertEqual(rotate_spot((-1,2,-1), 3), (1,-2,-1))
        self.assertEqual(rotate_spot((1,-1,0), 1), (1,1,0))

    def test_rotate_piece(self):
        self.assertEqual(rotate(ALL_PIECES[0], 1),
                         [(0,0,0), (-1,1,0), (0,1,0), (0,2,0), (0,1,1)])

    def test_flip_rotate_piece(self):
        self.assertEqual(rotate_and_flip(ALL_PIECES[0], 1),
                         [(0,0,0), (-1,-1,0), (0,-1,0), (0,-2,0), (0,-1,-1)])


