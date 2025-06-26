# G-AVL

This is G-AVL - a GUI overlay for Mark Drela's Athena Vortex Lattice software.
For more information about the original software, go to https://web.mit.edu/drela/Public/web/avl/.

## Software contents

The G-AVL software consists of two independent parts:
aircraft geometry design and performance calculation.

### GeoDesign

Aircraft Geometry Design Routine, or GeoDesign for short, is a fully autonomous subsystem of G-AVL.
It consists purely of original source code provided in this repository and is not directly connected to AVL.
Its purpose is to create the desired geometry of the aircraft based on fundamental aircraft parameters,
such as wingspan, taper ratio, etc.

### Calc
Performance Calculator, or Calc for short, is an interface for the MIT AVL.
It takes the geometry created by user in the GeoDesign module and transforms it into an AVL-type text file.
Then allows the user to run a measurement or a series of measurements for desired flight parameters,
like the angle of attack, sideslip, etc.
The results can then be accessed directly through the software, exported into a .csv file,
or plotted on the screen using AVL built-in functionalities.

## Guide
### Geometry Creation
*If you already have an .avl file from other sources, skip to the next section.*

G-AVL allows for the creation of a simple geometry of an aircraft. User can choose from presets of configurations
for a wing, a horizontal tail and a vertical tail. Each of the configurations can be further refined
by inserting relevant parameters.

For example, if the user chooses a Simple Tapered wing preset, they can further adjust: wing position, span, MAC,
taper ratio, sweep angle and inclination angle.

#### Available configurations:
* Wing & Horizontal Tail
  * Rectangular
  * Simple Tapered & Swept
  * Double Trapez
  * Delta
  * None (HT only)
* Vertical Tail
  * Rectangular
  * Simple Tapered & Swept
  * Twin
  * None
#### Required Parameters
All parameters have a help window, displayed by clicking the `?` button next to their name, with all the necessary
information.
* Universal
  * Origin Position (x, z) - position of the surface's root section's leading edge, relative to an arbitrary
    origin of the geometry (could be the tip of the fuselage, wing origin point, etc, as long as it is consistent
    for every surface), in meters.
  * Span - the horizontal distance between surface's tips, in meters. Must be positive.
  * MAC - the Mean Aerodynamic Chord of the surface, in meters. Must be positive.
  * Inclination - the built-in AoA of the surface relative to the x-axis, in degrees.
  * Dihedral - the angle between the surface main axis and y-axis, in degrees. Positive for tip up, negative for tip
    down. Must be between -90 and 90.
* Preset Specific
  * Simple Tapered & Swept
    * Taper Ratio - ratio of the tip chord to the root chord - c_tip / c_root. Must be between 1 and 0.
    * Sweep Angle - angle between the y-axis and the 25%MAC line of the surface, in degrees. Positive for backward
      sweep, negative for forward sweep. Must be between -90 and 90.
    * Clearance - Optional Y distance between the root sections of two symmetrical halves of the surface. Change from 0
      only for distinctly separated configurations, like canard or fighter-type tail.
  * Double Trapez
    * TODO
  * Delta
    * Surface Area - the surface area of the wing, in meters squared.
  * Vertical Tail
    * Height - the vertical distance between the root and the tip of the tail.
  * Twin
    * Clearance - Y distance between the root sections of two symmetrical halves of the surface.

#### Airfoil Selection
For each surface, user can select one airfoil. A simple NACA 4-digit airfoil can be defined by its code, while more
complex profiles have to be defined by a .dat file with points. For a flat plate, use NACA 0000.

The file with points should be in the following format:
* Points positions should be given as x/c, y/c, where (0, 0) is the leading edge and (1, ...) is the trailing edge. 
  The x/c between 0 and 1, y/c between -1 and 1.
* One point per line, containing x/c, y/c of the point separated with a comma, spaces, tabs or any combination of those.
* Points can be provided in any order.
* Any lines containing plain text (or anything not fitting the previously defined point format) will be ignored.
* Example of a correct file: http://airfoiltools.com/airfoil/seligdatfile?airfoil=n0012-il (all files from
  airfoiltools.com should work)

#### Control Surfaces
Control surfaces can be added and edited using the `Control Surfaces` sub-menu. When starting from the default geometry,
there will be already Ailerons, Flaps, and Elevator defined.

When adding a new type of control surface onto the wing, press the top-most `+` button. A pop-up will open with
a dropdown menu, where you can select the type of control you want to add.

To add a new strip of control onto the wing, press the `+` button next to the name of the type of control you want to
add. A pop-up will appear where you can input the spanwise position of start and end of the strip, as well as the
chordwise position of the hinge. The strips cannot overlap. **As of now, that means one strip can't start at the same
point another one ends!** If you want to do so, leave a 1 cm gap between the strips.

To edit an existing strip, press the `E` button next to it.

To remove an existing strip or type, press the relevant `-` button.

### Importing geometry from .avl file
DISCLAIMER: Importing an AVL file is not recommended, as the functionality of G-AVL will be limited. It is advised to
recreate the geometry in the app, as it will take no longer than 15 minutes, and will be more reliable. However, if,
for any reason, you do not wish to remake the geometry from scratch, continue reading.

It is possible to import geometry from an existing AVL-type text file. Although it is not guaranteed this geometry will
be editable in GAVL, it can still be used for calculations, as described in the following sections.
To do this, on the top bar press `File` -> `Import`. G-AVL will then try to recognise if the surfaces fit any of the
existing presets. Control Surfaces, as of now, are not supported with importing. If the AVL file has any, they will
stay and (probably) work with `CALC` mode, but you will not be able to edit them in `GEODESIGN`.

#### What NOT to do
* If the imported file contains any of the following keywords:

  `COMPONENT`, `NOWAKE`, `NOALBE`, `NOLOAD`, `CLAF`, `CDCL`, `BODY`

  or uses `iYsym` / `iZsym`, those will be ignored along with its blocks. Make sure the file does not contain any of
  those, or at least that it will work properly without those.
* Do **NOT** use `SURFACE` for things that are not lifting surfaces (like fuselage, nacelle).
* If `AFILE` is used for any section, make sure the path is defined correctly, that is the path is either:
  * absolute - `AFILE C:\...\airfoil.dat`
  * relative with respect to the AVL file - if the AVL file is `...\parent_folder\avl_file.avl`, then a block `AFILE
    airfoil.dat` will be interpreted as `...\parent_folder\airfoil.dat`

### Validation
When the geometry design is finished, and you wish to proceed to the calculations, it is advised to check the
`VALIDATION` mode and ensure that everything is in order. You can check the geometry as seen by AVL, the actual core of
this app that will be conducting the calculations, as well as the reference wingspan, wing area and chord used for
calculation of the parameters.

### Calculations
The calculation menu consists of two sections: left one, where you can set the desired flight parameters, and right one,
where the results will be displayed.

#### Input
Input section contains the following fields:
  * Aircraft Data
    * Alpha - Angle of attack of the aircraft, in degrees.
    * Beta - Sideslip angle of the aircraft, in degrees.
    * Roll, Yaw, Pitch rates - TODO
    * Control Surfaces - Deflection of each control surface, in degrees.
    * Configuration
      * Center of Mass - You can adjust the position of CoM, important for calculations of CM and such.
      * Height - Flight level of the aircraft, in meters above sea level. Must be between 0 and 80 000.
      
Each of the Flight Data parameters can be defined by:
* A single value (the default mode)
* A series of values (ex: from -10 to 10, step 0.5)
* Values from a file

To switch between those modes, press the `single / series` buton at the top of the menu, and choose the desired input
mode for each parameter from the dropdowns. **For every non-constant parameter, there must be an equal number of values
given!**

Also, the values can describe the parameter directly, or by relation with another parameter (ex: flaps deflection can
be defined as 20* or such that CL = 1.2). To use the bound definition, press `bind` button at the right of the field,
and then pick the binding parameter from the dropdown menu. Take notice that the software **DOES NOT KNOW** whether the
parameters you bind are actually related. For example, you can bind `flap` deflection using `CL`, as flaps influence
lift. However, if you bind `flap` using `Roll Moment`, there will be no effect at best, and a crash at worst, as there
is no relation between those two. It remains for your discretion to choose the proper binds.

After all the parameters are inserted correctly, pres the `execute` buton at the bottom of the menu. The app wil display
a `Running...` pop-up, that will disappear upon completion.

#### Output
The calculated values are displayed in the left part of the screen. They are divided into `Forces` and `Stability`,
where the former contains all forces and coefficients of the aircraft, and the latter displays all stability
derivatives.

For each measurement, you can generate plots using the buttons below the result display.

Using the `Save to .csv` button, you can save all data from every measurement into a text file, readable by most
software:

Excel: `Data` -> `From Text/CSV` -> `Transform Data` -> `Transform` -> `Use Firts Row as Headers` -> `File` ->
`Close & Load`

MATLAB: `data = readtable(path_to_csv);` -> access series as f.e. `data('Alpha')`. You can get the file path as text
by: `File Explorer` -> Go to your .csv file -> `Right Click` -> `Copy as Path` -> paste it in MATLAB using `Ctrl+V`.
