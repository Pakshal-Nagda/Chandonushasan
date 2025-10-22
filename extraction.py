import re

gana_to_GL = {
        'य': 'LGG',
        'म': 'GGG',
        'त': 'GGL',
        'र': 'GLG',
        'ज': 'LGL',
        'भ': 'GLL',
        'न': 'LLL',
        'स': 'LLG',
        'ल': 'L',
        'ग': 'G'
    }

def sutra_to_pattern(sutra):
    sutra = re.sub('([यमतरजभनसलग])्([यमतरजभनसलग])ौ', lambda x: x.group(1) + x.group(2), sutra)
    sutra = re.sub('([यमतरजभनसलग])ौ', lambda x: x.group(1) * 2, sutra)
    sutra = re.sub('[ो्ंः ]', '', sutra)
    sutra = sutra.strip('ा')
    pattern = ''
    for i in range(len(sutra)-1):
        if sutra[i] in 'ािीुूृॄेैोौॢॣद':
            continue
        elif sutra[i+1] == 'ा':
            n = 2
        elif sutra[i+1] == 'ि':
            n = 3
        elif sutra[i+1] == 'ी':
            n = 4
        elif sutra[i+1] == 'ु':
            n = 5
        elif sutra[i+1] == 'ू':
            n = 6
        elif sutra[i+1] == 'ृ':
            n = 7
        elif sutra[i+1] == 'ॄ':
            n = 8
        elif sutra[i+1] == 'ॢ':
            n = 9
        elif sutra[i+1] == 'ॣ':
            n = 10
        else:
            n = 1
        pattern += gana_to_GL[sutra[i]] * n
    pattern += gana_to_GL.get(sutra[-1], '')
    return pattern

def example_to_pattern(example, n):
    lines = [line.strip(' ॥।') for line in example.split('\n')]
    non_dev_re = re.compile(r"[^अ-औक-हा-्ॠॡॢॣंः]")
    syllable_re = re.compile(r"((([क-ह]्)*[क-ह][ा-ॄॢॣेैोौ]?|[अ-ऌॠॡएऐओऔ])[ंः]?([क-ह]्)?)")
    is_G_re = re.compile(r"[ाीूॄॣेैोौ्]$|[ंः]$|[आईऊॠॡएऐओऔ]")
    pattern = ''
    for line in lines:
        line = non_dev_re.sub('', line)
        syllables = [m.group(1) for m in syllable_re.finditer(line)]
        for syll in syllables:
            if is_G_re.search(syll):
                pattern += 'G'
            else:
                pattern += 'L'
    if len(pattern) == 4*n:
        patterns 
    if len(patterns) == 2:
        new_pat = []
        for pat in patterns:
            new_pat.append(pat[:len(pat)//2])
            new_pat.append(pat[len(pat)//2:])
        patterns = new_pat
    elif len(patterns) != 4:
        j = ''.join(patterns)
        n = len(j)
        patterns = [j[:n//4], j[n//4:n//2], j[n//2:3*n//4], j[3*n//4:]]
    pat_dict = {}
    for p in patterns:
        if p not in pat_dict:
            pat_dict[p] = 1
        else:
            pat_dict[p] += 1
    return max(pat_dict, key=lambda x: pat_dict[x])

if __name__ == '__main__':

    # Extracting evidences (sutra, pattern, example) from text (sq.txt and si.txt)
    evidences = {i: [] for i in range(6, 402)}
    for i in range(6, 402):
        with open('ch2/sq.txt', 'r') as f:
            sq = f.read()
        with open('ch2/si.txt', 'r') as f:
            si = f.read()
        sutra_re = fr'^.*?(?=\s*॥{i}॥$)'
        sutra2_re = fr'(?<=॥{i-1}\.\d॥\n)\D*?(?=[॥।]\n)'
        pattern_re = fr'(?<=॥{i}॥\n)\D*?(?=\n?यथा)'
        ex_re = fr'(?<=[॥।]\nयथा\n)\D*?(?=\s*॥{i}.1॥)'
        ex2_re = fr'(?<=॥{i}॥\n)\D*?(?=\s*॥{i}.1॥)'
        ex3_re = fr'(?<=[॥।]\nयथा\n)\D*(?=\n\D*?॥{i+1}॥)'

        for file in [sq, si]:
            match = re.search(sutra_re, file, re.MULTILINE) or re.search(sutra2_re, file)
            match = match.group() if match is not None else None
            evidences[i].append(match)

        for file in [sq, si]:
            match = re.search(pattern_re, file, re.DOTALL)
            match = match.group() if match is not None else None
            evidences[i].append(match)

        for file in [sq, si]:
            match = re.search(ex_re, file, re.DOTALL) or re.search(ex2_re, file, re.DOTALL) or re.search(ex3_re, file, re.DOTALL)
            match = match.group() if match is not None else None
            evidences[i].append(match)

    # Finding sutra indices where number of syllables change
    sutra_changes = []
    for i in evidences:
        if re.search(jaati_re, evidences[i][0]) or re.search(jaati_re, evidences[i][1]):
            sutra_changes.append(i)

    ## Preliminary sanity check tests
    #for file in ['sq.txt', 'si.txt']:
    #    with open('ch2/' + file, 'r') as f:
    #        text = f.read()

        #for i in range(6, 402):
        #    if f'॥{i}.1॥' not in text:
        #        print(i)

        #matches = re.findall(r'.*?\nयथा\n.*?॥\d+\.1॥', text, re.DOTALL)
        #print(len(matches))
        #for match in matches:
        #    if not re.search(r'॥(\d*)॥.*?\nयथा\n.*?॥\1\.1॥', match, re.DOTALL):
        #        print(match)
        #        print()

        #max = 6
        #print( re.findall(r'\d+\.?\d*', text))
        #for i in re.finditer(r'\d+\.?\d*', text):
        #    if max + 3 > float(i.group()) >= max: max = float(i.group()); #print(i, 'pass')
        #    else: print(text[i.span()[0]:i.span()[1]])

    ## Checking for errors
    #from jarowinkler import jarowinkler_similarity
    #for i in evidences:
    #    if (s := jarowinkler_similarity(evidences[i][0], evidences[i][1])) < 0.8:
    #        print(i, s)
    #        print(evidences[i][:2])
    #for i in evidences:
    #    if (s := jarowinkler_similarity(evidences[i][2], evidences[i][3])) < 0.8:
    #        print(i, s)
    #        print(evidences[i][2:4])
    #for i in evidences:
    #    if (s := jarowinkler_similarity(evidences[i][4], evidences[i][5])) < 0.8:
    #        print(i, s)
    #        print(evidences[i][4:])
