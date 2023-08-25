import uuid, random, time, argparse, os, json, string
import promptfiles

def pseudoword():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(2,10)))
                   
def type_dependent_corruption(prompt):
    '''
    @param:
    prompt (list): [category, subcategory, prompttext]

    @return:
    transcript (str): prompttext, corrupted to simulate a human reader's response
    '''
    if prompt[0] == "Spontaneous Speech Prompts":
        # Generate a random sequence of randomly selected characters
        transcript = ' '.join(pseudoword() for j in range(random.randint(10,60)))
        return transcript
    elif random.random() < 0.1:
        words = prompt[2].split()
        if len(words)>2:
            insertion_point = random.randint(1,len(words)-1)
            return ' '.join(words[:insertion_point]+[pseudoword()]+words[insertion_point:])
        else:
            return prompt[2]
    else:
        return prompt[2]
    
def format_prompt(prompt):
    '''
    Format a prompt as a dict.
    
    @param:
    prompt (list): [category, subcategory, prompttext]
    
    @return:
    prompt (dict): with keys as in the SAP data format
    '''
    ret = {
        "Prompt Text" : prompt[2],
        "Transcript" : type_dependent_corruption(prompt),
        "Category Description": prompt[0],        
        "Sub Category Description" : prompt[1]
    }
    return ret

def random_date():
    'Generate a random date in a fixed range using ISO format.'
    time_format = '%Y-%m-%d %H:%M:%S'
    stime = time.mktime(time.strptime('2023-03-01 00:00:00', time_format))
    etime = time.mktime(time.strptime('2024-04-30 23:59:59', time_format))
    return time.strftime(time_format, time.localtime(stime+(etime-stime)*random.random()))

def generate_contributor(contributor_id, listnum, prompts, novel_sentences):
    '''
    Generate dict for one contributor, with random number of completed files.

    @param:
    contributor_id (str): capitalized uuid for this contributor
    listnum (int in [1,10]): prompt list to use
    prompts (dict): as returned by promptfiles.load_PD_prompts()
    novel_sentences (list): as returned by promptfiles.load_PD_prompts()

    @return:
    contributor (dict): in SAP data format
    '''
    contributor = {}
    contributor['Contributor ID'] = contributor_id
    contributor['Can Converse in English'] = random.choice([True,False])
    contributor['Files'] = []
    nblocks = random.randint(0,10)
    for block in range(1,nblocks+1):
        if block < nblocks:
            nprompts = 45
        else:
            nprompts = random.randint(0,45)
        for ind in range(1,nprompts+1):
            file = {}
            i,j = random.randint(10,99), random.randint(1000,9999)
            file["Filename"] = '%s_%d_%d.wav'%(contributor_id.lower(),i,j)
            file["CreatedOrModified"] = random_date()
            file['Comment'] = ''
            if (2 <= block <= 9) and (31 <= ind <= 40):
                file["Prompt"] = format_prompt(novel_sentences[random.randint(0,11999)])
            else:
                file["Prompt"] = format_prompt(prompts[listnum][block][ind])
            contributor['Files'].append(file)
    return contributor

def generate_corpus(ncontributors):
    '''
    Generate a corpus.

    @param:
    ncontributors (int): number of contributors to generate

    @return:
    corpus (dict): corpus[contributor_id] is a contributor dict
    '''
    prompts, novel_sentences = promptfiles.load_PD_prompts()
    corpus = {}
    for i in range(ncontributors):
        listnum = i % 10 + 1
        contributor_id = str(uuid.uuid4()).upper()
        corpus[contributor_id] = generate_contributor(contributor_id, listnum, prompts, novel_sentences)
    return corpus

def main(outputdir):
    corpus = generate_corpus(2000)
    for contributor_id in corpus:
        os.makedirs(os.path.join(outputdir,contributor_id))
        with open(os.path.join(outputdir,contributor_id,contributor_id+'.json'),'w') as f:
            json.dump(corpus[contributor_id], f, indent=2)

################################################################################################
# Command line arguments
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description     = 'Create fake data for testing SAPsplit.py',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('datadir',help = 'Directory containing unsplit dataset')

    args   = parser.parse_args()
    main(args.datadir)
