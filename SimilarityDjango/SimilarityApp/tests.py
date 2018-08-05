import os
import zipfile
import shutil

def generate_zip_file(directory):
    path_splited = os.path.split(directory)
    zip_name = path_splited[-1] + '.zip'
    target_directory = os.path.join(path_splited[0], path_splited[-1]+'_zip')
    target_zip_path = os.path.join(target_directory, zip_name)
    shutil.rmtree(target_directory, ignore_errors=True)
    os.makedirs(target_directory, exist_ok=True)
    z = zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(directory):
        fpath = dirpath.replace(directory,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath+filename)
    z.close()

def decompress(zip_path, target_directory):
    f = zipfile.ZipFile(zip_path)
    shutil.rmtree(target_directory, ignore_errors=True)
    os.makedirs(target_directory, exist_ok=True)
    for name in f.namelist():
        f.extract(name, target_directory)

# Create your tests here.
if __name__ == '__main__':
    # decompress('C:\\Users\\JunyiLee\\Desktop\\李俊仪-201630609971_zip\\李俊仪-201630609971.zip', 'C:\\Users\\JunyiLee\\Desktop\\李俊仪-201630609971_files')
    filetype = os.path.splitext('算法实验-李俊仪-201630609971.zip')[-1]
    print(filetype)