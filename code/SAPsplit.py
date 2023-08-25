import argparse, json, copy, os.path, glob, collections, random, logging
import promptfiles

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

def create_subset2prompts(prompts, novel_sentences):
    '''
    Create a dict that shows the mapping from subset to a list of prompts,
    for the prompts whose location in a list is defined.

    @param:
    prompts, novel_sentences: as returned by promptfiles.load_PD_prompts

    @return:
    subset2prompts (dict): maps subset to sets of prompt texts, not including spontaneous speech
    '''
    subsets = ['train','dev','test']
    subset2list = { 'train':[1,2,3,4,6,7,8], 'dev':[5], 'test':[9,10] }

    subset2prompts = { s:set() for s in subsets }
    for subset in subsets:
        for listnum in subset2list[subset]:
            for block in prompts[listnum]:
                for ind in prompts[listnum][block]:
                    if prompts[listnum][block][ind][0] != "Spontaneous Speech Prompts":
                        subset2prompts[subset].add(prompts[listnum][block][ind][2])
    return subset2prompts

def load_corpus(datadir):
    '''
    @param:
    datadir (str): directory containing the corpus

    @return:
    corpus (dict): corpus[contributor_id] is content of one JSON file
    '''
    corpus = {}
    for jsonfile in glob.glob(os.path.join(datadir, '*', '*.json')):
        with open(jsonfile) as f:
            contributor = json.load(f)
            corpus[contributor['Contributor ID']] = contributor
    return corpus

def assign_contributors(subset2prompts, corpus):
    '''
    Assign each contributor to the subset from which the contributor has read the 
    largest number of prompt texts.  This accounts for lack of certainty about which 
    list the contributor read, and it accounts for some overlap between lists.

    @param:
    subset2prompts (dict): map a subset to a list of prompts known to be in that subset
    corpus (dict): map contributor_id to the dict stored in their json file

    @return:
    subset2contributors (dict): map subset to a set of contributor_ids
    subset2wavfiles (dict): map subset to a set of wavfile names
    wavfile2prompt (dict): map wavfile name to prompt [category, subcategory, prompttext]
    '''
    subset2contributors = {'train':set(), 'dev':set(), 'test':set()}
    subset2wavfiles = {'train':set(), 'dev':set(), 'test':set()}
    wavfile2prompt = {}
    
    for contributor_id,data in corpus.items():
        prompts = set(u['Prompt']['Prompt Text'].strip() for u in data['Files'])
            
        # n[subset] = # prompts that are known to be in that subset
        n = { s:len(prompts.intersection(subset2prompts[s])) for s in subsets }

        # assign this contributor to the subset with the most confirmed prompts
        (c, subset) = max([(v,k) for (k,v) in n.items()])
        subset2contributors[subset].add(contributor_id)

        # Add their wavfiles
        for u in data['Files']:
            subset2wavfiles[subset].add(u['Filename'])
            wavfile2prompt[u['Filename']] = [
                u['Prompt']['Category Description'],
                u['Prompt']["Sub Category Description"],                
                u['Prompt']['Prompt Text'] ]
            
    return subset2contributors, subset2wavfiles, wavfile2prompt

def determine_sharing(subset2wavfiles, wavfile2prompt):
    '''
    Divide dev and test subsets into shared and unshared portions.

    @param:
    subset2wavfiles (dict): map subset to a list of wavfiles
    wavfile2prompt (dict): map wavefile to [category, subcategory, prompt text]

    @return:
    subset2files (dict):
     subset2files['train'][wavfile] = prompt
     subset2files['dev']['shared'][wavfile] = prompt if prompt is in subset2files['train']
     subset2files['dev']['unshared'][wavfile] = prompt if not
    '''
    subset2files = {}
    subset2files['train'] = { w:wavfile2prompt[w][2] for w in subset2wavfiles['train'] }
    trainprompts = set(subset2files['train'].values())
    
    for subset in ['dev','test']:
        subset2files[subset] = { 'shared':{}, 'unshared':{} }
        for w in subset2wavfiles[subset]:
            p = wavfile2prompt[w]
            if p[2] in trainprompts and p[0]!="Spontaneous Speech Prompts":
                subset2files[subset]['shared'][w]=p
            else:
                subset2files[subset]['unshared'][w]=p
    return subset2files

####################################################################################
def main(datadir):
    '''
    Create and return a new train/dev/test split based on which list each speaker reads,
    and based on shared vs. unshared prompt texts.

    @param:
    datadir (str): directory containing data

    @return:
    subset2contributors (dict): map subset to contributor_id
    subset2files (dict): as returned by determine_sharing
    '''
    prompts, novel_sentences = promptfiles.load_PD_prompts()
    subset2prompts = create_subset2prompts(prompts, novel_sentences)

    corpus = load_corpus(datadir)
    subset2contributors,subset2wavfiles,wavfile2prompt=assign_contributors(subset2prompts,corpus)

    subset2files = determine_sharing(subset2wavfiles, wavfile2prompt)
    return subset2contributors, subset2files

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
