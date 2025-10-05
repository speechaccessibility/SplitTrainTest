import argparse, sys
import reader
"""
This script tests split_sapc2_data.py.  It reads that scripts inputs and outputs,
and checks that they meet the conditions: 

1. All speakers that were part of any split in SAPC1 must be placed in the 
train or dev splits of SAPC2.

2. Any speaker that was in the train or dev splits of any research
distribution cannot be part of the test1 or test2 splits for SAPC2.

3. The train and dev splits of SAPC2 contain at most 875 and 124 speakers,
respectively.

4. From the speakers in SAPC test1 and test2, the test utterances
will include only utterances whose text transcription is not identical to
any utterance spoken by a speaker in any train or dev distribution.
"""

etiologies = ['Down Syndrome','Cerebral Palsy','ALS',"Parkinson's Disease","Stroke"]
splits = ['dev', 'test1', 'test2', 'train']
maxcounts = { 'train':875, 'dev':124 }


#####################################################################################
def main(sapc1_dir, dist_dir, sapc2_dir):
    sapc1_sid2split = reader.read_sapc1(sapc1_dir, splits)
    dist_sid2meta, dist_fid2trans = reader.read_dist(dist_dir, splits)
    sapc2_fid2meta = reader.read_sapc2(sapc2_dir, splits)

    # 1. All speakers that were part of any split in SAPC1 must be placed in the 
    # train or dev splits of SAPC2.
    for (fid,meta) in sapc2_fid2meta.items():
        sid = reader.fid2sid(fid)
        for split in ['test1','test2']:
            if sid in sapc1_sid2split and meta[0]==split:
                print('Error 1: %s was in SAPC1 but is in SAPC2/%s'%(fid,split))
    print('Test 1 passed: No file from SAPC1 was found in SAPC2/test{1,2}')

    # 2. Any speaker that was in the train or dev splits of any research
    # distribution cannot be part of the test1 or test2 splits for SAPC2.
    for (fid,meta) in sapc2_fid2meta.items():
        sid = reader.fid2sid(fid)
        for split in ['test1','test2']:
            for s2 in ['train','dev']:
                if sid in dist_sid2meta and dist_sid2meta[sid]==s2 and meta==split:
                    print('Error 2: %s was in dist/%s but is in SAPC2/%s'%(fid,s2,split))
    print('Test 2 passed: No file from SAPC2/test{1,2} was found in dist/{train,dev}')
        
    # 3. The train and dev splits of SAPC2 contain at most 875 and 124 speakers,
    # respectively.
    sapc2_split2sid = {'train':set(), 'dev':set()}
    sapc2_meta2sid = {(s,e):set() for s in ['train','dev'] for e in etiologies}
    for (fid,meta) in sapc2_fid2meta.items():
        if meta[0] in sapc2_split2sid:
            sapc2_split2sid[meta[0]].add(reader.fid2sid(fid))
            sapc2_meta2sid[meta].add(reader.fid2sid(fid))
    for (split,sids) in sapc2_split2sid.items():
        if len(sids) != maxcounts[split]:
            print('Error 3: SAPC2/%s has %d > %d items'%(split,len(sids),maxcounts[split]))
    print('Test 3 passed: SAPC2/train has 875 speakers, SAPC2/dev has 124')
    for s in ['train','dev']:
        for e in etiologies:
            print('    %s %s: %d'%(s,e,len(sapc2_meta2sid[(s,e)])))
        
    # 4. From the speakers in SAPC test1 and test2, the test utterances
    # will include only utterances whose text transcription is not identical to
    # any utterance spoken by a speaker in any train or dev distribution.
    sapc2_tr = {}
    for (fid,trans) in dist_fid2trans.items():
        sid = reader.fid2sid(fid)
        meta = dist_sid2meta[sid]
        for split in ['train','dev']:
            if fid in sapc2_fid2meta and sapc2_fid2meta[fid][0]==split:
                sapc2_tr[trans] = 'SAPC2 '+split
            elif meta[0]==split:
                sapc2_tr[trans] = 'dist '+split
    for (fid,meta) in sapc2_fid2meta.items():
        for split in ['test1','test2']:
            trans = dist_fid2trans[fid]
            if trans in sapc2_tr and meta[0]==split:
                print('Error 4: %s in SAPC2/%s has transcript in %s'%(fid,split,sapc2_tr[trans]))
    print('Test 4 passed: No transcript in SAPC2/test{1,2} matches {dist,SAPC2}/{train,dev}')

########################################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
        Test train, dev, test1 and test2 file listings for the second Speech
        Accessibility Project Challenge.

        USAGE: python %s sapc1_dir dist_dir out_dir
        EXAMPLE: python %s ../SAPC1 ~/data/jsons/SpeechAccessibility_2025-08-31 ../SAPC2
        """%(sys.argv[0],sys.argv[0]),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'sapc1_dir',action='store',
        help='Directory containing {dev,test1,test2,train}.tsv for SAP challenge 1'
        )
    parser.add_argument(
        'dist_dir',action='store',
        help="""
        directory containing distution with Train, Dev, Test1, Test2
        subdirectories, each containing one json file per speaker, 
        specifying speaker etiology, utterance filenames, utterance transcripts.
        """
    )
    parser.add_argument(
        'out_dir',action='store',
        help="Directory in which to put {dev,test1,test2,train}.txt files"
    )
    args = parser.parse_args()
    main(args.sapc1_dir, args.dist_dir, args.out_dir)

