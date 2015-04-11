


I'm trying to write a solver for a puzzle a friend gave me 

It's a triangular case with hexagonal pieces, three pieces high

     /.\
    /. .\
   /. . .\
  /. . . .\
 /. . . . .\
 ----------

There are 11 pieces, all two layers thick 

- =  hexagon on bottom layer only
| =  hexagon on top layer only
+ =  hexagon on both layers


1.
 - +
  - -

2.
 - +
  - -

3.
  + - -

4.
  - + |

5.
  - + -

6.
 - |
  +

7.
 - -
  +

8.
 -
  + |

9.
 -
  - +

10.
 +
  - -

11.
 |
  + -



We're searching for a solution which places all 11 pieces in the triangle (using all the empty spaces)

Here's an example solution which places only 9 pieces:

Pieces:

 <0>: [(0, 1, 1), (0, 0, 1), (1, 1, 1), (1, 0, 1), (1, 1, 0)]
 <1>: [(1, 3, 2), (1, 2, 2), (2, 3, 2), (2, 2, 2), (2, 3, 1)]
 <2>: [(2, 0, 2), (3, 0, 2), (4, 0, 2), (2, 0, 1)]
 <3>: [(2, 0, 0), (3, 0, 0), (3, 0, 1), (4, 0, 1)]
 <4>: [(4, 0, 0), (3, 1, 0), (3, 2, 0), (3, 1, 1)]
 <5>: [(2, 4, 1), (1, 3, 1), (1, 3, 0), (2, 3, 0)]
 <6>: [(3, 2, 2), (3, 1, 2), (2, 1, 2), (2, 1, 1)]
 <7>: [(2, 1, 0), (2, 2, 0), (2, 2, 1), (3, 2, 1)]
 <8>: [(1, 0, 0), (0, 1, 0), (1, 2, 0), (1, 2, 1)]

Grid:

    First Layer           Second Layer          Third Layer
000 <8> <3> <3> <4>   <0> <0> <2> <3> <3>   002 102 <2> <2> <2>
  <8> <0> <7> <4>       <0> <0> <6> <4>       012 112 <6> <6>
    <8> <7> <4>           <8> <7> <7>           <1> <1> <6>
      <5> <5>               <5> <1>               <1> <1>
        240                   <5>                   242


