import os
from facade import WorkerFacade
if __name__ == '__main__':
    path = r"D:\Daten\Nora\zu_doof_zum_auswerten\new_data\post"
    facade = WorkerFacade()
    facade.collect_volumes(path)
    facade.show_saved_results(post=True)
    # model_type='cyto' or model_type='nuclei'

