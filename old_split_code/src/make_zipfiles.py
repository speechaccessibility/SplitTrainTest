import os,py7zr

MAX_SIZE = 20 * 1024 * 1024 * 1024 # 20G

################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = 'Find a way to zip up all of the directories in 20G 7z zipfiles',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('datadir',help = 'Directory containing dev and train subdirs')
    parser.add_argument('outputdir',help = 'Directory into which to write the zipfiles')
    
    args   = parser.parse_args()

    # Find the size in bytes of each contributor directory
    idpath2size = {}
    for split in os.listdir(args.datadir):
        splitpath = os.path.join(args.datadir,subdir)
        if os.path.isdir(splitpath):
            for id in os.listdir(path):
                idpath = os.path.join(splitpath,iddir)
                if os.path.isdir(idpath):
                    idpath2size[id] = 0
                    for filename in os.listdir(idpath):
                        filepath = os.path.join(idpath,filename)
                        idpath2size[idpath] += os.stat(filepath).st_size
                    

                        
                        
    # Greedy assign them to zipfile lists
    ziplists = {}
    for idpath in idpath2size.keys():
        done = False
        for z in ziplists.keys():
            if ziplists[z][0]+idpath2size[idpath] < MAX_SIZE and done == False:
                ziplists[z][0] += idpath2size[idpath]
                ziplists[z][1].append(idpath)
                done = True
        if done == False:
            zipkey = len(zipfiles)
            ziplists[zipkey] = [ idpath2size[idpath], [ idpath ] ]

    # Create the zipfiles
    datadirname = os.path.basename(os.path.normpath(args.datadir)) # Call them all this name + number
    for zipkey in zipfiles.keys():
        zipfilepath = os.path.join(args.outputdir,'%s%d.7z'%(datadirname,zipkey))
        with py7zr.SevenZipFile(zipfilepath, 'w') as archive:
            for idpath in zipfiles[zipkey][1]:
                archive.write(idpath)

        
            
