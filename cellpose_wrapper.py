from cellpose import models
import torch


def collect_masks(imgs, ratio=1, diameter=None):
    cell_model = models.Cellpose(model_type='nuclei', gpu=True)

    #dia_model = models.SizeModel(models.CellposeModel())
    # list of files
    # PUT PATH TO YOUR FILES HERE!
    #imgs = [image, ]
    nimg = len(imgs)
    # define CHANNELS to run segementation on
    # grayscale=0, R=1, G=2, B=3
    # channels = [cytoplasm, nucleus]
    # if NUCLEUS channel does not exist, set the second channel to 0
    channels = []
    for i in range(nimg):
        channels.append([0, 0])

    # IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
    # channels = [0,0] # IF YOU HAVE GRAYSCALE
    # channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
    # channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

    # if diameter is set to None, the size of the cells is estimated on a per image basis
    # you can set the average cell `diameter` in pixels yourself (recommended)
    # diameter can be a list or a single number for all images
    imgs_list = [i for i in imgs[0]]
    try:
        #todo: check for lamb and adjust cell diameter acordingly

        masks, flows, styles, diams = cell_model.eval(imgs, diameter=diameter, batch_size=1, channels=channels,
                                                 do_3D=True, normalize=True, flow_threshold=0.4, cellprob_threshold=0.0, anisotropy=ratio,
                                                     stitch_threshold=0.4)  # todo: masks is what you need. post=diameter20 pre=diameter10
        print(diams)
    except:
       masks=None
       print("cellpose failed")

    del cell_model
    torch.cuda.empty_cache()
    return masks