import argparse, sys
import reader
"""
This script is designed to create the train/dev/test1/test2 splits
for the second Speech Accessibility Project Challenge
based on the 2025-08-31 SAP partner distribution.

It's designed to satisfy a few constraints:

1. All speakers that were part of any split in SAPC1 must be placed in the train 
or dev splits of SAPC2.

2. Any speaker that was in the train or dev splits of any research
distribution should be in train or dev, respectively, of SAPC2.

3. There must be at most 875 in train and 124 in dev, including the maximum
possible number from the minimum group.

4. From the speakers in SAPC test1 and test2, the test utterances
will include only utterances whose text transcription is not identical to
any utterance spoken by a speaker in any train or dev distribution.
"""

etiologies = ['Down Syndrome','Cerebral Palsy','ALS',"Parkinson's Disease","Stroke"]
splits = ['dev', 'test1', 'test2', 'train']
maxcounts = { 'train':875, 'dev':124 }


#####################################################################################
def main(sapc1_dir, dist_dir, out_dir):
    sapc1_sid2split = reader.read_sapc1(sapc1_dir, splits)
    dist_sid2meta, dist_fid2trans = reader.read_dist(dist_dir, splits)
    sapc2_meta2sid = { (s,e):set() for s in splits for e in etiologies }
    sapc2_fid2meta = {}

    # 1. All speakers that were part of any split in SAPC1 must be placed in the train 
    # or dev splits of SAPC2.
    for (sid,split) in sapc1_sid2split.items():
        if sid not in dist_sid2meta:
            raise RuntimeError(sid+' in SAPC1 but not distribution')
        etiology = dist_sid2meta[sid][1]
        if etiology not in etiologies:
            raise RuntimeError('WARNING: %s has unknown etiology: %s'%(split,sid,etiology))
        
        if split=='dev' or split=='train':
            sapc2_meta2sid[(split,etiology)].add(sid)
        else:
            if len(sapc2_meta2sid[('train',etiology)]) < 7*len(sapc2_meta2sid[('dev',etiology)]):
                sapc2_meta2sid[('train',etiology)].add(sid)
            else:
                sapc2_meta2sid[('dev',etiology)].add(sid)

    # 2. Any speaker that was in the train or dev splits of any research
    # distribution should be in train or dev, respectively, of SAPC2.
    avail = { s:{e:[] for e in etiologies} for s in maxcounts.keys() }
    for (sid,meta) in dist_sid2meta.items():
        if sid not in sapc1_sid2split:
            if meta[0] not in maxcounts:
                sapc2_meta2sid[meta].add(sid)
            else:
                avail[meta[0]][meta[1]].append(sid)
            
    # 3. There must be at most 875 in train and 124 in dev, including the maximum
    # possible number from the minimum group.
    for (split,mc) in maxcounts.items():
        #  Sort (count,etiology) pairs in order of increasing count
        len2e = sorted([(len(sapc2_meta2sid[(split,e)]),e) for e in etiologies])
        #  While the total length less than the maxcount
        while sum([p[0] for p in len2e]) < mc:
            # Find the smallest count for which availability is not zero
            while len(avail[split][len2e[0][1]]) == 0:
                len2e = len2e[1:]
            # Get a speaker from that etiology, then re-sort len2e
            sapc2_meta2sid[(split,len2e[0][1])].add(avail[split][len2e[0][1]].pop())
            len2e = sorted([(len(sapc2_meta2sid[(split,e)]),e) for e in etiologies])
            
    # 4. From the speakers in SAPC2 test1 and test2, the test utterances
    # will include only utterances whose text transcription is not identical to
    # any utterance spoken by a speaker in the SAPC2 or distributed train or dev.
    sapc2_traintrans = set()
    for (fid,trans) in dist_fid2trans.items():
        sid = reader.fid2sid(fid)
        meta = dist_sid2meta[sid]
        for split in ['train','dev']:
            if sid in sapc2_meta2sid[(split,meta[1])]:
                sapc2_fid2meta[fid] = (split,meta[1])
            if sid in sapc2_meta2sid[(split,meta[1])] or meta[0]==split:                
                sapc2_traintrans.add(trans)

    for (fid,trans) in dist_fid2trans.items():
        sid = reader.fid2sid(fid)
        meta = dist_sid2meta[sid]
        for split in ['test1','test2']:
            if sid in sapc2_meta2sid[(split,meta[1])] and trans not in sapc2_traintrans:
                sapc2_fid2meta[fid] = (split,meta[1])

    reader.write_sapc2(sapc2_fid2meta, out_dir, splits)
            
        
    
                
########################################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
        Generate train, dev, test1 and test2 file listings for the second Speech
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

