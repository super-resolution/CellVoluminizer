import numpy as np
import matplotlib.pyplot as plt
import napari

def show_rgb(ch1, ch2):
    if len(ch1.shape) == 3:
        ch1 = np.mean(ch1, axis=0)
    if len(ch2.shape) == 3:
        ch2 = np.mean(ch2, axis=0)
    RGB = np.stack([ch1,
                    np.zeros_like(ch1), ch2],axis=-1)
    plt.imshow(RGB, )
    plt.show()

def show_segmentation(image, label1=None, label2=None):
    with napari.gui_qt():
        #viewer = napari.Viewer()
        viewer = napari.view_image(image, rgb=False)
        #viewer.add_image(array, rgb=False, colormap="green")
        viewer.add_labels(label1.astype(np.uint8), name='segmentation1')
        if np.any(label2):
            viewer.add_labels(label2.astype(np.uint8), name='segmentation2')

def show_histogram(degranulated, ndegranulated):
    bins = np.arange(0, 3.5, 0.2)
    fig, axs, = plt.subplots(2, figsize=(8, 8))
    v = (3 * ndegranulated.astype(np.float32) / (4 * np.pi)) ** (1 / 3)
    n_deg_diameter = (3 * ndegranulated.astype(np.float32) / (4 * np.pi)) ** (1 / 3) * 2
    deg_diameter = (3 * degranulated.astype(np.float32) / (4 * np.pi)) ** (1 / 3) * 2
    axs[0].hist(n_deg_diameter, bins=bins, alpha=0.5, label="not degranulated")

    axs[0].hist(deg_diameter, bins=bins, alpha=0.5, label="degranulated")
    axs[0].legend()
    (n, bins2, patches) = axs[1].hist(ndegranulated, bins=25, alpha=0.5, label="not degranulated")
    axs[1].hist(degranulated, alpha=0.5, bins=bins2, label="degranulated")

    axs[0].set_xlabel("particle diameter")
    axs[1].set_xlabel("particle volume")

    axs[0].set_ylabel("count")
    axs[1].set_ylabel("count")
    plt.savefig("pre.svg")
    plt.show()