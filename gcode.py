###############################################################################
# PYTHON CODE TO GENERATE GCODE FILE TO EXAMPLE IN FIGURE 25 OF THE ARTICLE 
# "Optimisation of variable material orientations through design subregions 
# for additive manufacturing of fibre composites" by P.A.C. de Freitas, T.A. 
# Dutra, and R.T.L. Ferreira. 
# 
# 2026 All rights reserved to P.A.C. de Freitas.
###############################################################################

import numpy as np

###############################################################################
###############################################################################

def print_plate(
        curves,
        position_of_curves
    ):

    """
    Converts optimized toolpath curves into a physical G-code file for 3D printing.


    Parameters
    ----------
    
    * curves : list of lists
    
        Nested list where each element is [x_coordinates, y_coordinates] representing a continuous toolpath segment.
    
    * position_of_curves : list of lists
    
        Metadata mapping polygons to curve indices: [polygon_id, start_idx, end_idx].

    
    Returns
    -------

    * Outputs a file named 'layer_curves.gcode' in the local directory.

    """


    # Printing parameters

    h = 0.5             # fused filament height [mm]
    
    b = 0.8             # fused filament diameter [mm]
    
    D = 1.75            # original filament diameter [mm]
    
    T0 = 190            # nozzle temperature [Celsius] 
    
    TB = 90             # bed temperature [Celsius]
    
    F = 600             # translating speed [mm/min]

    xoff = 30           # x offset from bed edges [mm]

    yoff = 50           # y offset from bed edges [mm]

    Eretract = -b       # retract filament [mm]

    Fretract = 15000    # retraction translating speed [mm/min]
        
    
    # Opening the outputfile
    
    file = open('layer_curves.gcode','w')


    # Set modes, home, and pre-heat

    file.write('M83                      ; use relative distances for extrusion \n')

    file.write('G28                      ; home all axes (X,Y,Z) \n')

    file.write('G21                      ; set units to millimeters \n')

    file.write('G1 X30 Y185 Z5 F3600     ; put nozzle in this position before heating process \n')
    
    file.write('G90                      ; absolute position for XYZ axes \n')

    file.write('M140 S%d                 ; start heating the bed to %d degrees Celsius \n' %(TB,TB))

    file.write('M190 S%d                 ; wait until the bed reaches %d degrees before continuing \n' %(TB,TB))

    file.write('M104 S%d T0              ; start heating T0 to %d degrees Celsius \n' %(T0,T0))

    file.write('M109 S%d T0              ; wait until T0 to reach %d degrees before continuing  \n\n' %(T0,T0))
 

    # Clean the nozzle before starting the print

    file.write('G1 X25 Y180 Z0.5 E0      ; clear material before printing\n')
    
    file.write('G1 X25 Y40 Z0.5 E12 F360 ; clear material beforre printing \n')

    file.write('G1 X90 Y40 Z0.5 E6 F360  ; clear material before printing \n\n') 
    
    file.write('G1 X90 Y50 Z0.5 E2 F360  ; clear material before printing \n\n') 

    
    # Build a table of start/end points for each polygonal region

    data_table = []

    for i in range(len(position_of_curves)):

        x_begin = curves[position_of_curves[i][1]][0][0]

        y_begin = curves[position_of_curves[i][1]][1][0]

        x_end = curves[position_of_curves[i][2]][0][-1]
        
        y_end = curves[position_of_curves[i][2]][1][-1]

        data_table.append([i,x_begin,y_begin,x_end,y_end])

    
    # Stores the optimized order of regions

    regioes_impressas = []

    while(len(regioes_impressas)<(len(position_of_curves))):

        if len(regioes_impressas) == 0:

            regioes_impressas.append(0)

            x_final = data_table[0][3]

            y_final = data_table[0][4]

        else:

            minimo_dis = 10*6

            minimo_pos = 0

            for i in range(len(data_table)):

                if i not in regioes_impressas:

                    x_inicial = data_table[i][1]

                    y_inicial = data_table[i][2]

                    dist = np.sqrt((x_inicial-x_final)**2+(y_inicial-y_final)**2)

                    if dist <= minimo_dis:

                        minimo_dis = dist

                        minimo_pos = i

            regioes_impressas.append(minimo_pos)

            x_final = data_table[minimo_pos][3]

            y_final = data_table[minimo_pos][4]

    
    ## Printing the curves

    for i in regioes_impressas:

        numero_de_curvas = position_of_curves[i][2] - position_of_curves[i][1] + 1

        for j in range(numero_de_curvas):

            x = curves[j+position_of_curves[i][1]][0]

            y = curves[j+position_of_curves[i][1]][1]

            if len(x)>0:

                x0 = 1000*x[0] + xoff
                    
                y0 = 1000*y[0] + yoff
                
                z0 = h

                file.write('G1 X%f Y%f Z%f E%f F%f \n'%(x0,y0,z0+0.5*h,0,Fretract))

                file.write('G1 X%f Y%f Z%f E%f F%f \n'%(x0,y0,z0,-Eretract,F))

                for k in range(len(x)-1):

                    x1 = 1000*x[k] + xoff
                    
                    y1 = 1000*y[k] + yoff
                    
                    z1 = h
                
                    x2 = 1000*x[k+1] + xoff
                
                    y2 = 1000*y[k+1] + yoff
                
                    z2 = h
                
                    l = np.sqrt((x2-x1)**2+(y2-y1)**2)
                
                    E = (h+4*(b-h)/np.pi)*l*h/D**2
                
                    file.write('G1 X%f Y%f Z%F E%f F%f \n'%(x2,y2,z2,E,F))

                x2 = 1000*x[-1] + xoff
                
                y2 = 1000*y[-1] + yoff
                
                z2 = h
                
                file.write('G1 X%f Y%f Z%f E%f F%f \n'%(x2,y2,z2+0.5*h,Eretract,F))
        
        
        # Move Z up slightly after completing a region

        file.write('G1 Z%f E%f F%f \n'%(2*h,0,F)) 
    
    
    # Moving nozzle to a predefined positon

    file.write('\nG1 X25 Y190 Z100 E-2 F3600  ; put nozzle in this position after printing process \n')


    # Closing the file where gcode has been written

    file.close()

    return
    
###############################################################################
###############################################################################