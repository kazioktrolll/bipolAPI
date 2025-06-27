# G-AVL

This is G-AVL - a GUI overlay for Mark Drela's Athena Vortex Lattice software.
For more information about the original software, visit [MIT/AVL](https://web.mit.edu/drela/Public/web/avl/).

This software uses GhostScript Portable for image conversion. For more information, visit
[PortableApps/GhostScript](https://portableapps.com/apps/utilities/ghostscript_portable).

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
It takes the geometry created by the user in the GeoDesign module and transforms it into an AVL-type text file.
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
taper ratio, sweep angle, and inclination angle.

#### Available configurations:
* Wing & Horizontal Tail
  * Rectangular
  * Simple Tapered
  * Double Trapez
  * Delta
  * None (HT only)
* Vertical Tail
  * Vertical Rectangular
  * Vertical Tapered
  * Simple Tapered
  * None
#### Required Parameters
All parameters have a help window, displayed by clicking the `?` button next to their name, with all the necessary
information.
* Universal
  * Position (x, z) – position of the surface's root section's leading edge, relative to an arbitrary
  origin of the geometry (could be the tip of the fuselage, wing origin point, etc., as long as it is consistent
  for every surface), in meters.
  * Span – the horizontal distance between surface's tips, in meters. Must be positive.
  * MAC – the Mean Aerodynamic Chord of the surface, in meters. Must be positive.
  * Inclination – the built-in AoA of the surface relative to the x-axis, in degrees.
  * Dihedral – the angle between the surface main axis and y-axis, in degrees. Positive for tip up, negative for tip
  down. Must be between -90 and 90.
* Preset Specific
  * Simple Tapered & Swept
    * Taper Ratio – ratio of the tip chord to the root chord - c_tip / c_root. Must be between 0 and 1.
    * Sweep Angle – angle between the y-axis and the 25%MAC line of the surface, in degrees. Positive for backward
    sweep, negative for forward sweep. Must be between -90 and 90.
    * Clearance – Optional Y distance between the root sections of two symmetrical halves of the surface. Change from 0
    only for distinctly separated configurations, like canard or fighter-type tail.
  * Double Trapez
    * Root chord – Chord of the wing at the root, in meters. Must be positive.
    * Mid Chord – Chord of the wing at the seam, in meters. Must be positive.
    * Tip Chord – Chord of the wing at the tip, in meters. Must be positive.
    * Seam Spanwise Position – the position of the seam as a fraction of the total span. Must be between 0 and 1.
  * Delta
    * Surface Area – the surface area of the wing, in meters squared.
  * Vertical Tail
    * Height – the vertical distance between the root and the tip of the tail.
  * Twin
    * Clearance – Y distance between the root sections of two symmetrical halves of the surface.

#### Airfoil Selection
For each surface, the user can select one airfoil. A simple NACA 4-digit airfoil can be defined by its code, while more
complex profiles have to be defined by a .dat file with points. For a flat plate, use NACA 0000.

The file with points should be in the following format:
* Points positions should be given as x/c, y/c, where (0, 0) is the leading edge and (1, ...) is the trailing edge. 
The x/c between 0 and 1, y/c between -1 and 1.
* One point per line, containing x/c, y/c of the point separated with a comma, spaces, tabs, or any combination of
those.
* Points can be provided in any order.
* Any lines containing plain text (or anything not fitting the previously defined point format) will be ignored.
* Example of a correct file: [AirfoilTools/naca0012](http://airfoiltools.com/airfoil/seligdatfile?airfoil=n0012-il)
(all files from [AirfoilTools](http://airfoiltools.com) should work)

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
recreate the geometry in the app, as it will take no longer than 15 minutes and will be more reliable. However, if,
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
this app that will be conducting the calculations, as well as the reference wingspan, wing area, and chord used for
calculation of the parameters.

### Calculations
The calculation menu consists of two sections: the left one, where you can set the desired flight parameters, and the
right one, where the results will be displayed.

#### Input
The input section contains the following fields:
  * Aircraft Data
    * Alpha – Angle of attack of the aircraft, in degrees.
    * Beta – Sideslip angle of the aircraft, in degrees.
    * Roll, Yaw, Pitch rates – TODO
    * Control Surfaces – Deflection of each control surface, in degrees.
    * Configuration
      * Center of Mass – You can adjust the position of CoM, important for calculations of CM and such.
      * Height – Flight level of the aircraft, in meters above sea level. Must be between 0 and 80 000.
      
#### Series of Measurements
Each of the Flight Data parameters can be defined by:
* A single value (the default mode)
* A series of values (ex: from -10 to 10, step 0.5)
* Values from a file

To switch between those modes, press the `single / series` buton at the top of the menu, and choose the desired input
mode for each parameter from the dropdowns. **For every non-constant parameter, there must be an equal number of values
given!**

To import a series of values from a file:
1. Ensure the file is in CSV format. If the data in the file has a header line, it will be used to name the aviable
series in step 7. If not, series will be named `Series 1`, `Series 2`, ...
2. In `Series` mode, press `Add File` at the top
3. Select your CSV file
4. Change the mode of the parameter you want to import to `From File`
5. Press `Choose File`
6. In `Choose File`, select the file you just added
7. In `Choose Series`, select the series from the file
8. Press `Set`
9. Check if the series has the correct number of values (the number in brackets)


#### Binding Parameters
The values can describe the parameter directly, or by relation with another parameter (ex: flaps deflection can
be defined as 20 degrees, or such that CL = 1.2). To use the bound definition, press `bind` button at the right of the
field, and then pick the binding parameter from the dropdown menu. Take notice that the software **DOES NOT KNOW**
whether the parameters you bind are actually related. For example, you can bind `flap` deflection using `CL`, as flaps
influence lift. However, if you bind `flap` using `Roll Moment`, there will be no effect at best, and a crash at worst,
as there is no relation between those two. It remains for your discretion to choose the proper binds.

After all the parameters are inserted correctly, pres the `execute` buton at the bottom of the menu. The app wil display
a `Running...` pop-up, that will disappear upon completion.

#### Output
The calculated values are displayed in the left part of the screen. They are divided into `Forces` and `Stability`,
where the former contains all forces and coefficients of the aircraft, and the latter displays all stability
derivatives.

For each measurement, you can generate plots using the buttons below the result display.

Using the `Save to .csv` button, you can save all data from every measurement into a text file, readable by most
software.

## Example Session
**Before you start, you need to know your:**
* Wing's, Horizontal, and Vertical Tails' Spans,
* Wing's Horizontal, and Vertical Tails' Mean Aerodynamic Chords (MACs),
* If any of the surfaces is tapered or swept, then the respective values are also needed,
* Wing's, Horizontal, and Vertical Tails' airfoils (either 4-digit NACA codes or files with points),
* Positions of Horizontal and Vertical Tails in relation to the Wing,
* Position of Center of Mass (CoM) relative to the wing,
* Type, spanwise position, and chordwise hinge position of all control surfaces your aircraft has – ailerons, flaps,
elevators & rudder.

1. Open the app.
2. Create a new default geometry by clicking `New` or `File` -> `New`.
3. Edit the wing:
   1. Select the correct shape of the wing from the dropdown menu at the top left.
   2. Fill the required geometrical parameters:
      1. For any wing – Span, MAC, and position (it is recommended to leave wing's position as [0,0,0] and use it as
      a reference for the other positions).
      2. Additionally, for a simple tapered wing – Taper Ratio, and Sweep Angle,
      3. Additionally, for a double trapez wing - Root & Mid & Tip Chords, Span, Spanwise Seam Position, and
      Sweep Angle.
      4. The remaining parameters are not critical for an entry-level analysis and can be adjusted later.
      5. Angled variants of empennage, like V-shape tail, can be created by setting `Dihedral` to a significant value.
   4. Edit / Add the control surfaces in the menu at the middle left.
   5. Select the airfoil in the menu at the bottom left:
      1. For 4-digit NACA - Press `NACA` and input the code,
      2. For other airfoils - Press `Load from file` and select the proper file.
3. Repeat step 3 for the Horizontal Tail and the Vertical Tail.
4. When finished, press `Validation` at the Top Bar.
5. Ensure the displayed geometry is correct, and that the displayed reference values for surface, span, and chord are
also correct.
6. When finished, press `Calculations` at the Top Bar.
7. Input the calculation data:
   1. `Alpha` - Angle of Attack, in degrees,
   2. `Beta` - Sideslip Angle, in degrees,
   3. `Roll, Pitch & Yaw Rates` - as named,
   4. `Control Surfaces' deflections` - as named, in degrees,
   5. `Center of Mass` - XYZ position of the center of mass, in meters,
   6. `Altitude` - flight altitude, in meters.
8. Press `Execute`.
9. Read the results from the right section. For advanced analysis, stability derivatives can be accessed by changing the
mode from `Forces` to `Stability`.
10. Additional graphs can be generated and saved by clicking the buttons at the bottom right.
11. For a series of measurements:
    1. Switch from `Single` to `Series` at the top left.
    2. Select a proper mode for each parameter – for the simplest series, a range of AoA, change `Alpha` from `Constant`
    to `Range`, and input the minimal, maximal values and the step of the series.
    3. Check if the number of values in the series is correct – the number in brackets next to the entry field.
    4. If more than one parameter is serialised, check if all the non-constant parameters have the same number of
    values.
    5. Press `Execute`.
    6. To switch between the measurements in the series, use the newly displayed page menu at the top left.
    7. The plot buttons at the bottom left display the graphs for the currently selected measurement.
    8. Consider saving the results to a file and working on them in Excel or MATLAB, by pressing `Save to .csv`. This
      will generate a file containing all the values in all the measurements. To import this file into another software:
       1. Excel: `Data` -> `From Text/CSV` -> `Transform Data` -> `Transform` -> `Use Firts Row as Headers` -> `File` ->
       `Close & Load`
       2. MATLAB: `data = readtable(path_to_csv);` -> access series as f.e. `data('Alpha')`. You can get the file path
       as text by: `File Explorer` -> Go to your .csv file -> `Right Click` -> `Copy as Path` -> paste it in MATLAB
       using `Ctrl+V`.

**FOR MORE DETAILED DESCRIPTIONS OF FUNCTIONS, READ THE PREVIOUS PART, *GUIDE*.**
