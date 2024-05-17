import pymeshlab
import os
import numpy as np
import math
from pathlib import Path

dire = "E:\\Johannes\\Curvature_Paper\\Group3_Redo" #Change as required (folder containing the distal femur .stls)

done = 0;
#Walk through all distal femurs)
for dirpath, dirnames, filenames in os.walk(dire):
    for filename in [f for f in filenames if f.endswith(".stl") ]:
            filepath = os.path.join(dirpath,Path(filename).stem + "_CurvatureMaps")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            orignalFile = os.path.join(dirpath, filename)
            stem = Path(orignalFile).stem
            ridgeFile = os.path.join(filepath, stem + '_Ridges.ply')
            transitionFile = os.path.join(filepath, stem + '_Transition.ply')
            projectFile = os.path.join(filepath, stem + '_MeshProject.mlp')
            #load distal femur into meshlab
            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(orignalFile)
            m1 = ms.current_mesh()
            # reduce size if needed and repair
            if m1.vertex_number() > 50000:
                ms.meshing_decimation_quadric_edge_collapse(targetfacenum=50000, preservenormal=True, autoclean=True)
            ms.meshing_repair_non_manifold_edges()
            ms.meshing_remove_connected_component_by_face_number(mincomponentsize = 2500)
            #create copy for transition map (minimal curvature)
            ms.apply_filter('generate_copy_of_current_mesh')
            ms.set_mesh_name(newname='Transistion')
            m = ms.current_mesh()
            box = m.bounding_box()
            lengthScale = box.diagonal()
            p = pymeshlab.Percentage(13 / lengthScale * 100)
            #calculate minimal curvature (note: meshlab switched minimal and maximal curvatuer)
            ms.compute_curvature_principal_directions_per_vertex(autoclean=True,
                                                                 method='Scale Dependent Quadric Fitting',
                                                                 curvcolormethod='Max Curvature', scale=p)
            m1 = ms.current_mesh()
            minCurvValue = m1.vertex_scalar_array();
            #Colorize minimal curvature values
            ms.compute_color_from_scalar_using_transfer_function_per_vertex(minqualityval=-0.12, maxqualityval=0.0,
                                                                            midhandlepos=70, tfslist=0,
                                                                            csvfilename='E:\MeshlabScript\MeshlabTransitionPoint.qmap')
            #Save file and create copy for maximal curvature map (ridges)
            ms.save_current_mesh(transitionFile)
            ms.apply_filter('generate_copy_of_current_mesh')
            ms.set_mesh_name(newname='Ridges')
            m2 = ms.current_mesh();
            #Calculate maximal curvature map for small scale structures
            p = pymeshlab.Percentage(5 / lengthScale * 100)
            ms.compute_curvature_principal_directions_per_vertex(autoclean=True,
                                                                 method='Scale Dependent Quadric Fitting',
                                                                 curvcolormethod='Min Curvature', scale=p)
            # Colorize maximal curvature values and save
            ms.compute_color_from_scalar_using_transfer_function_per_vertex(minqualityval=0.05, maxqualityval=0.3,
                                                                            midhandlepos=60, tfslist=0,
                                                                            csvfilename='E:\MeshlabScript\MeshlabRidges.qmap')
            ms.save_current_mesh(ridgeFile)

print('all done')
input("Press Enter to continue...")
