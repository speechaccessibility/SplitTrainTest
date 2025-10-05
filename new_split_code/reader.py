import os.path, json, glob

def path2fid(path):
    return os.path.splitext(os.path.basename(path))[0]

def fid2sid(fid):
    '''
    Extract the speaker ID from the FID
    '''
    return fid.split('_')[0]

def path2sid(path):
    '''
    Extract the speaker ID from the path
    '''
    return fid2sid(path2fid(path))

def read_sapc1(sapc1_dir, splits):
    '''
    Read in split.tsv files from sapc1_dir for split in splits.
    @return:
    sapc1_sid2split[sid] = split
    '''
    sapc1_sid2split = {}
    for split in splits:
        with open(os.path.join(sapc1_dir, split+'.tsv')) as f:
            for line in f:
                if '.wav' in line:   # Ignore comments and directories, keep only wav file lines
                    sid = path2sid(line.split()[0])
                    sapc1_sid2split[sid] = split
    return sapc1_sid2split

def read_dist(dist_dir, splits):
    '''
    load necessary info from the distribution
    @return:
    dist_sid2meta[sid] = (split, etiology)
    dist_fid2trans[fid] = transcription
    '''
    dist_sid2meta = {}
    dist_fid2trans = {}
    for split in splits:
        jsonpathnames = glob.glob(os.path.join(dist_dir,split[0].upper()+split[1:],"*.json"))
        for jsonpathname in jsonpathnames:
            sid = os.path.splitext(os.path.basename(jsonpathname))[0]
            with open(jsonpathname) as f:
                data = json.load(f)
                # 1. Read etiology and split of speaker
                if 'Etiology' not in data:
                    raise RuntimeError(split+'/'+sid+' has no Etiology')
                dist_sid2meta[sid] = (split, data['Etiology'] )
                
                # 2. Read in the text transcript of each utterance
                for fdict in data['Files']:
                    fid = path2fid(fdict['Filename'])
                    if 'Prompt' not in fdict or 'Transcript' not in fdict['Prompt']:
                        raise RuntimeError(split+'/'+fid+' has no Transcript')
                    dist_fid2trans[fid] = fdict['Prompt']['Transcript']
    return dist_sid2meta, dist_fid2trans
                    
def read_sapc2(sapc2_dir, splits):
    '''
    read data from SAPC2 files
    @return:
    sapc2_fid2meta[fid] = (split,etiology)
    '''
    sapc2_fid2meta = {}
    for split in splits:
        with open(os.path.join(sapc2_dir, split+'.txt')) as f:
            for line in f:
                fields = line.strip().split()
                sapc2_fid2meta[path2fid(fields[0])] = (split,' '.join(fields[1:]))
    return sapc2_fid2meta

def write_sapc2(sapc2_fid2meta, sapc2_dir, splits):
    fps = {}
    for split in splits:
        fps[split] = open(os.path.join(sapc2_dir, split+'.txt'),'w')
    for (fid,meta) in sapc2_fid2meta.items():
        split = meta[0]
        fps[split].write(os.path.join(split,fid+'.wav')+'\t'+meta[1]+'\n')
    for split in splits:
        fps[split].close()
    
                  
