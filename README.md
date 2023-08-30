# PySon

## Description

Package for interfacing with Sonnet to automate designing geometries, running simulations, and post-processing data. 

## Table of Contents



## Getting Started

### Requirements

- Python ≥ 3.6
- Required: numpy, matplotlib, scikit-rf, shapely
- Optional:
    - Matlab Engine ([Compatible Python Versions](https://www.mathworks.com/support/requirements/python-compatibility.html))
    - SonnetLab v8.0 ([Download](https://www.sonnetsoftware.com/support/downloads/SonnetLab_v8.0.zip))

### Installation

First, install Python dependencies with pip,

```bash
pip install numpy matplotlib scikit-rf shapely
```

Then simply place [pyson.py](http://pyson.py) in an accessible folder and import it via,

```python
import pyson
```

- **Matlab engine / Sonnetlab support**
    
    Begin by downloading Sonnetlab from [here](https://www.sonnetsoftware.com/support/sonnet-suites/sonnetlab.html), rename the code’s parent directory to “sonnetlab,” and place it in the same directory as [pyson.py](http://pyson.py) for example like this:
    
    ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ea17a2f1-0a01-4e03-b6db-1213dfa69da9/Untitled.png)
    
    Next if you are using a version of Sonnet unsupported by Sonnetlab (16.52 included!) you will need to edit SonnetPath.m to the following
    
    ```matlab
    aSonnetPath='C:\\Program Files (x86)\\Sonnet Software\\16.52';
    aSonnetInstallDirectoryList={'C:\\Progra~2\\Sonnet Software\\16.52'};
    aSonnetInstallVersionList='"00-00-0000"';
    return
    ```
    
    Next to get Matlab engine to work run the following commands
    
    - As administrator in CMD.exe:
    
    ```bash
    cd “matlabroot\\extern\\engines\\python”
    python setup.py install
    
    ```
    
    - In MATLAB
    
    ```
    cd (fullfile(matlabroot, ‘extern’, ‘engines’,’python))
    system (‘python setup.py install’)
    
    ```
    

## User Documentation

### pyson.open_son

```python
open_son(file_name, sonnet_path="", temp=False, ml_backend=False, overwrite=None)
```

Opens an existing Sonnet file with a given name. Returns a PySon project.

- **Arguments**
    
    **file_name: str**
    
    Name / directory of Sonnet file
    
    **sonnet_path: str, *optional***
    
    Directory for specific sonnet version. Default is C:\Program Files (x86)\Sonnet Software\16.52\bin\” **    
    temp: Bool, **optional**
    
    **Dangerous.** Deletes Sonnet file and all generated directories upon garbage collection. Not recommended for open_son and primarily for internal use.
    
     **ml_backend: bool, *optional***
    
    Use Matlab / Sonnetlab backend rather than native parser. Enables some extra features and may have better compatibility and stability with some Sonnet versions.
    
    **overwrite: PySon project, *optional***
    
    Requires ml_backend. Overwrites an existing matlab engine instance rather than spawning a new one. Reduces resource overhead and speeds up project creation.
    
- **Examples**
    
    ```python
    pyson.open_son("project_files\\existing.son")
    ```
    

### pyson.new_son

```python
new_son(file_name, sonnet_path="", temp=False, ml_backend=False, overwrite=None)
```

Creates a new Sonnet file with a given name. Returns a PySon project.

- **Arguments**
    
    **file_name**: str
    
    Name / directory of Sonnet file
    
    **sonnet_path: str, *optional***
    
    Directory for specific sonnet version. Default is C:\Program Files (x86)\Sonnet Software\16.52\bin\” 
    
    **temp: Bool, *optional***
    
    Deletes Sonnet file and all generated directories upon garbage collection. 
    
     **ml_backend: bool, *optional***
    
    Use Matlab / Sonnetlab backend rather than native parser. Enables some extra features (but restricts others) and may have better compatibility and stability with some Sonnet versions.
    
    **overwrite: PySon project, *optional***
    
    Requires ml_backend. Overwrites an existing matlab engine instance rather than spawning a new one. Reduces resource overhead and speeds up project creation.
    
- **Examples**
    
    ```python
    pyson.new_son("project_files\\new.son")
    ```
    

### pyson.from_template

```python
from_template(file_name, new_file="", sonnet_path="", temp=False, ml_backend=False, overwrite=None)
```

Use an existing Sonnet file as a template to create a new file. Returns a PySon project.

- **Arguments**
    
    **file_name**: str
    
    Name / directory of Sonnet template file
    
    **new_file: str, *optional***
    
    Name / directory of output file. Default is {file_name}-{1,2,…}.son
    
    **sonnet_path: str, *optional***
    
    Directory for specific sonnet version. Default is C:\Program Files (x86)\Sonnet Software\16.52\bin\” 
    
    **temp: Bool, *optional***
    
    Deletes Sonnet file and all generated directories upon garbage collection. 
    
     **ml_backend: bool, *optional***
    
    Use Matlab / Sonnetlab backend rather than native parser. Enables some extra features (but restricts others) and may have better compatibility and stability with some Sonnet versions.
    
    **overwrite: PySon project, *optional***
    
    Requires ml_backend. Overwrites an existing matlab engine instance rather than spawning a new one. Reduces resource overhead and speeds up project creation.
    
- **Examples**
    
    ```python
    pyson.from_template("project_files\\template.son", new_file="output_file.son")
    ```
    

### project.save

```python
save(file_name="")
```

Save a PySon project to disk. Returns nothing.

- **Arguments**
    
    **file_name**: **str, *optional***
    
    Name / directory of Sonnet project if not the same as before.
    
- **Examples**
    
    ```python
    project = pyson.new_son("new.son")
    # Apply modifications
    project.save()
    ```
    

### project.add_metal_polygon

```python
add_metal_polygon(metalization_level, xcoords, ycoords, metal_type="", tech_layer="", inherit=True, header=[])
```

Add a metal polygon to the project. Returns a polygon id. 

- **Arguments**
    
    **metalization_level: int**
    
    Level to add polygon
    
    **xcoords: array-like floats**
    
    List of x coordinates for vertices.
    
    **ycoords: array-like floats**
    
    List of y coordinates for vertices. **
    
    **metal_type: str, *optional***
    
    Name of metal to use, default is lossless superconductor. 
    
     **tech_layer: str, *optional***
    
    Name of tech layer if metal is added as part of it.
    
    **header: array-like, optional**
    
    Array of overriding properties for the polygon. Primarily for internal use.
    
- **Examples**
    
    ```python
    xc = [50,150,150,50]
    yc = [50,50,150,150]
    project.add_metal_polygon(0,xc,yc)
    ```
    
    ![box.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d0bd3e66-4753-45de-a291-bf6a69282098/box.png)
    

### project.add_std_port

```python
add_std_port(polygon, vertex, port_number=None, res=50, react=0, ind=0, cap=0)
```

Adds a port to the selected polygon and vertex. Returns a port number. 

- **Arguments**
    
    **polygon: int**
    
    ID on which to add a port
    
    **vertex: int**
    
    Vertex after which to add a port i.e. vertex=2 places a port on the edge between the 2nd and 3rd vertices.
    
    **port_number: int, *optional***
    
    Force a certain port_number instead of incrementing by 1. **
    
    **res: float, *optional***
    
    Port resistance. 
    
    **react: float, *optional***
    
    Port reactance. 
    
    **ind: float, *optional***
    
    Port inductance. 
    
    **cap: float, *optional***
    
    Port capacitance. 
    
- **Examples**
    
    ```python
    xc = [50,150,150,50]
    yc = [50,50,150,150]
    box = project.add_metal_polygon(0,xc,yc)
    project.add_std_port(box, 0)
    ```
    
    ![box_port.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/7885f8ec-4290-45b6-b3c3-79c332f2fba1/box_port.png)
    

### project.delete_polygon

```python
delete_polygon(index)
```

Deletes a polygon, supported only in Python backend. Returns nothing.

- **Arguments**
    
    **index: int**
    
    Polygon ID to delete.
    
- **Examples**
    
    ```python
    box = project.add_metal_polygon(0,xc,yc)
    project.delete_polygon(box)
    ```
    

Known Bugs:

### project.box_size

```python
box_size()
```

Returns two floats (x size, y size)

- **Examples**
    
    ```python
    x,y = project.box_size()
    ```
    

### project.change_box_size

```python
change_box_size(x,y)
```

Changes box size to specified values. Returns nothing.

- **Arguments**
    
    **x: float**
    
    New x size for box
    
    **y: float**
    
    New y size for box
    
- **Examples**
    
    ```python
    project.change_box_size(200,200)
    ```
    

### project.cell_size

```python
cell_size()
```

Returns two floats (x size, y size)

- **Examples**
    
    ```python
    cx,cy = project.cell_size()
    ```
    

### project.change_cell_size

```python
change_cell_size(x,y)
```

Changes cell size to specified values. Returns nothing.

- **Arguments**
    
    **x: float**
    
    New cell x size
    
    **y: float**
    
    New cell y size
    
- **Examples**
    
    ```python
    project.change_cell_size(0.1,0.1)
    ```
    

### project.change_dielectric_layer_thickness

```python
change_dielectric_layer_thickness(layer, thickness)
```

Changes thickness of a specified dielectric layer. Returns nothing.

- **Arguments**
    
    **layer: int**
    
    Layer index to change.
    
    **thickness: float**
    
    New thickness for layer
    
- **Examples**
    
    ```python
    # Set the 0-th layer to be 200 units thick
    project.change_dielectric_layer_thickness(0,200)
    ```
    

### project.set_valvar

```python
set_valvar(name, value=None, vartype=None, descr=None)
```

Set a Sonnet project variable. Returns nothing.

- **Arguments**
    
    **name: string**
    
    Variable to change.
    
    **value: float, *optional***
    
    New value for layer. None ⇒ unchanged.
    
    **vartype: str* **
    
    Variable type as a string. None ⇒ unchanged.
    
    Length: “LNG”
    
    Inductance: “IND”
    
    Other type strings can be found by opening the .son file as a txt and searching for valvar.
    
    **descr: str, *optional***
    
    Variable description. None ⇒ unchanged.
    
- **Examples**
    
    Consider the following inductor controlled by a variable:
    
    ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9852e9b3-8fa9-4d37-9975-d0f6c77534ac/Untitled.png)
    
    We can set its values to this:
    
    ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/7ca11c39-d217-4865-acac-dab0fa29f167/Untitled.png)
    
    Using this:
    
    ```python
    project.set_valvar("L1", 21.22, "IND", "Ideal Component Value")
    ```
    

### project.add_abs_frequency_sweep

```python
add_abs_frequency_sweep(start,stop)
```

Set an adaptive frequency sweep range. Returns nothing.

- **Arguments**
    
    **start: float**
    
    Sweep start frequency
    
    **stop: float**
    
    Sweep stop frequency
    
- **Examples**
    
    ```python
    # Add a sweep from 6 to 8 GHz (standard units)
    project.add_abs_frequency_sweep(6,8)
    ```
    

### project.set_speed

```python
set_speed(speed)
```

Set simulation coarseness / edge meshing level, dictates speed and memory usage. Returns nothing.

- **Arguments**
    
    **speed: int**
    
    Coarseness / edge meshing level (0,1,2 where 0 is finest/slowest). 
    
- **Examples**
    
    ```python
    # Set coarseness / edge meshing to fine
    project.set_speed(0)
    ```
    

### project.targ_abs

```python
targ_abs(resolution)
```

Set the target number of frequencies to measure from an adaptive frequency sweep. Disabled if res_abs is enabled. Returns nothing. 

- **Arguments**
    
    **resolution: int**
    
    Number of frequencies to target. 
    
- **Examples**
    
    ```python
    project.targ_abs(300)
    ```
    

### project.res_abs

```python
res_abs(enable, resolution)
```

Set the desired resolution for an adaptive frequency sweep. Disables res abs. Returns nothing.

- **Arguments**
    
    **enable: bool**
    
    Enable a specific resolution rather than a target number of frequencies.
    
    **resolution: float**
    
    Resolution to target. 
    
- **Examples**
    
    ```python
    # Set coarseness / edge meshing to fine
    project.set_speed(0)
    ```
    

### project.add_mdif_output

```python
add_mdif_output(file_output="")
```

Add an mdif output to simulations. Returns nothing.

- **Arguments**
    
    **file_output: str, *optional***
    
    MDIF file to output to. Default is $BASENAME.mdf, which is the sonnet file but with .son →.mdf.
    
- **Examples**
    
    ```python
    add_mdif_otuput("out.mdf")
    ```
    

### project.rm_mdif_output

```python
rm_mdif_output(file_output="")
```

Remove a set mdif output, however, it does not delete any files. Returns nothing.

- **Arguments**
    
    **file_output: str, *optional***
    
    MDIF output to remove. Default to remove is $BASENAME.mdf.
    
- **Examples**
    
    ```python
    rm_mdif_output("out.mdf")
    ```
    

### project.simulate_network

```python
simulate_network(file_output="")
```

Runs a Sonnet EM simulation of the current project. Returns a Scikit-RF NetworkSet where (if a sweep hasn’t otherwise been defined) the 0-th element is the simulation network.

- **Arguments**
    
    **file_output: str, *optional***
    
    MDIF file to output to. Default creates a temporary file that is removed afterwards.
    
- **Examples**
    
    ```python
    # Run a simulation from 6-8GHz and get its skrf.Network
    project.add_abs_frequency_sweep(6,8)
    network = project.simulate_network()[0]
    ```
    

### project.sonnet_call_em

```python
sonnet_call_em(file_name="", options="")
```

Run sonnet EM on a file with the given options. Generally for internal use. Returns nothing.

- **Arguments**
    
    **file_name: str, *optional***
    
    File to run EM.exe on
    
    **options: str, *optional***
    
    Options to run EM.exe with
    
- **Examples**
    
    ```python
    project.sonnet_call_em(project.file_name)
    ```
    

### project.draw

```python
draw(layer=None, metal_args=dict(color="#209fb5", edgecolor="#4c4f69", hatch="///"), 
             metal_argf = None, ports=True, figsize=(5,5), 
             port_box=dict(boxstyle="square", fc="#eff1f5", ec="#4c4f69", alpha=1), port_font_size=8)
```

Draws a sonnet project using matplotlib. Returns matplotlib figure and axes objects.

- **Arguments**
    
    **figsize: (int, int), *optional***
    
    Size of plot
    
    **layer: int, *optional***
    
    Layer to draw. Default is the top layer that contains metal.
    
    **metal_args: dict, *optional***
    
    Arguments to pass to each fill function when drawing metal.
    
    **metal_argf: function, *optional***
    
    Function to run to determine each fill function’s arguments, function is passed the polygon format described in pyson.extract_polygons. Overwrites metal_args.
    
    **ports: bool, *optional***
    
    Enable drawing ports
    
    **port_box: dict, *optional***
    
    Box parameters for port. Passed to plt.text(bbox=port_box)
    
    **fontsize: float, *optional***
    
    Port font size 
    
- **Examples**
    
    Both of these examples use the simple box / port designed in project.add_metal_polygon and project.add_std_port.
    
    ```python
    # Basic draw
    fig, ax = project.draw()
    ```
    
    ![download.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/65d7f134-cc56-4586-b2c0-f581ac787845/download.png)
    
    ```python
    # Fancy gray / labeled drawing using metal_argf
    metal_argf = lambda x: dict(color="lightgrey", label=("Tech Layer " + str(x[-2]) if x[-2] is not "" else "Metal " + str(x[0])))
    fig, ax = project.draw(figsize=(20,20), port_font_size=20, metal_argf=metal_argf)
    xlim(0,200)
    ylim(0,200)
    
    #remove duplicate labels
    handles, labels = gca().get_legend_handles_labels()
    newLabels, newHandles = [], []
    for handle, label in zip(handles, labels):
        if label not in newLabels:
            newLabels.append(label)
            newHandles.append(handle)
    
    legend(newHandles, newLabels, loc=2, prop={'size':28})
    xlabel("Width (µm)", fontsize=28)
    xticks(fontsize=26)
    yticks(fontsize=26)
    ylabel("Height (µm)", fontsize=28)
    ```
    
    ![box_port.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/7885f8ec-4290-45b6-b3c3-79c332f2fba1/box_port.png)
    

## Parser Documentation

### project.son_dict

```python
project.son_dict
```

Not a function. Dictionary parses the Sonnet file and uses blocks as keys and strings for each line in the individual block. Additionally the file header is stored under “file_header” and the block “GEO” is not parsed into individual lines due to its particularly complicated nature. 

- **Examples**
    
    The following lines in the .son file:
    
    ```
    CONTROL
    ABS
    OPTIONS  -d
    SPEED 0
    CACHE_ABS 1
    Q_ACC N
    END CONTROL
    ```
    
    Would be parsed as follows:
    
    ```
    project.son_dict["CONTROL"] = ['ABS', 'OPTIONS -d', 'SPEED 0', 'CACHE_ABS 1', 'Q_ACC N']
    ```
    

### pyson.extract_polygons

```python
extract_polygons(unpacked)
```

Extract polygons from an unpacked dict of a sonnet file. Complicated return type.

- **Arguments**
    
    **unpacked: dict**
    
    Dictionary corresponding to a Sonnet project.
    
- **Returns**
    
    Returns a list of lists of the form,
    
    ```python
    [header, [vertex0, vertex1,...]]
    header = [metalization level, number of vertices, metal_type, ?, ID, ?, ?, ?, ?, ? ,? , ? , ? , ?, tech_layer, inherits]
    vertex0 = [x0,y0]
    ```
    
    Corresponding to each polygon in the project. Question marks indicate a parameter that is not understood and is fixed to some common default.
    
- **Examples**
    
    ```python
    # Get the first polygon listed in the file and find its ID
    polys = extract_polygons(project.son_dict)
    poly_id = polys[0][0][4]
    ```
    

### pyson.extract_ports

```python
extract_ports(unpacked, indices=False)
```

Extract ports from an unpacked dict of a sonnet file. Complicated return type.

- **Arguments**
    
    **unpacked: dict**
    
    Dictionary corresponding to a Sonnet project.
    
    **indices: bool, *optional***
    
    Whether to return a list of line numbers corresponding to ports instead of the list of port dicts.
    
- **Returns**
    
    Either returns line numbers corresponding to ports (indices=True) or a list of dicts with the following elements depending on port type.
    
    ```python
    # STD / All
    port_type
    poly
    points
    vertex
    port_number
    resistance
    reactance
    inductance
    capacitance
    x
    y
    
    # CUP
    calib_group
    cup_group
    cup_group_type
    cup_id
    cup_grndref
    cup_twtype
    
    # AGND
    agnd_calib_type
    agnd_plane_Length
    agnd_calib_length
    ```
    
- **Examples**
    
    ```python
    # Get the first port listed in the file and get its attached polygon
    ports = extract_ports(project.son_dict)
    poly = ports["poly"]
    ```
    

### pyson.extract_ports

```python
extract_box(unpacked)
```

Extract box data from an unpacked dict of a sonnet file. Complicated return type.

- **Arguments**
    
    **unpacked: dict**
    
    Dictionary corresponding to a Sonnet project.
    
- **Returns**
    
    Returns a list with two lists, the first is the details of the box and the second is  a list of lists corresponding to each defined layer.
    
    ```python
    [box, [layer0, layer1,...]]
    box = [?, x_size, y_size, x_cell_number, y_cell_number, ?, ?]
    layer0 = [thickness, ?, ?, ...]
    ```
    
- **Examples**
    
    ```python
    # Get the x dimension of the box
    box = pyson.extract_box(project.son_dict)
    x = box[0][1]
    ```
    

### pyson.repack_geo

```python
repack_geo(unpacked, polygons=None, ports=None, box=None)
```

Repack the geometry section of an unpacked Sonnet dict. Returns a Sonnet dict.

- **Arguments**
    
    **unpacked: dict**
    
    Dictionary corresponding to a Sonnet project.
    
    **polygons: list**
    
    List of polygons as discussed in extract_polygons.
    
    **ports: list**
    
    Not implemented
    
    **box: list**
    
    Box parameters / list of layers as discussed in extract_box.
    
- **Examples**
    
    ```python
    # Unpack polygons, and directly repack them doing nothing
    new_dict = pyson.repack_geo(project.son_dict, polygons=pyson.unpack_polygons(project.son_dict))
    ```
    

### pyson.param_exists

```python
param_exists(unpacked, block, param)
```

Check if a certain parameter exists in a block of the Sonnet dict (see Sonnet dict documentation). Returns a boolean.

- **Arguments**
    
    **unpacked: dict**
    
    Dictionary corresponding to a Sonnet project
    
    **block: string**
    
    Block of the Sonnet dict to check
    
    **parameter: string**
    
    Parameter to find
    
- **Examples**
    
    ```python
    # Check if a resolution block exists for frequency sweeps
    check = param_exists(project.son_dict, "CONTROL", "RES_ABS")
    ```
    

### pyson.replace_param

```python
param_exists(unpacked, block, param, value)
```

Set a parameter in the Sonnet dict (see Sonnet dict documentation). Returns nothing.

- **Arguments**
    
    **unpacked: dict**
    
    Dictionary corresponding to a Sonnet project
    
    **block: string**
    
    Block of the Sonnet dict to check
    
    **parameter: string**
    
    Parameter to find
    
    **value: string, int, Bool or Array-like**
    
    Value to set parameter
    
- **Examples**
    
    ```python
    # Set the resolution for frequency sweeps
    replace_param(project.son_dict, "CONTROL", "RES_ABS", 1.0e-4)
    ```
    

## TODO

### Known Bugs

- Support for vias and dielectric bricks is not implemented, and there will likely be significant issues opening files containing them.
- Different default dimensions between Python backend and Matlab backend (length in terms of um for Python instead of mil). For Python this is intentional, however, consistent behavior is desirable.

### Short-term Features

- Important: need to handle dimensions better, allow changing dimensions, and make it more clear what dimensions are being used.
- Via support, dielectric brick support
- Support more frequency sweep options (not just ABS)
- Better handling of adding/removing ports
- Finish crop function (unfinished attempt can be seen in code)
- Linux support (should be as easy as changing directory paths and removing .exe extensions)

### Long-term features

- Better understand polygon / box formats and move towards a dict structure instead of the messy arrays
- Better understand GEO block as a whole and parameterize it.
- Overall move towards a less hacky system of modifying the larger sonnet dict structure.
- Support several Sonnet versions
