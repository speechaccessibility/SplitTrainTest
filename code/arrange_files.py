import json,os,argparse,glob,shutil

################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = 'Re-arrange a data distribution into train, dev, test directories',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('datadir',help = 'Directory containing unsplit dataset and JSON file')
    parser.add_argument('outputdir',help = 'Directory into which to write')

    args   = parser.parse_args()

    pat = os.path.join(args.datadir,'Speech*Contributors.json')
    jsonfile=glob.glob(pat)
    if len(jsonfile)<1:
        raise RuntimeError('No file found matching the pattern '+pat)
    elif len(jsonfile)>1:
        raise RuntimeError("More than one file matched the pattern "+pat)
    with open(jsonfile[0]) as f:
        split2contributors = json.load(f)

    pat = os.path.join(args.datadir,'Speech*Split.json')
    jsonfile=glob.glob(pat)
    if len(jsonfile)<1:
        raise RuntimeError('No file found matching the pattern '+pat)
    elif len(jsonfile)>1:
        raise RuntimeError("More than one file matched the pattern "+pat)
    with open(jsonfile[0]) as f:
        split2prompts = json.load(f)
    splitfilename=os.path.splitext(os.path.basename(jsonfile[0]))[0]

    for split in ['train','dev','test']:
        tgt = os.path.join(args.outputdir,split)
        os.makedirs(tgt,exist_ok=True)
        # Copy the contributor directories to tgt
        for contributor in split2contributors[split]:
            src = os.path.join(args.datadir,contributor)
            tgt2 = os.path.join(tgt,contributor)
            if os.path.exists(tgt2):
                print(tgt2+' already exists; not copying')
            else:
                shutil.copytree(src,os.path.join(tgt,contributor))

        # Create a new transcript listing JSON in tgt
        with open(os.path.join(tgt,splitfilename+'_'+split+'.json'),'w') as f:
            json.dump(split2prompts[split],f,indent=1,sort_keys=True)
        
                       
