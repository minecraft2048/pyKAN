#Shared Utility methods and classes
import sys
import json
import os
import multiprocessing
try:
    import requests
except ImportError:
    raise ImportError("This program requires the python requests module. Please install it using pip or your distro's package manager")

DEBUG=False
default_ckan_repo = "https://github.com/KSP-CKAN/CKAN-meta/archive/master.tar.gz"
repository_list = "https://raw.githubusercontent.com/KSP-CKAN/CKAN-meta/master/repositories.json"

def download_json(uri):
    debug ('Downloading %s' % uri)
    r = requests.get(uri)
    debug('Returning data: %s' % r.text)
    return r.json()

def __download_file__(dl_data):
    debug('Downloading %s' % dl_data['uri'])
    filename = os.path.join(dl_data['cachedir'],os.path.basename(dl_data['uri']))
    retries = 0
    done = False
    while not done and retries < dl_data['retries']:
        try:
            r = requests.get(dl_data['uri'], stream=True)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024): 
                    if chunk: 
                        debug_n('#')
                        f.write(chunk)
                done = True
        except Exception as e:
            retries += 1
            debug ('Download error %s. %s  retries remain' %(e, dl_data['retries'] - retries))
            done = False
    debug('')
    return filename        

def download_files(urilist, cachedir, retries):
    dl_data = []
    for uri in urilist:
        dl_data.append({"uri": uri,"cachedir": cachedir, 'retries': retries})
    pool = multiprocessing.Pool()
    return pool.map(__download_file__, dl_data)


def is_kspdir(path):
    return os.path.isdir(os.path.join(path,'GameData'))

def error(message,code=1):
    sys.stderr.write('%s\n' %message)
    sys.exit(code)

def debug(message):
    if DEBUG:
        sys.stderr.write('%s\n' %message)

def debug_n(message):
    if DEBUG:
        sys.stderr.write('%s' %message)
        sys.stderr.flush()

def SaveJsonToFile(filename,data):
    debug('Saving %s to %s' % (data,filename))
    open(filename,'w').write(json.dumps(data,indent=4))    

def ReadJsonFromFile(filename, default=None,create=False):
    if default == None:
        return json.loads(open(filename).read())
    else:
        try:
            return ReadJsonFromFile(filename)
        except IOError:
            if create:
                SaveJsonToFile(filename,default)
            return default

def mkdir_p(targetpath):
    pathlist = isinstance(targetpath,list) and targetpath or targetpath.split(os.pathsep)
    pathSoFar = ''
    for i in pathlist:
        pathSoFar = os.path.join(pathSoFar,i)
        if os.path.isdir(pathSoFar):
            continue
        else:
            os.mkdir(pathSoFar)

