#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from pprint import pprint
from pprint import pformat
from copy import deepcopy
import operator


# pruning ideas:
#
# all pieces must start at 000, even if this means they have negative z values
# then only empty spaces in the board will be valid starting places
#
#
#


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
        ### placing only 9 pieces involves about 5 seconds and about 1500 backtracks
        # +
        #  - -
        [(0,0,0), (0,1,0), (1,1,0), (0,0,1)],
        # |
        #  + -
        [(0,0,1), (0,1,0), (1,1,0), (0,1,1)]
      ]
'''


class Board:

    def __init__(self):
        self.empty_spaces = deepcopy(ALL_SPACES)
        self.pieces = [] #dictionary of xy locations to pieces


    def __repr__(self):
        return pformat({"pieces": self.pieces,
                        "spaces": self.empty_spaces})


    # place a piece on the board, can-place must be true for the piece
    def place(self, piece, loc):
        moved_spots = [piece_add(spot, loc) for spot in piece]

        for spot in moved_spots:
            self.empty_spaces.remove(spot)

        self.pieces.append((loc, piece))

    # removes a piace at a location from the board,
    # the pieces must already be on the board at the given location
    def remove(self, piece, loc):
        moved_spots = [piece_add(spot, loc) for spot in piece]

        for spot in moved_spots:
            self.empty_spaces.add(spot)

        self.pieces.remove((loc, piece))

    # can a piece be placed on a board?
    def can_place(self, piece, loc):
        #print((piece, loc))
        for spot in piece:
            moved_spot = piece_add(spot, loc)
            if not moved_spot in self.empty_spaces:
                return False
        return True



def piece_add(spot, loc):
    return tuple(map(operator.add, spot, loc))


### piece ###
# a piece is just a list of 3-D coords
# the first spot in any piece must be 000 or 001
# negative x and y coords are allowed, since positioning is relative
# pieces are only ever 2 slots high, so z coords can only ever be 0 or 1

# all modifications of pieces are functional, they return new pieces


# flip a piece horizontally
#  ⊆
#  goes to
#  ⊇
# when a piece flips horizontally it flips 'around' 00
def flip(piece):
    highest = max([x for x,y,z in piece])

    # z coords 0->1 1->0
    # x coords go negative
    return list(map(lambda t: (-t[0],t[1],1-t[2]), piece))


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
def rotate60xdegrees(piece, rotations):
    return [rotate_spot(spot, rotations) for spot in piece]
    # rotate around 00


#there are more elegant ways to do this, but they are a huge pain
def rotate_spot(spot, rotations):
    for r in range(rotations):
        spot = ROTATION_DICT[spot]
    return spot

# (0,0) stays the same
# (1,0) -> (0,1) -> (-1,1) -> (-1,0) -> (-1,-1) -> (0,-1)
# (2,0) -> (1,2) -> (-1,2) -> (-2,0) -> (-1,-2) -> (1,-2)
# (1,1) -> (0,2) -> (-2,1) -> (-2,-1) -> (0,-2) -> (1,-1)

#   (-2-3) (-1-3) ( 0-3) ( 1-3) ( 2-3)
# (-2-2) (-1-2) ( 0-2) ( 1-2) ( 2-2)
#   (-2-1) (-1-1) ( 0-1) ( 1-1) ( 2-1)
# (-2 0) (-1 0)   0 0  ( 1 0) ( 2 0)
#   (-2 1) (-1 1) ( 0 1) ( 1 1) ( 2 1)
# (-2 2) (-1 2) ( 0 2) ( 1 2) ( 2 2)
#   (-2 3) (-1 3) ( 0 3) ( 1 3) ( 2 3)

ROTATION_DICT = {
    (0,0,0):   (0,0,0),

    (1,0,0):   (0,1,0),
    (0,1,0):   (-1,1,0),
    (-1,1,0):  (-1,0,0),
    (-1,0,0):  (-1,-1,0),
    (-1,-1,0): (0,-1,0),
    (0,-1,0):  (1,0,0),

    (2,0,0):   (1,2,0),
    (1,2,0):   (-1,2,0),
    (-1,2,0):  (-2,0,0),
    (-2,0,0):  (-1,-2,0),
    (-1,-2,0): (1,-2,0),
    (1,-2,0):  (2,0,0),

    (1,1,0):   (0,2,0),
    (0,2,0):   (-2,1,0),
    (-2,1,0):  (-2,-1,0),
    (-2,-1,0): (0,-2,0),
    (0,-2,0):  (1,-1,0),
    (1,-1,0):  (1,1,0),

    (0,0,1):   (0,0,1),

    (1,0,1):   (0,1,1),
    (0,1,1):   (-1,1,1),
    (-1,1,1):  (-1,0,1),
    (-1,0,1):  (-1,-1,1),
    (-1,-1,1): (0,-1,1),
    (0,-1,1):  (1,0,1),

    (2,0,1):   (1,2,1),
    (1,2,1):   (-1,2,1),
    (-1,2,1):  (-2,0,1),
    (-2,0,1):  (-1,-2,1),
    (-1,-2,1): (1,-2,1),
    (1,-2,1):  (2,0,1),

    (1,1,1):   (0,2,1),
    (0,2,1):   (-2,1,1),
    (-2,1,1):  (-2,-1,1),
    (-2,-1,1): (0,-2,1),
    (0,-2,1):  (1,-1,1),
    (1,-1,1):  (1,1,1),


}


"""

# rotation might be easier in cube coords
# http://www.redblobgames.com/grids/hexagons/#rotation


# in code coords
# A rotation 60° right shoves each coordinate one slot to the right:
# and multiplies everything by -1
#            [ x,  y,  z]
#            to  [-z, -x, -y]


# http://www.redblobgames.com/grids/hexagons/#conversions
# we're using a to represent the third axis, since it never changes here
def cube_to_hex(h): # axial
    x, y, z, a = h
    q = x
    r = z + (x + (x&1)) / 2
    return (q, r, a)

def hex_to_cube(h): # axial
    q, r, a = h
    x = q
    z = r - (q + (q&1)) / 2
    y = -x-z
    return (x, y, z, a)

"""


def depth_first_search():
    board = Board()
    pieces = ALL_PIECES

    return place_remaining(board, pieces)


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

    #print(("trying piece: ", piece))

    # rotation and flipping give all possible orientations
    for n in [0,1,2,3,4,5]:      # all 6 possible rotations
        for f in [True, False]:  # whether to flip

            rotated = rotate60xdegrees(piece, n)

            #print(("rotation: ", rotated))

            if ITERATION % 100000 == 0:
                print(("iteration", ITERATION))

            if f:
                rotated = flip(piece)

            for location in ALL_SPACES: #TODO does this need to be another copy?

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

    if (len(remaining_pieces) > 5):
        pprint({"backtracking remaining pieces:": len(remaining_pieces),
                "number on board": len(board.pieces)})
    return False #if no placement for the piece works return false


print(depth_first_search())



