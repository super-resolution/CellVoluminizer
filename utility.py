import numpy as np
from scipy.spatial import ConvexHull
from cellpose_wrapper import collect_masks

def flood_fill_hull(image, px, pz):
    points = np.transpose(np.where(image)).astype(np.float32)
    points[:,0] *= pz
    points[:, 1:3] *= px
    hull = ConvexHull(points)
    # deln = scipy.spatial.Delaunay(points[hull.vertices])
    # idx = np.stack(np.indices(image.shape), axis = -1)
    # out_idx = np.nonzero(deln.find_simplex(idx) + 1)
    # out_img = np.zeros(image.shape)
    # out_img[out_idx] = 1
    return hull.volume

def compute_voxel_volume(image, px, pz):
    voxel = px**2*pz
    count = np.where(image)[0].shape[0]
    return voxel*count



def get_masks_and_volume(px, pz, volumes, array, coords, diameter=None):
    batch_size = 1
    masks = []
    V = []
    V2 = []
    print(len(coords))
    to_delete = []
    new_label = np.zeros_like(array).astype(np.uint16)


        #########
    for j in range(len(volumes)):
        if diameter:
            m = collect_masks(volumes[j*batch_size:(j+1)*batch_size], ratio=pz/px, diameter=diameter[j])
        else:
            m = collect_masks(volumes[j * batch_size:(j + 1) * batch_size], ratio=pz / px, diameter=6)
        if m:
            masks += m
        else:
            to_delete.append(j)
    to_delete.sort(reverse=True)
    for i in to_delete:# delete from bottom to top to not interfere with subsequent list indices
        del coords[i]

    for i in range(len(masks)):
        position = coords[i]
        current_mask = masks[i]
        for k in range(current_mask.max()+1):
            k +=1
            #create new array for each mask and compute volume
            x = np.zeros_like(current_mask)
            x[np.where(current_mask==k)] = 1
            # only add 3D masks to evaluation
            ThreeD = True
            for i in range(3):
                indices = np.where(current_mask==k)
                if len(set(indices[i]))<3:
                    ThreeD = False
                    print("2d found")
            if ThreeD:
                V.append(flood_fill_hull(x, px, pz))
                V2.append(compute_voxel_volume(x, px, pz))
        #create new labels for napari
        # current_mask[np.where(current_mask!=0)] += new_label.max()
        # new_label[position[0]:position[0]+current_mask.shape[0],
        # position[1]:position[1] + current_mask.shape[1],
        # position[2]: position[2] + current_mask.shape[2]] = current_mask

    return V, V2, new_label