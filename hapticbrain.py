import nibabel as nib
import pygame
import numpy as np

img = nib.analyze.load('s150423123325DST131221107521416505-0002-00001-000001-00.hdr')

dat = img.get_data()
x,y,z = dat.shape[0]/2,dat.shape[1]/2,dat.shape[2]/2
maxd = np.amax(dat)



imgwidth = 300


pygame.init()


dims = ["x","y","z"]
surfaces = {}

def gray(im,maxval):
    """ Source: https://stackoverflow.com/questions/41168396/how-to-create-a-pygame-surface-from-a-numpy-array-of-float32  """
    im = 255 * (im / maxval) # float(im.max()))
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
    maxval = float(np.amax(dat))

    for j,dim in enumerate(dims):
        dimlen = dat.shape[j]
        
        for i in range(dimlen):
            if dim=="x": mat = dat[i,:,:]
            if dim=="y": mat = dat[:,i,:]
            if dim=="z": mat = dat[:,:,i]

            graymat = gray(mat,maxval)
            ###graymat = mat
            surf = pygame.surfarray.make_surface(graymat)
            surf = pygame.transform.flip(surf,False,True)
            
            surfaces[dim].append(surf)

    print("...done")
    return surfaces
    


Y_OFFSET = 20

def show_position(screen,position):
    """ Show position (x,y,z) """
    screen.fill((0,0,0))
    for j,dim in enumerate(dims):
        i = position[j]
        surf = surfaces[dim][i]
        screen.blit(surf,(j*imgwidth,Y_OFFSET))

    poslabel = "x=%i y=%i z=%i"%position
    fnt = pygame.font.SysFont("Courier",20)
    textsurf = fnt.render(poslabel,True,(255,255,255),(0,0,0)).convert(16)
    screen.blit(textsurf,(0,0))
    
    pygame.display.flip()





prepare_surfaces(dat)
    
screen = pygame.display.set_mode((3*imgwidth,480))
#img = pygame.image.load('pacman.jpg').convert()
screen.fill((0,0,0))
#screen.blit( img, (x,y) )
    
show_position(screen,(100,100,100))

done = False
while not done:
    events = pygame.event.get()
    for event in events:
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
            done = True
    
pygame.quit()
