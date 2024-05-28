import json,os,argparse,glob,shutil

def copy_contributors(contributors, src, tgt, transcriptfile):
    '''
    Copy contributors from src to tgt
    '''
    os.makedirs(tgt,exist_ok=True)
    # Copy the contributor directories to tgt
    for contributor in contributors:
        s = os.path.join(src,contributor)
        t = os.path.join(tgt,contributor)
        if os.path.exists(t):
            print(t+' already exists; not copying')
        elif not os.path.exists(s):
            print(s+' does not exist; not copying')
        else:
            shutil.copytree(s,t)
            
    # Create a new transcript listing JSON in tgt
    with open(os.path.join(tgt, transcriptfile),'w') as f:
        json.dump(contributors,f,indent=1,sort_keys=True)
        
                       
    

################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = 'Re-arrange a data distribution into train, dev, test directories',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('datadir',help = 'Directory containing unsplit dataset and JSON file')
    parser.add_argument('traindevdir',help = 'Directory into which to write train and dev splits')
    parser.add_argument('testdir',help = 'Directory into which to write test split')

    args   = parser.parse_args()

    pat = os.path.join(args.datadir,'Speech*Contributors.json')
    jsonfile=glob.glob(pat)
    if len(jsonfile) != 1:
        raise RuntimeError('There should be exactly 1 file matching the pattern '+pat)
    with open(jsonfile[0]) as f:
        split2contributors = json.load(f)

    pat = os.path.join(args.datadir,'Speech*Split.json')
    jsonfile=glob.glob(pat)
    if len(jsonfile)!=1:
        raise RuntimeError('There should be exactly 1 file matching the pattern '+pat)
    with open(jsonfile[0]) as f:
        split2prompts = json.load(f)
    splitfilename=os.path.splitext(os.path.basename(jsonfile[0]))[0]

    for split in ['train','dev']:
        tgt = os.path.join(args.traindevdir,split)
        copy_contributors(split2contributors[split], args.datadir, tgt, splitfilename+'_'+split+'.json')
        
    if 'testdir' in args:
        tgt = os.path.join(args.testdir,split)
        copy_contributors(split2contributors['test'], args.datadir, tgt, splitfilename+'_test.json')
