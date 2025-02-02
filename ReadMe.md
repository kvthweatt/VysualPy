# VysualPy / Vysual Python
A node graph-based IDE for any language, designed to allow users to build code faster with live node-to-code blueprints.
Featuring 3 blueprint node graph workspaces, each with their own utility. Two of the graphs are for visualizing your code,
they are the Blueprint graph and the Execution graph.

![image](https://github.com/user-attachments/assets/c459a295-b27a-46dc-8b77-ed4e6c272f96)

The Code Building graph is designed to be a live editing tool,
where you can type into the empty space of the graph and a code node is created, and the code inside that node
is updated in the IDE source file all automatically. If you call a function that doesn't exist (like modeling your code) it
will create an empty function according to how you called it.

If you type the following into the Build graph:

```py
def main():
    test()
    return
```

And `test()` didn't exist already, it will be created in the source file, and in the Build graph as a node, and will be linked
with an execution line to `main()`

Inspired by Unreal Engine blueprints and disassembler execution flow graphs, this IDE makes coding more like using building
blocks, and less like building the blocks themselves. While you can still build your blocks with whatever and however you
like, processes like refactoring become easier, and building applications becomes faster.

**Please Note**: While the base IDE is being developed it will only support Python. In a future version, plugins will
be added allowing users to define custom languages or add an existing language. In the IDE Configuration menu you will
also be able to set your compiler, linker, library or resource paths, and more.

- Please report any bugs to kvthweatt@gmail.com or [here](https://github.com/kvthweatt/VysualPy/issues/new?template=Blank+issue)

Execution Graph preview:
![image](https://github.com/user-attachments/assets/ba05022e-b4b6-4e33-b307-3b20803edc59)
![image](https://github.com/user-attachments/assets/490d8a96-d00c-4a51-b7ce-b74f4c298fea)

### Known Bugs:

- None currently.

--------

# To-Do:
- Breakpoints
- Projects
- Stack view & ability to directly modify the stack
- More granular control over color coding for blueprint graphs.
- Improve the Preferences menu and configuration.
- Add a "Snap connected nodes nearby" context option along with snap distance option to Preferences
- Plugin support to extend IDE features.
- Extend support for more languages, starting with C, C++, C#
- Translations

# Attribution
- Uses [Qt5](https://github.com/qt/qt5)

