from copy import copy
from matplotlib import pyplot as plt
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import MultiPolygon as ShapelyMultiPolygon
from datetime import datetime
from random import randint, seed
import numpy as np
import skrf as rf
import subprocess
import shutil
import os

# See if MATLAB Engine is installed
ml_import = True
try:
    import matlab.engine
except ImportError:
    ml_import = False
    pass

pyson_version = 0.1

class sonnetFile:
    # Constructors / Destructors
    def __init__(self,  file_name, temp, sonnet_path="", eng=None):
        sp = "C:\\Program Files (x86)\\Sonnet Software\\16.52\\bin\\"
        self.eng = eng
        self.file_name = file_name
        self.temp = temp
        self.ml_backend = eng is not None
        self.son_dict = unpack_son(file_name) 
        if os.path.isdir(sp):
            self.sonnet_path = sp
        elif sp != "":
            self.sonnet_path = sonnet_path
        else:
            raise Exception("Sonnet 16.52 path not found, please specify custom path. Versions != 16.52 are untested.")

    def __del__(self):
        if self.temp:
            if self.ml_backend:
                self.clean_output_files()
                self.clean_project()

            # If file_name exists, delete it
            if os.path.isfile(self.file_name):
                os.remove(self.file_name)

            # If the path sondata/file_name exists, delete it
            extradir = "sondata\\"+os.path.splitext(self.file_name)[0]
            if os.path.isdir(extradir):
                if self.ml_backend:
                    os.rmdir(extradir)
                else:
                    shutil.rmtree(extradir)

        if self.ml_backend:
            self.eng.quit()

    # Sonnetlab Functions
    def save(self, file_name=""):
        file_name = file_name if file_name != "" else self.file_name
        if self.ml_backend:
            if file_name == "":
                self.eng.eval(f"Project.save();", nargout=0)
            else:
                self.eng.eval(f"Project.saveAs(\"{file_name}\");", nargout=0)

            # Unpack the sonnet file and remove duplicate VALVAR lines (SonnetLab Bug)
            unpacked = unpack_son(self.file_name)
            out_geo = ""
            valvar_lines = []
            geo_split = unpacked["GEO"].split("\n")
            for geo_line in range(len(geo_split)):
                if "VALVAR" in geo_split[geo_line]:
                    if geo_split[geo_line] in valvar_lines:
                        continue
                    else:
                        valvar_lines.append(geo_split[geo_line])
                out_geo += geo_split[geo_line] + "\n"
            unpacked["GEO"] = out_geo
            repack_son(file_name, unpacked)
            self.file_name = file_name
        else:
            repack_son(file_name, self.son_dict)
            self.file_name = file_name

    def open_in_sonnet(self):
        self.save()
        subprocess.call(f"{self.sonnet_path}xgeom.exe {self.file_name}")
        self.reload()

    def add_metal_polygon(self, metalization_level, xcoords, ycoords, metal_type="", tech_layer="", inherit=True, header=[]):
        if self.ml_backend:
            # Get list of polygons before adding new one if tech layer needs to be changed
            polygons = None
            if tech_layer != "":
                polygons = extract_polygons(self.unpack())

            # Convert a list of coordinates of the form [a,b,c,d] to a string of the form [a;b;c;d]
            xc = str(xcoords).replace(",", ";")
            yc = str(self.fix_y(ycoords)).replace(",", ";")
            if(metal_type == ""):
                self.eng.eval(f"polyId = Project.addMetalPolygonEasy({metalization_level}, {xc}, {yc}).DebugId;", nargout=0)
            elif(type(metal_type) == int):
                self.eng.eval(f"polyId = Project.addMetalPolygonEasy({metalization_level}, {xc}, {yc}, {metal_type}).DebugId;", nargout=0)
            else:
                self.eng.eval(f"polyId = Project.addMetalPolygonEasy({metalization_level}, {xc}, {yc}, \"{metal_type}\").DebugId;", nargout=0)
            self.save()


            # If tech layer is not "" then change the tech layer
            if(tech_layer != ""):

                # Get list of polygons after adding new one
                polygons_new = extract_polygons(self.unpack())

                # Find the new polygon
                new_poly = polygons_new.index([p for p in polygons_new if p not in polygons][0])

                # Change tech layer
                polygons_new[new_poly][0][-2] = tech_layer
                polygons_new[new_poly][0][-1] = "INH" if inherit else "NOH"

                # Repack polygons and repack sonnet file
                repack_son(self.file_name, repack_geo(self.unpack(), polygons=polygons_new))
                self.reload()

            return int(self.eng.workspace["polyId"])
        else:
            polys = extract_polygons(self.son_dict)
            poly_ids = [int(p[0][4]) for p in polys]
            new_id = 1
            while new_id in poly_ids:
                new_id = randint(2, len(poly_ids)*10)
            inh = "" if tech_layer == "" else ("INH" if inherit else "NOH")

            new_header = []
            if header != []:
                new_header = header
                if header[2] == -1:
                    new_header[2] = new_id
            else:
                new_header = [metalization_level, len(xcoords), -1 if metal_type == "" else metal_type, 'N', new_id, 1, 1, 100, 100, 0, 0, 0, 'Y', tech_layer, inh]

            new_poly = [new_header, list(zip(xcoords, self.fix_y(ycoords)))]

            # Handle when the user doesn't close the polygon
            if new_poly[1][0] != new_poly[1][-1]:
                new_poly[1].append(new_poly[1][0])
                new_poly[0][1] = new_poly[0][1] + 1
            polys.append(new_poly)
            self.son_dict = repack_geo(self.son_dict, polygons=polys)
            return new_id

    def add_subcircuit(self, project, x, y):
        if self.ml_backend:
            raise Exception("This function is not supported in the Matlab backend.")
        else:
            id_maps = []
            polys = extract_polygons(project.son_dict)
            for i in range(len(polys)):
                old_id = polys[i][0][2]
                polys[i][0][2] = -1
                for j in range(len(polys[i][1])):
                    polys[i][1][j][0] = polys[i][1][j][0] + x
                    polys[i][1][j][1] = polys[i][1][j][1] + y
                new_id = self.add_metal_polygon(0, *zip(*polys[i][1]), header=polys[i][0])
                id_maps.append((old_id, new_id))

    def set_valvar(self, name, value=None, vartype=None, Descr=None):
        geo = self.son_dict["GEO"].split("\n")
        for i in range(len(geo)):
            if geo[i].startswith(f"VALVAR {name}"):
                vv = geo[i].split(" ")
                vv[2] = str(vartype) if vartype != None else vv[2]
                vv[3] = str(value) if value != None else vv[3]
                vv[4] = str(Descr) if Descr != None else vv[4]
                geo[i] = " ".join(vv)
                break
        self.son_dict["GEO"] = "\n".join(geo)

    def delete_polygon(self, index):
        if self.ml_backend:
            raise Exception("This function is not supported in the Matlab backend.")
        else:
            polys = extract_polygons(self.son_dict)
            polys.pop(index)
            self.son_dict = repack_geo(self.son_dict, polygons=polys)

    def add_via_polygon(self, metalization_level, to_level, xcoords, ycoords):
        if not self.ml_backend:
            raise Exception("This function is not supported in the Python backend.")
        xc = str(xcoords).replace(",", ";")
        yc = str(self.fix_y(ycoords)).replace(",", ";")
        self.eng.eval(f"Project.addViaPolygonEasy({metalization_level}, {to_level}, {xc}, {yc});", nargout=0)

    def change_dielectric_layer_thickness(self, layer, thickness):
        if self.ml_backend:
            self.eng.eval(f"Project.changeDielectricLayerThickness({layer+1}, {thickness});", nargout=0)
        else:
            box = extract_box(self.son_dict)
            box[1][layer][0] = thickness
            self.son_dict = repack_geo(self.son_dict, box=box)

    def add_std_port(self, polygon, vertex, port_number=None, res=50, react=0, ind=0, cap=0):
        if self.ml_backend:
            self.eng.eval(f"Project.addPortToPolygon({polygon_number}, {port_number});", nargout=0)
        else:
            v = [p for p in extract_polygons(self.son_dict) if int(p[0][4]) == polygon][0][1]
            x = (v[vertex][0] + v[vertex+1][0])/2
            y = (v[vertex][1] + v[vertex+1][1])/2

            port_nums = list(map(lambda x: x["port_number"], extract_ports(self.son_dict)))
            pn = 1 if len(port_nums) == 0 else max(port_nums)+1
            pn = port_number if port_number is not None else pn
            port_lines = []
            port_lines.append("POR1 STD")
            port_lines.append(f"POLY {polygon} 1")
            port_lines.append(f"{vertex}")
            port_lines.append(f"{pn} {res} {react} {ind} {cap} {x} {y}")

            geo = [y for y in (x for x in self.son_dict["GEO"].splitlines()) if y]
            port_indices = extract_ports(self.son_dict, indices=True)
            print(port_indices)
            final_port = 0
            if len(port_indices) == 0:
                print([i for i in range(len(geo)) if "NUM" in geo[i]])
                polygons_start = [i for i in range(len(geo)) if "NUM" in geo[i]][0]
                final_port = polygons_start-1
            else:
                final_port = max(port_indices)
            print(final_port)
            geo = geo[:final_port+1] + port_lines + geo[final_port+1:]
            self.son_dict["GEO"] = "\n".join(geo)

    def change_box_size(self, x, y):
        if self.ml_backend:
            self.eng.eval(f"Project.changeBoxSize({x}, {y});", nargout=0)
        else:
            box = extract_box(self.son_dict)
            box[0][1] = x
            box[0][2] = y
            self.son_dict = repack_geo(self.son_dict, box=box)

    def change_cell_size(self, x, y):
        if self.ml_backend:
            self.eng.eval(f"Project.changeCellSizeUsingNumberOfCellsXY({x}, {y});", nargout=0)
        else:
            box = extract_box(self.son_dict)
            lenx, leny = box[0][1], box[0][2]
            box[0][3] = 2*int(lenx / x)
            box[0][4] = 2*int(leny / y)
            self.son_dict = repack_geo(self.son_dict, box=box)

    def cell_size(self):
        if self.ml_backend:
            raise Exception("This function is not supported in the Matlab backend.")
        else:
            box = extract_box(self.son_dict)
            return box[0][1]/(box[0][3]/2), box[0][2]/(box[0][4]/2)

    def box_size(self):
        if self.ml_backend:
            x_size = self.eng.eval("Project.xBoxSize();")
            y_size = self.eng.eval("Project.yBoxSize();")
        else:
            x_size = extract_box(self.son_dict)[0][1]
            y_size = extract_box(self.son_dict)[0][2]
        return x_size, y_size

    def fix_y(self, yc):
        _, y_size = self.box_size()
        yco = [y_size - y for y in yc]
        return yco

    def add_mdif_output(self, file_output=""):
        if self.ml_backend:
            # Save any metal changes beforehand
            self.save()

            # Unpack the file and insert "aoeu" into the block FILEOUT
            unpacked = self.unpack()

            fout = ""
            if file_output == "":
                fout = "$BASENAME.mdf"
            else:
                fout = file_output

            unpacked["FILEOUT"].append(f"MDIF D Y {fout} IC 8 S RI R 50.00000")

            # Repack the file and load changes into matlab
            repack_son(self.file_name, unpacked)
            self.reload()
        else:
            up = copy(self.son_dict)
            fout = ""
            if file_output == "":
                fout = "$BASENAME.mdf"
            else:
                fout = file_output
            self.son_dict["FILEOUT"].append(f"MDIF D Y {fout} IC 8 S RI R 50.00000")

    def rm_mdif_output(self, file_output=""):
        if self.ml_backend:
            # Save any metal changes beforehand
            self.save()

            # Unpack the file and insert "aoeu" into the block FILEOUT
            unpacked = self.unpack()

            fout = ""
            if file_output == "":
                fout = "$BASENAME.mdf"
            else:
                fout = file_output

            unpacked["FILEOUT"] = [line for line in unpacked["FILEOUT"] if fout not in line]

            # Repack the file and load changes into matlab
            repack_son(self.file_name, unpacked)
            self.reload()
        else:
            fout = ""
            if file_output == "":
                fout = "$BASENAME.mdf"
            else:
                fout = file_output

            self.son_dict["FILEOUT"] = [line for line in self.son_dict["FILEOUT"] if fout not in line]


    def simulate_network(self, file_output=""):
        # If no file output is specified, use temp-0.mdf, unless temp-0.mdf exists in which case use temp-1.mdf
        i = 0
        fo = ""
        if file_output == "":
            fo = "temp-"+str(i)+".mdf"
            while os.path.isfile(fo):
                i = i + 1
                fo = "temp-"+str(i)+".mdf"
        with open(fo, 'w') as f:
            f.write('temp')

        # Add the mdif output to the file
        self.add_mdif_output(fo)
        self.save()

        # Call em to run the simulation
        self.sonnet_call_em()

        # Remove the mdif output from the file
        self.rm_mdif_output(fo)
        self.save()
       
        good_output = True

        with open(fo, 'r') as f:
            if f.readline() == 'temp':
                raise Warning('Simulation failed.')

        out = None
        if good_output:
            # Load the results into skrf
            out = rf.NetworkSet.from_mdif(fo)

        # Delete the temp file
        os.remove(fo)

        return out

    def sonnet_call_em(self, file_name="", options=""):
        subprocess.call(f"{self.sonnet_path}em.exe {self.file_name}{'' if options == '' else ' '}{options}")

    def targ_abs(self, resolution):
        if self.ml_backend:
            # Unpack the project
            unpacked = self.unpack()

            # Replace the param TARG_ABS in the block CONTROL with the new resolution
            self.repack(replace_param(unpacked, "CONTROL", "TARG_ABS", resolution))
        else:
            self.son_dict = replace_param(self.son_dict, "CONTROL", "TARG_ABS", resolution)

    def res_abs(self, enable, resolution):
        if self.ml_backend:
            # Unpack the project
            unpacked = self.unpack()

            # Replace the param RES_ABS in the block CONTROL with the new resolution
            self.repack(replace_param(unpacked, "CONTROL", "RES_ABS", [enable, resolution]))
        else:
            self.son_dict = replace_param(self.son_dict, "CONTROL", "RES_ABS", [enable, resolution])

    def add_abs_frequency_sweep(self, start, stop):
        if self.ml_backend:
            # Unpack the project
            unpacked = self.unpack()

            # Replace the param ABS in the block FREQ with the new sweep
            self.repack(replace_param(unpacked, "FREQ", "ABS", [start, stop]))

            # Check if the project has a param TARG_ABS in the block CONTROL and if not add it with a default value 300
            if "TARG_ABS" not in unpacked["CONTROL"]:
                self.targ_abs(300)
        else:
            # Replace the param ABS in the block FREQ with the new sweep
            self.son_dict = replace_param(self.son_dict, "FREQ", "ABS", [start, stop])

            # Check if the project has a param TARG_ABS in the block CONTROL and if not add it with a default value 300
            if "TARG_ABS" not in self.son_dict["CONTROL"]:
                self.targ_abs(300)


    def set_speed(self, speed):
        # Unpacke the project
        unpacked = self.unpack()

        # Replace the param SPEED in the bloc CONTROL with the new speed
        self.repack(replace_param(unpacked, "CONTROL", "SPEED", speed))

    def crop(self, x1, y1, x2, y2):
        if self.ml_backend:
            raise NotImplementedError("Cropping is not implemented for the matlab backend")
        else:
            fix_ids = []
            up = copy(self.son_dict)
            polygons = extract_polygons(up)
            poly_out = []
            rect = ShapelyPolygon([[x1,y1],[x1,y2],[x2,y2],[x2,y1],[x1,y1]])
            for p in polygons:
                a = ShapelyPolygon(p[1]).intersection(rect)

                if a.is_empty:
                    continue
                if isinstance(a,ShapelyMultiPolygon):
                    multi_id = False
                    for p1 in list(a.geoms):
                        x = p1.exterior.coords.xy[0]
                        y = p1.exterior.coords.xy[1]
                        poly_out.append([p[0],list(map(lambda inp : [inp[0]-x1, inp[1]-y1], zip(x,y)))])
                        if multi_id:
                            fix_ids.append(len(poly_out)-1)
                        else:
                            multi_id = True
                    continue
                
                x = a.exterior.coords.xy[0]
                y = a.exterior.coords.xy[1]
                poly_out.append([p[0],list(map(lambda inp : [inp[0]-x1, inp[1]-y1], zip(x,y)))])
            for i in fix_ids:
                poly_ids = [int(p[0][4]) for p in poly_out]
                new_id = 1
                while new_id in poly_ids:
                    new_id = randint(2, len(poly_ids)*10)
                poly_out[i][0][0] = new_id
            # Repack polygons
            self.son_dict = repack_geo(self.son_dict, polygons=poly_out)

            # Change box boundaries
            cell_x, cell_y = self.cell_size()
            box_x, box_y = self.box_size()
            self.change_box_size(box_x, box_y)
            self.change_cell_size(cell_x, cell_y)

    def draw(self, figsize=(5,5), layer=None, metal_args=dict(color="#209fb5", edgecolor="#4c4f69", hatch="///"), 
             metal_argf = None, ports=True, 
             port_box=dict(boxstyle="square", fc="#eff1f5", ec="#4c4f69", alpha=1), port_font_size=8):

        draw_layer = layer
        up = self.unpack() if self.ml_backend else self.son_dict
        if layer is None:
            if len([a[0][0] for a in extract_polygons(up)]) > 0:
                ids =  [int(a[0][0]) for a in extract_polygons(up)]
                draw_layer = max(ids)
            else:
                return ptl.figure(figsize=figsize)
        # Get box size to handle coordinate shifts
        _,y = self.box_size()
        fig = plt.figure(figsize=figsize)
        ax = plt.axes()
        polys0 = [a[1] for a in extract_polygons(up) if int(a[0][0]) == draw_layer]
        poly_ids = [int(a[0][4]) for a in extract_polygons(up) if int(a[0][0]) == draw_layer]
        poly_data = [a[0] for a in extract_polygons(up) if int(a[0][0]) == draw_layer]
        polygons = [[[v[0], y-v[1]] for v in p] for p in polys0]

        ports = []
        if len(extract_ports(up)) > 0:
            ports = [[a["port_number"],a["x"],y-a["y"]] for a in extract_ports(up) if a["poly"] in poly_ids]

        for pind in range(len(polygons)):
            if metal_argf is not None:
                plt.fill(*zip(*polygons[pind]), **metal_argf(poly_data[pind]))
            else:
                plt.fill(*zip(*polygons[pind]), **metal_args)

        for port in ports:
            plt.text(port[1], port[2], port[0], bbox=port_box, clip_on=True, fontsize=port_font_size)

        return fig, ax

    def reload(self):
        if self.ml_backend:
            # Clear project variable
            self.eng.eval("clear Project;", nargout=0)

            # Re-open the project
            self.eng.eval(f"Project = SonnetProject(\"{self.file_name}\");", nargout=0) 
        else:
            self.son_dict = self.unpack()

    def repack(self, unpacked):
        repack_son(self.file_name, unpacked)
        self.reload()

    def clean_project(self):
        if self.ml_backend:
            self.eng.eval("Project.cleanProject();", nargout=0)

    def clean_output_files(self):
        if self.ml_backend:
            self.eng.eval("Project.cleanOutputFiles();", nargout=0)

    def unpack(self):
        self.save()
        return unpack_son(self.file_name)

def unpack_son(file_name):
    # Open file_name and start reading its lines
    with open(file_name, "r") as f:
        lines = f.readlines()
        # Create a dictionary to hold the different blocks
        unpacked = {}
        # Create a variable to hold the current block name
        current_block = ""
        # If header has not been reached yet leave this as true
        pre_header = True
        file_header = ""
        # Loop through the lines
        for line in lines:
            # If the line is equal to header set pre_header to false
            if line == "HEADER\n":
                pre_header = False
            # If the line is equal to END current_block\n set current_block to ""
            elif line == f"END {current_block}\n":
                current_block = ""
                continue

            # If pre_header is false and current_block="" then set current_block to the line
            if not pre_header and current_block == "":
                current_block = line.strip()
                if current_block != "GEO":
                    unpacked[current_block] = []
                else:
                    unpacked[current_block] = ""
            elif not pre_header and not current_block == "GEO":
                unpacked[current_block].append(line.strip())
            elif not pre_header:
                # Leave all geometry information untouched
                unpacked[current_block] += line
            else:
                file_header += line
    unpacked["file_header"] = file_header
    return unpacked

def extract_polygons(unpacked):
    # Extract the lines relevant to polygons
    g_lines = [y for y in (x.strip() for x in unpacked["GEO"].splitlines()) if y]
    polygons_start = [i for i in range(len(g_lines)) if "NUM" in g_lines[i]][0]
    polygon_lines = g_lines[polygons_start+1:]

    if(len(polygon_lines) == 0):
        return []

    pind = -1
    polygons = []
    subheader = False
    via = False
    for li in range(len(polygon_lines)):
        # If the line has more than 3 spaces or is equal to "VIA POLYGON" it is a new polygon
        split = polygon_lines[li].split()
        if len(split) > 3 and not via:
            polygons.append([split, []])
            pind += 1
            subheader = False
            via = False
        elif via:
            continue
        elif polygon_lines[li].strip() == "VIA POLYGON":
            via = True
        elif len(split) == 3:
            polygons[pind][0] = polygons[pind][0] + split[1:]
            subheader = True
        elif len(split) == 2:
            if not subheader:
                polygons[pind][0] = polygons[pind][0] + ["",""]
                subheader = True
            polygons[pind][1].append(list(map(float,split)))

    return polygons

def extract_box(unpacked):
    # From the GEO block get the line starting with BOX
    up = copy(unpacked)
    geo = unpacked["GEO"].splitlines()
    box_start = [y for y in range(len(geo)) if "BOX" in geo[y]][0]
    # Now make an array of all the lines following it with a tab
    box_end = 0
    for x in range(box_start+1, len(geo)):
        tabs_over_spaces = geo[x].replace("      ", "\t")
        if "\t" not in tabs_over_spaces:
            box_end = x
            break
    geo_box = geo[box_start][4:].split(' ')
    geo_box[0:6] = list(map(int, geo_box[0:6]))
    geo_box[6] = float(geo_box[6])
    layers = geo[box_start+1:box_end]
    for i in range(len(layers)):
        layers[i] = layers[i].strip()
        layers[i] = layers[i].split(' ')
        layers[i][0:6] = list(map(float, layers[i][0:6]))
        layers[i][6] = int(layers[i][6])
        layers[i][7] = layers[i][7].replace("\"", "")
        if len(layers) > 8:
            layers[i][8:] = list(map(float, layers[i][8:]))
    del up
    return[geo_box, layers]

def repack_geo(unpacked, polygons=None, ports=None, box=None):
    up = copy(unpacked)
    if polygons is not None:
        # Extract the lines relevant to polygons
        g_lines = [y for y in (x for x in unpacked["GEO"].splitlines()) if y]
        polygons_start = [i for i in range(len(g_lines)) if "NUM" in g_lines[i]][0]
       
        new_polygons = ["NUM "+str(len(polygons))]
        # Add the new polygons
        for polygon in polygons:
            new_polygons.append(' '.join(map(str,polygon[0][:-2])))
            if(polygon[0][-2] != ""):
                new_polygons.append("TLAYNAM "+ ' '.join(map(str, polygon[0][-2:])))
            for v in polygon[1]:
                new_polygons.append(' '.join(map(str,v)))
            new_polygons.append("END")
        new_lines = g_lines[:polygons_start] + new_polygons

        # Re-insert the new polygons
        up["GEO"] = "\n".join(new_lines) + "\n"

    if box is not None:
        # From the GEO block get the line starting with BOX
        geo = up["GEO"].splitlines()
        box_start = [y for y in range(len(geo)) if "BOX" in geo[y]][0]
        # Now make an array of all the lines following it with a tab
        box_end = 0
        for x in range(box_start+1, len(geo)):
            tabs_over_spaces = geo[x].replace("      ", "\t")
            if "\t" not in tabs_over_spaces:
                box_end = x
                break
        b = copy(box)
        b[0][0] = len(b[1])-1
        geo[box_start] = "BOX " + ' '.join(map(str, box[0]))
        for i in range(len(box[1])):
            geo[box_start+i+1] = '\t' + ' '.join(map(str, box[1][i][0:7])) + ' "' + box[1][i][7] + '"'
            if len(box[1][i]) > 8:
                geo[box_start+i+1] = geo[box_start+i+1] + ' ' + ' '.join(map(str, box[1][i][8:]))
        up["GEO"] = "\n".join(geo) + "\n"

    return up


def extract_ports(unpacked, indices=False):
    # Extract the lines relevant to ports
    g_lines = [y for y in (x.strip() for x in unpacked["GEO"].splitlines()) if y]

    if len([i for i in range(len(g_lines)) if "POR1" in g_lines[i]]) == 0:
        return []
    
    port_lines = [i for i in range(len(g_lines)) if "POR1" in g_lines[i]]
    port_indices_out = copy(port_lines)
    ports = []
    port_type = ""
    pind = -1
    for i in port_lines:
        pline = 0
        while True:
            if i+pline+1 > len(g_lines):
                break
            li = g_lines[i+pline]
            # If the line contains POR1 it is a new port
            split = li.split(" ")
            if "POR1" in split:
                if pline != 0:
                    break
                ports.append({})
                pind = pind + 1
                pline = 0

                port_type = split[1]
                ports[pind]["type"] = port_type

                if port_type == "CUP":
                    ports[pind]["calib_group"] = split[2]
            else:
                if pline == 1:
                    port_indices_out.append(i+pline)
                    ports[pind]["poly"] = int(split[1])
                    ports[pind]["points"] = int(split[2])
                elif pline == 2:
                    port_indices_out.append(i+pline)
                    ports[pind]["vertex"] = int(split[0])
                elif pline == 3:
                    port_indices_out.append(i+pline)
                    ports[pind]["port_number"] = int(split[0])
                    ports[pind]["resistance"] = float(split[1])
                    ports[pind]["reactance"] = float(split[2])
                    ports[pind]["inductance"] = float(split[3])
                    ports[pind]["capacitance"] = float(split[4])
                    ports[pind]["x"] = float(split[5])
                    ports[pind]["y"] = float(split[6])
                    if port_type == "AGND":
                        if len(split) < 9:
                            ports[pind]["agnd_calib_type"] = "NONE"
                        else: 
                            ports[pind]["agnd_calib_type"] = split[7]
                            ports[pind]["agnd_plane_length"] = split[8]
                            if len(split) == 10:
                                ports[pind]["agnd_calib_length"] = split[9]
                elif port_type == "STD":
                    break
                elif port_type == "CUP":
                    if split[0] == "CUPGRP":
                        port_indices_out.append(i+pline)
                        ports[pind]["cup_group"] = split[1]
                        ports[pind]["cup_group_type"] = split[2]
                    elif split[0] == "ID":
                        port_indices_out.append(i+pline)
                        ports[pind]["cup_id"] = int(split[1])
                    elif split[0] == "GRNDREF":
                        port_indices_out.append(i+pline)
                        ports[pind]["cup_grndref"] = split[1]
                    elif split[0] == "TWTYPE":
                        port_indices_out.append(i+pline)
                        ports[pind]["cup_twtype"] = split[1]
                    else:
                        break
            pline = pline + 1

    if indices:
        return port_indices_out
    return ports

def repack_ports(unpacked, ports):
    geo = unpacked["GEO"].splitlines()

def repack_son(file_name, unpacked):
    up = copy(unpacked)
    output_string = ""
    output_string += up.pop("file_header")
    for block in up:
        output_string += block + "\n"
        if block != "GEO":
            for line in unpacked[block]:
                output_string += line + "\n"
        else:
            output_string += unpacked[block]
        output_string += f"END {block}\n"

    with open(file_name, "w") as f:
        f.write(output_string)

def param_exists(unpacked, block, param):
    for line in unpacked[block]:
        if param in line:
            return True
    return False

def replace_param(unpacked, block, param, value):
    up = copy(unpacked)
    v = ""
    if isinstance(value, list):
        for i in value:
            if isinstance(i, bool):
                v += "Y " if i else "N "
            else:
                v += f"{i} "
        v = v[:-1]
    else:
        v = value

    for i in range(len(unpacked[block])):
        if param in unpacked[block][i]:
            up[block][i] = f"{param} {v}"
            return up
            
    up[block].append(f"{param} {v}")
    return up


def new_son(file_name, sonnet_path="", temp=False,  ml_backend=False, overwrite=None):
    if ml_backend:
        if not ml_import:
            raise Exception("Matlab engine not available")

        if overwrite is None:
            eng = matlab.engine.start_matlab()
            genpath = eng.genpath('sonnetlab')
            eng.addpath(genpath, nargout=0)
        else:
            eng = overwrite.eng
        eng.eval("Project = SonnetProject();", nargout=0)
        eng.eval(f"Project.saveAs(\"{file_name}\");", nargout=0)
        return sonnetFile(file_name, temp, sonnet_path=sonnet_path, eng=eng)
    else:
        new_file = {'HEADER': [f'DAT {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
          f'BUILT_BY_CREATED PySon v{pyson_version}',
          f'BUILT_BY_SAVED PySon v{pyson_version}',
          f'MDATE {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
          f'HDATE {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'],
         'DIM': ['ANG DEG',
          'CAP PF',
          'CON /OH',
          'FREQ GHZ',
          'IND NH',
          'LNG UM',
          'RES OH'],
         'FREQ': [],
         'CONTROL': ['ABS', 'OPTIONS -d', 'SPEED 0', 'CACHE_ABS 1', 'Q_ACC N'],
         'GEO': 'TMET Lossless 0 SUP 0 0 0 0\nBMET Lossless 0 SUP 0 0 0 0\nBOX 1 160 160 32 32 20 0\n      0 1 1 0 0 0 0 "Unnamed"\n      0 1 1 0 0 0 0 "Unnamed"\nNUM 0\n\n',
         'OPT': ['MAX 100'],
         'VARSWP': [],
         'FILEOUT': [],
         'SMDFILES': [],
         'file_header': 'FTYP SONPROJ 16.52 ! Sonnet Project File\nVER 16.52\n'}
        repack_son(file_name, new_file)
        return sonnetFile(file_name, temp=temp, sonnet_path=sonnet_path)


def open_son(file_name, sonnet_path="", temp=False,  ml_backend=False, overwrite=None):
    if ml_backend:
        if not ml_import:
            raise Exception("Matlab engine not available")
        if overwrite is None:
            eng = matlab.engine.start_matlab()
            genpath = eng.genpath('sonnetlab')
            eng.addpath(genpath, nargout=0)
        else:
            eng = overwrite.eng
        eng.eval(f"Project = SonnetProject(\"{file_name}\");", nargout=0)
        return sonnetFile(file_name, temp, eng=eng, sonnet_path=sonnet_path)
    else:
        return sonnetFile(file_name, temp, sonnet_path=sonnet_path)


def from_template(file_name, new_file="", temp=False, sonnet_path="", overwrite=None, ml_backend=False):
    file_out = ""
    if new_file == "":
        i = 1
        while True:
            file_out = file_name.split(".")[0] + f"-{i}.son"
            if not os.path.exists(file_out):
                break
            i = i+1
    else:
        file_out = new_file
    # Copy file_name to newFile
    with open(file_name, "r") as f:
        with open(file_out, "w") as f1:
            for line in f:
                f1.write(line)

    return open_son(file_out, temp=temp, sonnet_path=sonnet_path, overwrite=overwrite, ml_backend=ml_backend)
