# G-AVL

This is G-AVL - a GUI overlay for Mark Drela's Athena Vortex Lattice software.
For more information about the original software, go to https://web.mit.edu/drela/Public/web/avl/.

## Software contents

The G-AVL software consists of two independent parts:
aircraft geometry design routine and performance calculation.

### GeoDesign

Aircraft Geometry Design Routine, or GeoDesign for short, is a fully autonomous subsystem of G-AVL.
It consists purely of original source code provided in this repository and is not directly connected to AVL.
Its purpose is to create the desired geometry of the aircraft based on fundamental aircraft parameters,
such as wingspan, taper ratio, etc.
The created geometry can also be quickly converted into an AVL-type string for use by Calc module or exporting.

Back-end structure:
 - Geometry (aircraft data)
   - Surfaces
     - Sections
       - Airfoil
       - Control Surface

Front-end structure:
 - Geometry Display
 - Left Menu

### Calc
Performance Calculator, or Calc for short, is an interface for the MIT AVL.
It takes the geometry created by user in the GeoDesign module and transforms it into an AVL-type text file.
Then allows the user to run a measurement or a series of measurements for desired flight parameters,
like the angle of attack, sideslip, etc.
The results can then be accessed directly through the software, exported into a .csv file,
or plotted on the screen using AVL built-in functionalities.

Calculation scheme:
- Reading the data input from the user
- Converting the aircraft geometry into a temporary .avl text file
- Creating a temporary .run text file based on the user data
- Calling AVl.exe with the two files as arguments
- For each element of the data series:
  - Running the run case in the AVL
  - Saving the data to a temporary file
- Closing the AVL
- Reading, transforming, and presenting the obtained data