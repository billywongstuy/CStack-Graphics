from display import *
from matrix import *
from draw import *
from copy import deepcopy

'''
push
    push a copy of the current top of the coordinate system (cs) stack onto the cs stack (a full copy, not just a reference to the current top... I'm looking at you python people)

pop
    removes the top of the cs stack (nothing needs to be done with this data)

translate/rotate/scale
    create a translation/rotation/scale matrix 
    multiply the current top of the cs stack by it

box/sphere/torus
    add a box/sphere/torus to a temporary polygon matrix
    multiply it by the current top of the cs stack
    draw it to the screen
    clear the polygon matrix 

line/curve/circle
    add a line to a temporary edge matrix
    multiply it by the current top
    draw it to the screen (note a line is not a solid, so avoid draw_polygons)

save
    save the screen with the provided file name

display
    show the image


'''

"""
Goes through the file named filename and performs all of the actions listed in that file.
The file follows the following format:
     Every command is a single character that takes up a line
     Any command that requires arguments must have those arguments in the second line.
     The commands are as follows:
         sphere: add a sphere to the edge matrix - 
	    takes 4 arguments (cx, cy, cz, r)
         torus: add a torus to the edge matrix - 
	    takes 5 arguments (cx, cy, cz, r1, r2)
         box: add a rectangular prism to the edge matrix - 
	    takes 6 arguments (x, y, z, width, height, depth)	    

	 circle: add a circle to the edge matrix - 
	    takes 3 arguments (cx, cy, r)
	 hermite: add a hermite curve to the edge matrix -
	    takes 8 arguments (x0, y0, x1, y1, rx0, ry0, rx1, ry1)
	 bezier: add a bezier curve to the edge matrix -
	    takes 8 arguments (x0, y0, x1, y1, x2, y2, x3, y3)
         line: add a line to the edge matrix - 
	    takes 6 arguments (x0, y0, z0, x1, y1, z1)
	 ident: set the transform matrix to the identity matrix - 
	 scale: create a scale matrix, 
	    then multiply the transform matrix by the scale matrix - 
	    takes 3 arguments (sx, sy, sz)
	 move: create a translation matrix, 
	    then multiply the transform matrix by the translation matrix - 
	    takes 3 arguments (tx, ty, tz)
	 rotate: create a rotation matrix,
	    then multiply the transform matrix by the rotation matrix -
	    takes 2 arguments (axis, theta) axis should be x, y or z
         clear: clear the edge matrix of points
	 apply: apply the current transformation matrix to the 
	    edge matrix
	 display: draw the lines of the edge matrix to the screen
	    display the screen
	 save: draw the lines of the edge matrix to the screen
	    save the screen to a file -
	    takes 1 argument (file name)
	 quit: end parsing

See the file script for an example of the file format
"""
ARG_COMMANDS = [ 'line', 'scale', 'move', 'rotate', 'save', 'circle', 'bezier', 'hermite', 'box', 'sphere', 'torus', 'color' ]

def parse_file( fname, edges, polygons, transform, screen, color ):
    
    f = open(fname)
    lines = f.readlines()

    m = new_matrix()
    ident(m)
    cstack = [m]
    
    #step = 0.01
    step = 0.1
    c = 0
    while c < len(lines):
        line = lines[c].strip()
        #print ':' + line + ':'

        if line in ARG_COMMANDS:            
            c+= 1
            args = lines[c].strip().split(' ')
            #print 'args\t' + str(args)

        if line == 'push':
            cstack.append(deepcopy(cstack[-1]))

        elif line == 'pop':
            if len(cstack) > 1:
                cstack.pop()
            
        elif line == 'sphere':
            #print 'SPHERE\t' + str(args)
            add_sphere(polygons,
                       float(args[0]), float(args[1]), float(args[2]),
                       float(args[3]), step, color)
            matrix_mult( cstack[-1], polygons )
            draw_polygons(polygons, screen, color)
            polygons[:] = []
            
        elif line == 'torus':
            #print 'TORUS\t' + str(args)
            add_torus(polygons,
                      float(args[0]), float(args[1]), float(args[2]),
                      float(args[3]), float(args[4]), step, color)
            matrix_mult( cstack[-1], polygons )
            draw_polygons(polygons, screen, color)
            polygons[:] = []
            
        elif line == 'box':
            #print 'BOX\t' + str(args)
            add_box(polygons,
                    float(args[0]), float(args[1]), float(args[2]),
                    float(args[3]), float(args[4]), float(args[5]), color)
            matrix_mult( cstack[-1], polygons )
            draw_polygons(polygons, screen, color)
            polygons[:] = []
            
        elif line == 'circle':
            #print 'CIRCLE\t' + str(args)
            add_circle(edges,
                       float(args[0]), float(args[1]), float(args[2]),
                       float(args[3]), step)
            matrix_mult( cstack[-1], edges )
            draw_lines(edges, screen, color)
            edges[:] = []
            
        elif line == 'hermite' or line == 'bezier':
            #print 'curve\t' + line + ": " + str(args)
            add_curve(edges,
                      float(args[0]), float(args[1]),
                      float(args[2]), float(args[3]),
                      float(args[4]), float(args[5]),
                      float(args[6]), float(args[7]),
                      step, line)                      
            matrix_mult( cstack[-1], edges )
            draw_lines(edges, screen, color)
            edges[:] = []
            
        elif line == 'line':            
            #print 'LINE\t' + str(args)
            add_edge( edges,
                      float(args[0]), float(args[1]), float(args[2]),
                      float(args[3]), float(args[4]), float(args[5]) )
            matrix_mult( cstack[-1], edges )
            draw_lines(edges, screen, color)
            edges[:] = []
            
        elif line == 'scale':
            #print 'SCALE\t' + str(args)
            t = make_scale(float(args[0]), float(args[1]), float(args[2]))
            #matrix_mult(t, cstack[-1])
            #NOW WE TRANSFORM BEFORE SHAPES
            matrix_mult(cstack[-1],t)
            cstack[-1] = t
            
        elif line == 'move':
            #print 'MOVE\t' + str(args)
            t = make_translate(float(args[0]), float(args[1]), float(args[2]))
            #matrix_mult(t, cstack[-1])
            matrix_mult(cstack[-1],t)
            cstack[-1] = t

        elif line == 'rotate':
            #print 'ROTATE\t' + str(args)
            theta = float(args[1]) * (math.pi / 180)
            
            if args[0] == 'x':
                t = make_rotX(theta)
            elif args[0] == 'y':
                t = make_rotY(theta)
            else:
                t = make_rotZ(theta)
            #matrix_mult(t, cstack[-1])
            matrix_mult(cstack[-1],t)
            cstack[-1] = t
            
        elif line == 'color':
            color[0] = args[0]
            color[1] = args[1]
            color[2] = args[2]

        elif line == 'clear':
            edges = []
            
        elif line == 'ident':
            #ident(transform)
            ident(cstack[pos])
            
        #elif line == 'apply':
        #    matrix_mult( transform, edges )

        elif line == 'display' or line == 'save':
            #clear_screen(screen)
            #draw_lines(edges, screen, color)
            #draw_polygons(edges, screen, color)

            if line == 'display':
                display(screen)
            else:
                save_extension(screen, args[0])
            
        c+= 1
