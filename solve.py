#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# the hexagonal board is an 'offset' 2d grid in a triangle shape with 3 layers
#
#  (0,0) (1,0) (2,0) (3,0) (4,0)
#     (0,1) (1,1) (2,1) (3,1)
#  ----- (1,2) (2,2) (3,2)
#     ----- (1,3) (2,3)
#  ----- ----- (2,4)
#

# three triangular layers
ALL_SPACES = [
    (0,0,0), (1,0,0), (2,0,0), (3,0,0), (4,0,0),
    (0,1,0), (1,1,0), (2,1,0), (3,1,0),
    (1,2,0), (2,2,0), (3,2,0),
    (1,3,0), (2,3,0),
    (2,4,0)
    (0,0,1), (1,0,1), (2,0,1), (3,0,1), (4,0,1),
    (0,1,1), (1,1,1), (2,1,1), (3,1,1),
    (1,2,1), (2,2,1), (3,2,1),
    (1,3,1), (2,3,1),
    (2,4,1)
    (0,0,2), (1,0,2), (2,0,2), (3,0,2), (4,0,2),
    (0,1,2), (1,1,2), (2,1,2), (3,1,2),
    (1,2,2), (2,2,2), (3,2,2),
    (1,3,2), (2,3,2),
    (2,4,2)
]


ALL_PIECES = [
        # all pieces are 'centered' (rotate around) 000 or 001
        #
        # - lower hex
        # | upper hex
        # both lower and upper hexes

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
        [(0,0,0), (0,1,0), (1,1,0), (1,1,1)],
        # +
        #  - -
        [(0,0,0), (0,1,0), (1,1,0), (0,0,1)],
        # |
        #  + -
        [(0,0,1), (0,1,0), (1,1,0), (0,1,1)]
      ]



class Board:

    def __init__(self):
        board.empty_spaces = ALL_SPACES
        board.pieces = {} #dictionary of xy locations to pieces


    # place a piece on the board, can-place must be true for the piece
    def place(self, piece, loc):
        moved_spots = [loc + spot for spot in piece]

        for spot in moved_spots:
            board.empty_spaces.remove(spot)

        board.pieces.append((loc, piece))

    # removes a piace at a location from the board, 
    # the pieces must already be on the board
    def remove(self, piece, loc):
        moved_spots = [loc + spot for spot in piece]

        for spot in moved_spots:
            board.empty_spaces.append(spot)

        board.pieces.remove((loc, piece))

    # can a piece be placed on a 
    def can_place(self, piece, loc):
        moved_spots = [loc + spot for spot in piece]
        return all(spot in board.empty_spaces for spot in moved_spots)



# piece - a piece is just a list of 3-D coords
# including 000
# all modifications of piecea are functional, they return new pieces



# flip a piece horizontally
# B -> ᗺ
def flip(piece):
    highest = max([x for x,y,z in piece])

    # z coords 0->1 1->0
    # x coords go negative and then add lowest
    return map(lambda (x,y,z): (-x+highest,y,1-z), piece)


# there are 6 directions of orientation for hexagonal pieces
# 360/6 = 60
# rotates a piece 60*rotations degrees clockwise
# rotation might be easier in cube coords
# http://www.redblobgames.com/grids/hexagons/#rotation
def rotate60xdegreesCW(piece, rotations):
    pass
    # rotate around 00







def depth_first_search():
    board = Board()
    pieces = ALL_PIECES

    return place_remaining(board, pieces)


# tries to place all the remaining pieces
# returns either a finished board or False if there is no solution for that branch
# depth first
def place_remaining(board, remaining_pieces):

    if len(remaining_pieces)==0:
        return board

    piece = remaining_pieces[0]
    remaining_pieces = remaining_pieces[1:]

    for rotations in [0,1,2,3,4,5]:
        for location in ALL_SPACES:

            rotated = rotate60xdegrees(piece, rotation)
            if board.can_place(rotated, location):

                board.place(rotated, loc)
                solution = place_remaining(board, remaining_pieces)

                if not solution:
                    board.remove(rotated, loc) #keep looping
                else:
                    return solution

            else:
                pass

    print("failed to place piece %n, backtracking", 12-len(remaining_pieces))
    return False #if no placement for the piece works return false


print(depth_first_search())



