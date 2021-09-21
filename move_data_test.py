import pathlib
import time

from_folder = pathlib.Path(
	'/Anodesanas spektru dati/2 aleksandra paraugs')
to_folder = pathlib.Path('S:\\PAAO\\Data\\Anodesanas spektru dati\\test_gui')

files = from_folder.rglob('*.txt')
files = [x for x in files if x.is_file() and x.name != 'ref_spektrs.txt']


for i, file in enumerate(files):
    file.rename(to_folder/file.name)
    # 100ms
    time.sleep(0.1)
    print(file.name)
    # if i == 250:
    #     break


new_files = to_folder.rglob('*.txt')
new_files = [x for x in new_files if x.is_file() and x.name !=
             'ref_spektrs.txt']


for i, file in enumerate(new_files):
    file.rename(from_folder/file.name)
