import os, os.path, json, glob, argparse, sys
"""
This script is designed to create the train/dev/test1/test2 splits
for the second Speech Accessibility Project Challenge
based on the 2025-08-31 SAP partner distribution.

It's designed to satisfy a few constraints:

1. All speakers that were part of any split in SAPC1 must be placed in the 
train or dev splits of SAPC2.  This permits us to release all of those
files, so that people who want to re-run all of the tests from SAPC1 on 
their own can freely do so using only the manifests.

2. Any speaker that was in the train or dev splits of any research
distribution cannot be part of the test1 or test2 splits for SAPC2.
Instead, the train and dev splits of SAPC2 will include data from the
train and dev splits of the 2025-08-31 partner distribution,
up to a maximum total of 999 distributed speakers,
with the number of speakers per etiology chosen in order to maximize
the smallest etiology in both train and dev, and chosen so that there
are 777 speakers in train and 222 speakers in dev.

3. From the speakers in SAPC test1 and test2, the test utterances
will include only utterances whose text transcription is not identical to
any utterance spoken by a speaker in any train or dev distribution.
Other utterances of these speakers will be sequestered (will not be part of
train, dev, test1 or test2).  These will be mostly spontaneous utterances,
but not all.
"""



#####################################################################################
def main(sapc1_dir, distrib_dir, output.dir):
    # First: Read all data from SAPC1, get list of speaker IDs
    subsets = ['Dev', 'Test1', 'Test2', 'Train']
    sapc1_speakers = { subset.lower():set() for subset in subsets }
    for subset in subsets:
        with open(os.path.join(sapc1_dir, subset.lower()+'.tsv')) as tsvfp:
            for line in tsvfp:
                utt_filename = os.path.basename(line)
                speaker_id = utt_filename[0:utt_filename.find("_")]
                sapc1_speakers[subset].add(speaker_id)
    
    # Second: load necessary info from the 2025-08-31 partner distribution
    distrib_speakers = { subset.lower():{} for subset in subsets }
    distrib_transcripts = {}
    for subset in subsets:
        jsonpathnames = glob.glob(os.path.join(distrib_dir,subset,"*.json"))
        for x in jsonpathnames:
            spkr_id = os.path.splitext(os.path.basename(x))[0]
            with open(x) as ifp:
                data = json.load(ifp)
                # 1. Read in the etiology of the speaker
                if 'Etiology' not in data:
                    raise RuntimeError(subset+'/'+spkr_id+' has no Etiology')
                distrib_speakers[subset.lower()][spkr_id] = data['Etiology']

                # 2. Read in the text transcript of each utterance
                for wavfile in data['Files']:
                    if 'Prompt' not in wavfile or 'Transcript' not in wavefile['Prompt']:
                        raise RuntimeError(subset+'/'+wavfile['Filename']+' has no Transcript')
                    distrib_transcripts[spkr_id] = wavfile['Prompt']['Transcript']

    # Third: count up the number of speakers of each etiology in SAPC1,
    # and allocate them to train and dev of the new challenge

    # Fourth: Allocate speakers from the new distribution to challenge splits:
    # train+dev = maximize the minimum etiology up to 999 total, including all SAPC1 speakers
    # test1+test2 = all test1+test2 speakers in distribution who were not part of SAPC1

    # Fifth: Find the waveforms from each of the test speakers whose transcripts
    # don't exist for any train or dev speaker in the distribution or in the challenge
                
########################################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
        Generate train, dev, test1 and test2 file listings for the second Speech
        Accessibility Project Challenge.

        USAGE: python %s sapc1_dir distrib_dir output_dir

        distribution = 
        output_dir = directory in which to write {dev,test1,test2,train}.txt listing files
        """%(sys.argv[0]),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'sapc1_dir',action='store',
        help='Directory containing {dev,test1,test2,train}.tsv for SAP challenge 1'
        )
    parser.add_argument(
        'distrib_dir',action='store',
        help="""
        directory containing distribution with Train, Dev, Test1, Test2
        subdirectories, each containing one json file per speaker, 
        specifying speaker etiology, utterance filenames, utterance transcripts.
        """
    )
    parser.add_argument(
        'output_dir',action='store',
        help="Directory in which to put {dev,test1,test2,train}.txt files"
    )
    args = parser.parse_args()
    main(args.sapc1_dir, args.distrib_dir, args.output_dir)

