import argparse, json, copy, os.path, glob, collections, random, logging, pandas
import promptfiles

'''
Read in JSON files from a Speech Accessibility Project corpus, and generate a train/dev/test split.

SPLIT DEFINITIONS________________________________
subsets are:
  train: lists 1-4 and 6-8
  dev: list 5
  test: lists 9-10

psets are:
  common: shared by train, dev, and test
  shared: shared by train and either dev or test
  repeat: shared by dev and test (should be empty)
  unique: unique to a subset

HOW TO RUN THIS________________________________

See the description string in the argparse.ArgumentParser object

HISTORY________________________________________

Written: Mark Hasegawa-Johnson
Revision History: 
Originally written 2023 Aug 12, re-using a little code from update_train_test_split.py.
Revised 2023 Aug 23
Revised 2024 Jan 16 to use the listfiles
Revised 2024 May 11 to expect all input JSONS in toplevel datadir
'''

def create_subset2contributors(listfile):
    '''
    @param:
    listfile (str): XLSX
      first row should have column titles including "ContributorID" and "List#"

    @return:
    subset2contributors (dict of lists): map train, dev, test to lists of contributor IDs
    '''
    subset2list = {
        'train':[1,2,3,4,6,7,8,11,12,13,14,16,17,18],
        'dev':[5,15],
        'test':[9,10,19,20] }

    list2subset = { n:k for k,v in subset2list.items() for n in v }
    subset2contributors = {'train':set(),'dev':set(),'test':set() }

    df = pandas.read_excel(listfile)
    df.set_index("ContributorID", inplace=True)
    ls = df["List#"] # list series
    for uuid, listtxt in ls.items():
        listnum = int(listtxt.split()[-1])  # assume the integer is last word in the string
        subset2contributors[list2subset[listnum]].add(uuid)
    return subset2contributors
    
def create_subset2prompts(prompts):
    '''
    Create a dict that shows the mapping from subset to a list of prompts,
    for the prompts whose location in a list is defined.

    @param:
    prompts (dict):
     prompts[listnum][block][i][0] is category
     prompts[listnum][block][i][1] is a subcategory, or empty string
     prompts[listnum][block][i][2] is a prompt text

    @return:
    subset2prompts (dict): maps subset to sets of prompt texts, not including spontaneous speech
    '''
    subsets = ['train','dev','test']
    subset2list = { 'train':[1,2,3,4,6,7,8], 'dev':[5], 'test':[9,10] }

    subset2prompts = { s:set() for s in subsets }
    for subset in subsets:
        for listnum in subset2list[subset]:
            for block in prompts[listnum]:
                for ind in range(len(prompts[listnum][block])):
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
    for jsonfile in glob.glob(os.path.join(datadir, '*.json')):
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
    '''
    subset2contributors = {'train':set(), 'dev':set(), 'test':set()}
    subset2wavfiles = {'train':set(), 'dev':set(), 'test':set()}
    wavfile2prompt = {}
    
    for contributor_id,data in corpus.items():
        prompts = set(u['Prompt']['Prompt Text'].strip() for u in data['Files'])

        # n[subset] = # prompts that are known to be in that subset
        n = { s:len(prompts.intersection(subset2prompts[s])) for s in ['train','dev','test'] }

        # assign this contributor to the subset with the most confirmed prompts
        (c, subset) = max([(v,k) for (k,v) in n.items()])
        subset2contributors[subset].add(contributor_id)
            
    return subset2contributors

def assign_wavfiles(subset2contributors, corpus):
    '''
    Assign each wavefile

    @param:
    subset2contributors (dict): map a subset to a list of contributors
    corpus (dict): map contributor_id to the dict stored in their json file

    @return:
    subset2wavfiles (dict): map subset to a set of wavfile names
    wavfile2prompt (dict): map wavfile name to prompt [category, subcategory, prompttext, transcript]
    '''
    subset2wavfiles = {'train':set(), 'dev':set(), 'test':set()}
    wavfile2prompt = {}

    contributor2subset = {}
    for subset,L in subset2contributors.items():
        for c in L:
            if c in contributor2subset:
                if contributor2subset[c] != subset:
                    raise RuntimeError("%s has 2 subsets: %s and %s"%(c,subset,contributor2subset[c]))
            contributor2subset[c] = subset

    for contributor_id,data in corpus.items():
        if contributor_id in contributor2subset:
            subset = contributor2subset[contributor_id]
        elif contributor_id.lower() in contributor2subset:
            subset = contributor2subset[contributor_id.lower()]
        else:
            logging.warn('%s in listfile but not in corpus'%(contributor_id.lower()))
        
        # Add their wavfiles
        for u in data['Files']:
            subset2wavfiles[subset].add(u['Filename'])
            wavfile2prompt[u['Filename']] = [
                u['Prompt']['Category Description'],
                u['Prompt']["Sub Category Description"],                
                u['Prompt']['Prompt Text'],
                u['Prompt']['Transcript'] ]
            
    return subset2wavfiles, wavfile2prompt

def determine_sharing(subset2wavfiles, wavfile2prompt):
    '''
    Divide dev and test subsets into shared and unshared portions.

    @param:
    subset2wavfiles (dict): map subset to a list of wavfiles
    wavfile2prompt (dict): map wavefile to [category, subcategory, prompt text]

    @return:
    subset2files (dict):
     subset2files['train'][wavfile] = [prompt,transcript]
     subset2files['dev']['shared'][wavfile] = [prompt,transcript] if prompt is in subset2files['train']
     subset2files['dev']['unshared'][wavfile] = [prompt,transcript] if not
    '''
    subset2files = {}
    subset2files['train'] = {}
    for w in subset2wavfiles['train']:
        subset2files['train'][w] = [ wavfile2prompt[w][2], wavfile2prompt[w][3] ]
    trainprompts = set(p[0] for p in subset2files['train'].values())
    
    for subset in ['dev','test']:
        subset2files[subset] = { 'shared':{}, 'unshared':{} }
        for w in subset2wavfiles[subset]:
            p = wavfile2prompt[w]
            if p[2] in trainprompts and p[0]!="Spontaneous Speech Prompts":
                subset2files[subset]['shared'][w]=[ p[2], p[3] ]
            else:
                subset2files[subset]['unshared'][w]= [ p[2], p[3] ]
    return subset2files

####################################################################################
def main(datadir, listfile=None):
    '''
    Create and return a new train/dev/test split based on which list each speaker reads,
    and based on shared vs. unshared prompt texts.

    @param:
    datadir (str): directory containing data

    @return:
    subset2contributors (dict): map subset to contributor_id
    subset2files (dict): as returned by determine_sharing
    '''
    corpus = load_corpus(datadir)

    if listfile==None:
        prompts = promptfiles.load_prompts('PromptsAnnotationGuidelines')
        subset2prompts = create_subset2prompts(prompts)
        subset2contributors=assign_contributors(subset2prompts,corpus)

    else:
        subset2contributors = create_subset2contributors(listfile)
        
    subset2wavfiles,wavfile2prompt=assign_wavfiles(subset2contributors,corpus)
    subset2files = determine_sharing(subset2wavfiles, wavfile2prompt)
    return subset2contributors, subset2files

################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = '''Update the train/dev/test split to include new speakers.
        This requires some steps to run:

        (1) Somebody at UIUC needs to create the file ../lists/contributor_lists_$(current).xlsx
        by downloading relevant information from the contributor app.

        (2) The file SpeechAccessibility_2024-04-30_Only_Json.7z should be copied from the distribution,
        and unpacked in a directory that will be called datadir.

        (3) Run this program as:
        python SAPSplit.py datadir ../test_outputs/SpeechAccessibility_$(current)_Split.json -c ../test_outputs/SpeechAccessibility_$(current)_Split_by_Contributors.json -L ../lists/contributor_lists_$(current).xlsx -l logs/SpeechAccessibility_$(current)_Split.log
        ''',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('datadir',help = 'Directory containing unsplit dataset JSON files')
    parser.add_argument('outputfile', help='''Output filename''')
    parser.add_argument('-c','--contributorsplit', help='''Split listed by contributors''')
    parser.add_argument('-L','--listfile',help='XLSX mapping each contributor to one or more lists')
    parser.add_argument('-l','--logfile', default=None,
                        help = 'Where to send debug outputs (instead of stdout)')

    args   = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    if args.logfile:
        logging.basicConfig(filename=args.logfile,filemode='w')

        
    subset2contributors, subset2files = main(args.datadir, args.listfile)

    logging.info('%s %d'%('train', len(subset2files['train'])))
    for s in ['dev','test']:
        for p in ['shared','unshared']:
            logging.info('%s %s %d'%(s,p,len(subset2files[s][p])))

    with open(args.outputfile,'w') as f:
        json.dump(subset2files,f,indent=1,sort_keys=True)

    if args.contributorsplit != None:
        with open(args.contributorsplit,'w') as f:
            x={subset:[c for c in sorted(subset2contributors[subset])] for subset in subset2contributors}
            json.dump(x ,f,indent=1,sort_keys=True)
