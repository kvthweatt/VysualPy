## Changelog:
--------

8/29/25 - Node System Architecture Refactoring
- Implemented unified BaseNode system with abstract base class
- Added mixin architecture: RenderMixin, InteractionMixin, EditableMixin
- Created three specialized node types: BlueprintNode, ExecutionNode, BuildableNode
- Enhanced connection system with bezier curves and hover effects
- Added multi-selection support with rubber band selection
- Implemented group operations: align, distribute, move multiple nodes
- Added tree alignment shortcuts (Ctrl+S for children, Ctrl+Shift+S for full tree)
- Created comprehensive debug environment (debug_node_system.py)
- Added NodeCreationDialog with rich node creation interface
- Implemented connection dragging to move connected nodes together
- Added context menus for node creation and management
- Enhanced visual system with gradients and state-based styling
- Created backward compatibility layer for existing code
- Added type-safe port system with connection validation
- Implemented GlobalNodeTextEditor for BuildableNode editing

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
