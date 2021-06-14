import numpy as np
from skimage.measure import label
from tifffile import TiffFile
from scipy.stats import ttest_ind
import copy
from skimage import exposure
from utility import get_masks_and_volume
from display import show_segmentation,show_histogram
import os

class WorkerFacade():
    def evaluate(self, path, multichannel=True):
        px = 0
        pz = 0
        with TiffFile(path) as tif:
            image = tif.asarray()
            metadata = tif.imagej_metadata["Info"].split("\n")
            for tag in metadata:
                if "ScalingX" in tag:
                    px = float(tag.split(" ")[-1]) * 10 ** 6  # convert to micrometer
                if "ScalingZ" in tag:
                    pz = float(tag.split(" ")[-1]) * 10 ** 6  # convert to micrometer

        if px == 0 or pz == 0:
            raise ValueError("wtf metadata?")
        array = image[:, 2].astype(np.float64)
        if multichannel:
            lamb1 = image[:, 0].astype(np.float64)
            lamb1 = exposure.adjust_gamma(lamb1, gamma=0.9)
            lamb1 = np.clip((lamb1 / lamb1.max()) - 0.01, 0, 1)
            lamb1 /= lamb1.max()

        # thresh = threshold_otsu(array[10])

        array = exposure.adjust_gamma(array, gamma=0.9)
        # array = gaussian_filter(array, sigma=0.05)#todo: check this parameter
        array = np.clip((array / array.max()) - 0.01, 0, 1)

        array /= array.max()

        binary = array != 0

        lab = label(binary)
        print(lab.max())
        coords = []
        n_deg_coords = []
        deg_volumes = []
        ndeg_volumes = []
        dia = []
        n_deg_dia = []
        for i in range(lab.max()):
            i += 1
            print(i)
            indices = np.where(lab == i)
            # kick noise
            if indices[0].shape[0] < 30:
                lab[indices] = 0
            else:

                n_indices = list(copy.deepcopy(indices))
                position = []
                c = False
                # kick two dimensional crops....
                for z in range(3):
                    position.append(n_indices[z].min())
                    n_indices[z] -= n_indices[z].min()
                    if len(set(n_indices[z])) < 3:
                        c = True
                if c: continue
                # new = np.zeros((n_indices[0].max()+1,n_indices[1].max()+1,n_indices[2].max()+1)).astype(np.uint8)
                new = array[indices[0].min():indices[0].max(),
                      indices[1].min():indices[1].max(),
                      indices[2].min():indices[2].max(), ]  # indices Z,X,Y
                if multichannel:
                    lamb_volume = lamb1[indices[0].min():indices[0].max(),
                                  indices[1].min():indices[1].max(),
                                  indices[2].min():indices[2].max(), ]
                    lamb_ind = np.where(lamb_volume != 0)
                    if lamb_ind[0].shape[0] > 0.1 * indices[0].shape[0]:
                        deg_volumes.append(new)
                        coords.append(position)
                        dia.append(int(np.sqrt(
                            ((indices[1].max() - indices[1].min()) ** 2 + (indices[2].max() - indices[2].min()) ** 2) / 2)))
                    else:
                        ndeg_volumes.append(new)
                        n_deg_coords.append(position)
                        n_deg_dia.append(int(np.sqrt(
                            ((indices[1].max() - indices[1].min()) ** 2 + (indices[2].max() - indices[2].min()) ** 2) / 2)))
                else:
                    deg_volumes.append(new)
                    coords.append(position)
                    dia.append(int(np.sqrt(
                        ((indices[1].max() - indices[1].min()) ** 2 + (indices[2].max() - indices[2].min()) ** 2) / 2)))

                # break
        # set estimated diameter to median
        dia_est = np.mean(np.array(dia))
        n_deg_dia_est = np.mean(np.array(n_deg_dia))

        V2, V, new_label = get_masks_and_volume(px, pz, deg_volumes, array, coords, diameter=dia)
        V2ndeg, Vndeg, new_label_ndeg = get_masks_and_volume(px, pz, ndeg_volumes, array, n_deg_coords, diameter=n_deg_dia)

        #show_segmentation(array, label1=new_label_ndeg)

        return V2, V2ndeg, V2

    def collect_volumes(self, path, data="data"):
        l = os.listdir(path)
        degranulated = []
        ndegranulated = []
        degranulated_other_volume = []
        n = 0
        if not os.path.exists(data):
            os.mkdir(data)
        for file in l:
            print(n)
            if ".tif" in file:
                n += 1

                result = self.evaluate(path + "\\" + file, multichannel=True)
                degranulated += result[0]
                ndegranulated += result[1]
                degranulated_other_volume += result[2]
                if "post" in path:
                    np.save(data + "\\" + str(n) + "post.npy", np.array([result[0], result[1], result[2]]))
                else:
                    np.save(data + "\\" + str(n) + ".npy", np.array([result[0], result[1], result[2]]))

    def show_saved_results(self, post=False):
        l = os.listdir("data")
        degranulated = []
        granulated = []
        for file in l:
            if post and "post" in file:
                array = np.load("data"+"\\"+ file, allow_pickle=True)
                if np.any(array):
                    degranulated += array[0]
                    granulated += array[1]
            if not post and not "post" in file:
                array = np.load("data"+"\\"+ file, allow_pickle=True)
                if np.any(array):
                    degranulated += array[0]
                    granulated += array[1]
        show_histogram(np.array(degranulated), np.array(granulated))


