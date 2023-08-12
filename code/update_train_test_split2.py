'''
Read in JSON files from a Speech Accessibility Project corpus, and generate a train/dev/test split.
Participants who read lists 1-7 are in the train split,
 those who read list 8 are dev,
 those who read lists 9-10 are test.

Written: Mark Hasegawa-Johnson
Revision History: 
Originally written 2023 Aug 12, re-using a little code from update_train_test_split.py.
'''

import argparse, json, copy, os.path, glob, collections, random
import numpy as np

##################################################################################
# Since list ID is not provided in the data distribution,
# list ID is classified if participant reads one of the following prompts.
text2list = {
    "What's the distance to Pluckley, England?" : "list1",
    "Play hip hop music on Apple music." : "list2",
    "Set a timer for 60 minutes." : "list3",
    "Wake me up at 6:30 AM every day." : "list4",
    "Did the Seattle Mariners win?" : "list5",
    "Cancel alarm for noon." : "list6",
    "When is Buffalo Wild Wings open until?" : "list7",
    "Brighten the outdoor lights." : "list8",
    "Turn off the outdoor lights." : "list9",
    "How did the Arizona Diamondbacks game turn out yesterday?" : "list10"
}

####################################################################################
# Put lists 1-7 in train, list8 in dev, lists 9-10 in test
list2split = {
    'list1':'train','list2':'train','list3':'train','list4':'train','list5':'train',
    'list6':'train','list7':'train','list8':'dev','list9':'test','list10':'test'
}

####################################################################################
def main(datadir, logfile, outputfile):
    '''
    Create and return a new train/dev/test split based on which list each speaker reads.

    @param:
    datadir (str): directory containing data
    outputfile (str): output filenames are constructed from this by adding integers,
      e.g., 0 is added to best result, 1 is added to second-best, et cetera.

    @return:
    None
    '''

    participant2lists = {}
    
    # Check each participant's json file 
    # for sentences known to be unique to a given list.
    jsonfiles = glob.glob(os.path.join(datadir, '*', '*.json'))
    feature = {}
    for jsonfile in jsonfiles:
        with open(jsonfile) as f:
            data = json.load(f)
            participant = data['Contributor ID']
            participant2lists[participant] = []
            for utterance in data['Files']:
                if utterance['Prompt']['Prompt Text'] in text2list:
                    participant2lists[participant].append(text2list[utterance['Prompt']['Prompt Text']])


    twolisters = []
    emptylisters = []
    onelisters = { k:[] for k in text2list.values() }
    split = { 'train':[], 'dev':[], 'test':[] }
    for participant in participant2lists:
        if len(participant2lists[participant]) > 1:
            listid = participant2lists[participant][0]
            twolisters.append(' '.join([participant]+participant2lists[participant]))
            if all([list2split[y]==list2split[listid] for y in participant2lists[participant]]):
                split[list2split[listid]].append(participant)
            else:
                print('WARNING: Unable to assign %s: %s'%(participant,participant2lists[participant]))
        elif len(participant2lists[participant]) ==0:
            emptylisters.append(participant)
        else:
            listid = participant2lists[participant][0]
            onelisters[listid].append(participant)
            split[list2split[listid]].append(participant)

    if logfile != None:
        with open(logfile, 'w') as f:
            if len(twolisters) > 0:
                f.write('############## Participants with 2 or more lists ##############\n')
                f.write('\n'.join(twolisters) +'\n\n')
            for d in range(1,11):
                f.write('############## list%d ##############\n'%(d))
                f.write('\n'.join(onelisters['list%d'%(d)]) +'\n\n')
            if len(emptylisters) > 0:
                f.write('############## Participants not assigned to a list ##############\n')
                f.write('\n'.join(emptylisters)+'\n\n')
                

    with open(outputfile,'w') as f:
        json.dump(split, f, indent=2)
              
################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = 'Update the train/dev/test split to include new speakers.',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d','--datadir',
                        help = 'Directory containing unsplit dataset')
    parser.add_argument('-l','--logfile', default=None,
                        help = 'Specifies the list each participant was in.  May be None')
    parser.add_argument('-o','--outputfile', default='newsplit.json',
                        help = '''
                        Output filenames are based on this name, with numbers for the nth best.
                        For example: newsplit0.json, newsplit1.json, newsplit2.json
                        will be JSON-encodings of the best, second, and third-best splits found.
                        ''')

    args   = parser.parse_args()
    if not args.datadir:
        raise RuntimeError('Please use -d to specify a datadir')
        
    main(args.datadir, args.logfile, args.outputfile)
