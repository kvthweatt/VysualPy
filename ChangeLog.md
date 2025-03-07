## Changelog:
--------

2/13/25
- Existing nodes now editable and generating new nodes from code.
- Added new key combinations for the **Build Graph**
- **CTRL+Home** - Snap viewport to selected node (zoomed in)
- **CTRL+N** - Snap child nodes nearby

Both of these key combinations need adjustable values added to the preferences menu.

--------

--------

2/10/25
- Updated the Code Build Graph, new node generation working *from new nodes* (**not existing nodes**)
- Added Projects

--------

--------

2/2/25
- Added the Assembler View, shows Python ASM & Native ASM, under the "Run" menu option.

--------

--------

2/1/25
- Updated the IDE to show line numbers
- Updated the File Browser sidebar to have File Browser and Project Browser tabs
- Added CTRL+G (Go to Line) - Need to add Edit menubar option

--------

--------

1/31/25
- Fixed the bug where the entire source file contents would not display in the IDE (scroll bar issue)
- Improved IDE layout with File Browser & Terminal output window bars
- Color coded branched execution (if statements) to orange
- Improved execution path tracing to now show all calls with an exclude list to reduce the amount of nodes generated unnecessarily for builtins and user-defined methods / classes

--------

--------

1/26/25
- Missed update: Added the *Code Build View*
- Comment boxes update to have the resize handle maintain constant size for ease of use.
- Fixed a bug causing all blueprint graph nodes to duplicate upon graph creation.
- Fixed a bug causing rubber band selection to be active while connecting blueprint graph nodes.

--------

--------

1/25/25
- Added the *Execution View*
- Comment boxes updated to maintain constant font size for improved readability.
- Press ALT + Left-Click to pan graphs.

Selecting a node causes all other node lines except the parent and child to dim to easily identify paths.

Added rubberband selection.

Save and load execution graph workspaces (*.veg)

--------

--------

1/17/25
- Added the Blueprint View.

Right click a node's connections to see context options

Create, name, or rename a comment box and resize to wrap around graph node groups.

Save and load blueprint workspaces (*.vpb)

--------
