'''
Read in JSON files from a Speech Accessibility Project corpus, and generate a train/dev/test split.

subsets are:
  train: lists 1-4 and 6-8
  dev: list 5
  test: lists 9-10

psets are:
  common: shared by train, dev, and test
  shared: shared by train and either dev or test
  repeat: shared by dev and test (should be empty)
  unique: unique to a subset

Written: Mark Hasegawa-Johnson
Revision History: 
Originally written 2023 Aug 12, re-using a little code from update_train_test_split.py.
Revised 2023 Aug 23
'''

import argparse, json, copy, os.path, glob, collections, random, logging
import numpy as np
from collections import defaultdict

##################################################################################
# Mapping from lists (1-10) to subsets
subset2list = { 'train':[1,2,3,4,6,7,8], 'dev':[5], 'test':[9,10] }

##################################################################################
# Create the subset2prompt and prompt2subsets mappings
list2prompt = {}
for d in range(1,11):
    with open('../lists/list%d.txt'%(d)) as f:
        list2prompt['list%d'%(d)] = [ x.strip() for x in f.readlines() ]

subsets = set(['train','dev','test'])
subset2prompts = {s:set(sum([list2prompt['list%d'%(d)] for d in subset2list[s]],[])) for s in subsets}

allprompts = set(sum([list2prompt['list%d'%(d)] for d in range(1,11)],[]))
prompt2subsets = {p:set([s for s in subsets if p in subset2prompts[s]]) for p in allprompts}
        
#text2list = {
#    "What's the distance to Pluckley, England?" : "list1",
#    "Play hip hop music on Apple music." : "list2",
#    "Set a timer for 60 minutes." : "list3",
#    "Wake me up at 6:30 AM every day." : "list4",
#    "Did the Seattle Mariners win?" : "list5",
#    "Cancel alarm for noon." : "list6",
#    "When is Buffalo Wild Wings open until?" : "list7",
#    "Brighten the outdoor lights." : "list8",
#    "Turn off the outdoor lights." : "list9",
#    "How did the Arizona Diamondbacks game turn out yesterday?" : "list10"
#}

####################################################################################
def main(datadir):
    '''
    Create and return a new train/dev/test split based on which list each speaker reads,
    and based on shared vs. unshared prompt texts.

    @param:
    datadir (str): directory containing data

    @return:
    subset2files (dict):
     subset2files['train'][wavfile] = prompt
     subset2files['dev']['shared'][wavfile] = prompt if prompt is in subset2files['train']
     subset2files['dev']['unshared'][wavfile] = prompt if not
    '''

    wavfile2prompt = {}
    subset2wavfiles = { s:set() for s in subsets }
    trainprompts = set()
    
    # assign each speaker to a subset, and register their prompts there
    for jsonfile in glob.glob(os.path.join(datadir, '*', '*.json')):
        with open(jsonfile) as f:
            data = json.load(f)

        w2p = {u['Filename']:u['Prompt']['Prompt Text'].strip() for u in data['Files']}
        wavfile2prompt.update(w2p)
        prompts = set(w2p.values())
            
        # n[subset] = # prompts that are known to be in that subset
        n = { s:len(prompts.intersection(subset2prompts[s])) for s in subsets }

        # assign this speaker's wavfiles to the subset with the most confirmed prompts
        (c, subset) = max([(v,k) for (k,v) in n.items()])
        subset2wavfiles[subset] |= set(w2p.keys())

        # if subset is 'train', add this speaker's prompts to 'train'
        if subset=='train':
            trainprompts |= prompts

    # for each subset, put each wavfile in the right place
    subset2files = {}
    subset2files['train'] = { w:wavfile2prompt[w] for w in subset2wavfiles['train'] }
    for subset in ['dev','test']:
        subset2files[subset] = { 'shared':{}, 'unshared':{} }
        for w in subset2wavfiles[subset]:
            p = wavfile2prompt[w]
            if p in trainprompts:
                subset2files[subset]['shared'][w]=p
            else:
                subset2files[subset]['unshared'][w]=p
                
    return subset2files

################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = 'Update the train/dev/test split to include new speakers.',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('datadir',help = 'Directory containing unsplit dataset')
    parser.add_argument('outputfile', help='''Output filename''')
    parser.add_argument('-l','--logfile', default=None,
                        help = 'Where to send debug outputs (instead of stdout)')

    args   = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    if args.logfile:
        logging.basicConfig(filename=args.logfile,filemode='w')        
    subset2files = main(args.datadir)

    logging.info('train %d'%(len(subset2files['train'])))
    for s in ['dev','test']:
        for p in ['shared','unshared']:
            logging.info('%s %s %d'%(s,p,len(subset2files[s][p])))
            
    with open(args.outputfile,'w') as f:
        json.dump(subset2files,f,indent=1)
