import argparse, json, copy, os.path, glob, collections, random, logging
import promptfiles
from collections import defaultdict

def main(jsonfile1, jsonfile2, logfile):
    '''
    Test the overlaps between jsonfile1 and jsonfile2, and report them.

    Report to stdout in the format:
    DELETIONS:  <<entries in jsonfile1 that are gone in jsonfile2>>
    ...
    INSERTIONS:  <<entries in jsonfile2 that were not in jsonfile1>>
    ...
    SUBSTITUTIONS: <<entries in jsonfile1 that moved to a different category in jsonfile2>>
    ...
    
    Save the resulting file lists to logfile.
    '''
    with open(jsonfile1) as f:
        json1 = json.load(f)
    with open(jsonfile2) as f:
        json2 = json.load(f)

    utt2subset1 = { utt:'train' for utt in json1['train'] }
    utt2subset2 = { utt:'train' for utt in json2['train'] }
    for s in ['dev','test']:
        for ss in ['shared','unshared']:
            for utt in json1[s][ss]:
                utt2subset1[utt]=s+':'+ss
            for utt in json2[s][ss]:
                utt2subset2[utt]=s+':'+ss

    deleted = defaultdict(list)
    substituted = defaultdict(dict)
    inserted = defaultdict(list)

    
    for set1 in json1:
        if set1 == 'train':
            subsets = {'train': list(json1[set1].keys()) }
        else:
            subsets = {set1+':'+subset1: list(json1[set1][subset1].keys()) for subset1 in json1[set1] }
        for k,v in subsets.items():
            for utt in v:
                if utt not in utt2subset2:
                    deleted[k].append(utt)
                elif k != utt2subset2[utt]:
                    if utt2subset2[utt] not in substituted[k]:
                        substituted[k][utt2subset2[utt]] = []
                    substituted[k][utt2subset2[utt]].append(utt)


    for set2 in json2:
        if set2 == 'train':
            subsets = {'train': list(json2[set2].keys()) }
        else:
            subsets = {set2+':'+subset2: list(json2[set2][subset2].keys()) for subset2 in json2[set2] }
        for k,v in subsets.items():
            for utt in v:
                if utt not in utt2subset1:
                    inserted[k].append(utt)

    if len(deleted) > 0:
        print('DELETED:')
        for k in deleted:
            print(k,': ',len(deleted[k]))
        print('\n')
    if len(inserted) > 0:
        print('INSERTED:')
        for k in inserted:
            print(k,': ',len(inserted[k]))
        print('\n')
    if len(substituted) > 0:
        print('SUBSTITUTED:')
        for k1 in substituted:
            for k2 in substituted[k1]:
                print(k1,' -> ',k2,': ',len(substituted[k1][k2]))
        print('\n')

    with open(logfile,'w') as f:
        json.dump({ 'INSERTED':inserted, 'DELETED':deleted, 'SUBSTITUTED':substituted }, f,
                  indent=2, sort_keys=True )
    
    
################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = 'Compare jsonfile1 and jsonfile2; print change summary to jsonfile3',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('jsonfile1')
    parser.add_argument('jsonfile2')
    parser.add_argument('jsonfile3')
    
    args   = parser.parse_args()
    main(args.jsonfile1, args.jsonfile2, args.jsonfile3)
