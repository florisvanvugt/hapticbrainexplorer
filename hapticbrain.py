import nibabel as nib
import pygame
import numpy as np
import omega_cpp_py.robot as robot
import time

#img = nib.analyze.load('s150423123325DST131221107521416505-0002-00001-000001-00.hdr')
img = nib.load('icbm_avg_152_t1_tal_nlin_symmetric_VI.nii')

dat = img.get_data()
minval = float(np.amin(dat))
maxval = float(np.amax(dat))
# x,y,z = dat.shape[0]/2,dat.shape[1]/2,dat.shape[2]/2


# Controls the viscosity of the robot force field
VISCOSITY_MULTIPLIER = 100


def sigm(x):
    """ A sigmoid function used for transforming the viscosity values (so that
    we are more sensitive in the middle """
    return 1 - (1/(1+np.exp(-20*(x-.5))))



# Controls the size of the display panel
PANEL_WIDTH = 500

IMAGE_SCALE = 2.



pygame.init()


dims = ["x","y","z"]
surfaces = {}

def gray(im,minval,maxval):
    """ 
    Turn a matrix of numbers x into a matrix of tuples (x,x,x)
    so that it can be interpreted as a grayscale colour matrix.
    
    Source: https://stackoverflow.com/questions/41168396/how-to-create-a-pygame-surface-from-a-numpy-array-of-float32  
    """
    im = 255 * (im-minval) / (maxval-minval) # float(im.max()))
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret


def prepare_surfaces(dat):
    print("Preparing surfaces...")
    global surfaces
    surfaces = {"x":[],
                "y":[],
                "z":[]}

    for j,dim in enumerate(dims):
        dimlen = dat.shape[j]
        
        for i in range(dimlen):
            if dim=="x": mat = dat[i,:,:]
            if dim=="y": mat = dat[:,i,:]
            if dim=="z": mat = dat[:,:,i]

            graymat = gray(mat,minval,maxval)
            ###graymat = mat
            surf = pygame.surfarray.make_surface(graymat)
            surf = pygame.transform.flip(surf,False,True)
            surf = pygame.transform.smoothscale(surf,(int(surf.get_width()*IMAGE_SCALE),
                                                      int(surf.get_height()*IMAGE_SCALE)))
                                          
            surfaces[dim].append(surf)

    print("...done")
    return surfaces
    


Y_OFFSET = 35

def show_position(screen,position,label=""):
    """ Show position (x,y,z).
    Arguments
    screen : the pygame surface on which to draw
    label : the label corersponding
    """
    screen.fill((0,0,0))

    # Draw the panels corresponding to the slices
    for j,dim in enumerate(dims):
        i = position[j]
        surf = surfaces[dim][i]
        screen.blit(surf,(j*PANEL_WIDTH,Y_OFFSET))


    for j,dim in enumerate(dims):
        # Draw the crosshairs on each panel
        # these crosshairs should correspond to the
        # "other" coordinates
        i = position[j]
        surf = surfaces[dim][i]
        otherdims = [ w for w in range(3) if w!=j ]

        xpos = j*PANEL_WIDTH                 + int(IMAGE_SCALE*position[otherdims[0]])
        ypos = Y_OFFSET+surf.get_height()    - int(IMAGE_SCALE*position[otherdims[1]])
        
        pygame.draw.line(screen,(0,255,0),
                         (xpos,Y_OFFSET),
                         (xpos,Y_OFFSET+surf.get_height()),1)
        pygame.draw.line(screen,(0,255,0),
                         (j*PANEL_WIDTH,ypos),
                         ((j+1)*PANEL_WIDTH,ypos),1)

        

    (i,j,k)=position
    poslabel = "x=%i y=%i z=%i  %s  // press ESC to exit"%(i,j,k,label)
    fnt = pygame.font.SysFont("Courier",20)
    textsurf = fnt.render(poslabel,True,(255,255,255),(0,0,0)).convert(16)
    screen.blit(textsurf,(0,0))
    
    pygame.display.flip()




# The minimum and maximum expected values of the
# coordinates (x,y,z).
# This assumes that the robot is properly calibrated, i.e.
# brought to the extreme most point when perssing RESET.
minmax = [ [ .05,-.05], # note the sign flipping
           [-.06,.05],
           [-.05,.06] ]
#remap = [1,0,2] # how to remap the coordinates
remap = [[ 0,1,0 ], # transformation matrix for coordinates
         [ 1,0,0 ],
         [ 0,0,1 ]]




    
def robot_to_position(pos,dat):
    """ Given (x,y,z) robot coordinates,
    transform them into image coordinates """
    coord = []
    for j in range(3):
        mn,mx = minmax[j]
        i = pos[j]

        rel = (i-mn)/(mx-mn)
        if rel<0: rel=0.
        if rel>1: rel=1.

        coord.append(rel)

    # Remap the coordinates
    relpos = np.matmul(remap,coord)

    return tuple([ int(r*(n-1)) for (r,n) in zip(relpos,dat.shape) ])
    



prepare_surfaces(dat)
    
screen = pygame.display.set_mode((3*PANEL_WIDTH,480)) #,pygame.FULLSCREEN )
    
#show_position(screen,(100,100,100))




robot.launch()
robot.init()

robot.viscous_force(0) # start with viscous force field of zero viscosity (a fancy way of doing a null field)

done = False
while not done:
    events = pygame.event.get()
    for event in events:
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
            done = True

    x = robot.rshm('x')
    y = robot.rshm('y')
    z = robot.rshm('z')
    (i,j,k) = robot_to_position((x,y,z),dat)
    curval = dat[i,j,k]

    relval = (curval-minval)/(maxval-minval)
    visc = sigm(relval)*VISCOSITY_MULTIPLIER
    robot.wshm('viscosity',visc)
    
    show_position(screen,(i,j,k),"value = %f"%curval)
    print("x=%.3f y=%.3f z=%.3f visc=%.3f"%(x,y,z,visc))
    time.sleep(.05)


            
pygame.quit()

robot.unload()
