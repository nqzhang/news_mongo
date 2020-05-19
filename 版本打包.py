import zipfile,os


def zip_dirs(dest,dirs):
    f = zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED,allowZip64=True)
    for dir in dirs.split(','):
        if os.path.isfile(dir):
            f.write(dir)
            continue
        for dirpath, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                f.write(os.path.join(dirpath, filename))
    f.close()

dirs = "document,models,script,static,template,utils,views,app.py,server.py,requirements.txt,requirements_linux.txt"
zip_dirs('news_mongo.zip',dirs)
