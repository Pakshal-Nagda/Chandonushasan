import re
from extraction_verse import verse_to_GL

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

def sutra_to_GL(sutra, n):
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

def pattern_to_GL(pattern, n):
    candidates = []
    candidates += re.findall(r'(([यमतरजभनस]\s*(गण[ोौ]?\s*))+|([यमतरजभनसलग][िीुूृॄॢॣ]?\s*){3,}ा|[यमतरजभनस]\s*(गण)?\s*(द्वय|त्रय|चतुष्टय|पञ्चक|षट्क|सप्तक|ाष्टकम्)ं?\s*[यमतरजभनस]ो)\s*((गुरु|लघु)\s*(गुरू|लघू|द्वय)?)?')
    candidates += re.findall(r'(([यमतरजभनस]\s*(गण[ोौ]?\s*))+|([यमतरजभनसलग][िीुूृॄॢॣ]?\s*){3,}ा|[यमतरजभनस]\s*(गण)?\s*(द्वय|त्रय|चतुष्टय|पञ्चक|षट्क|सप्तक|ाष्टकम्)ं?\s*[यमतरजभनस]ो)+\s*((गुरु|लघु)\s*(गुरू|लघू|द्वय)?)?')
    yati = re.findall(r'((त्रि|चतुर्?|पञ्च|षड्?|सप्त|ष्ट[ाे]?|नव|([ेए]का|द्वा|चतुर्|पञ्च)?दश)भि.?\s*).*यति')
    yati = re.findall(r'ैरिति वर्तते')

def example_to_GL(examples, n):
    patterns = []
    for example in examples:
        non_dev_re = re.compile(r"[^अ-औक-हा-्ॠॡॢॣंः]")
        syllable_re = re.compile(r"((([क-ह]्)*[क-ह][ा-ॄॢॣेैोौ]?|[अ-ऌॠॡएऐओऔ])[ंः]?([क-ह]्)?)")
        is_G_re = re.compile(r"[ाीूॄॣेैोौ्]$|[ंः]$|[आईऊॠॡएऐओऔ]")
        pattern = []
        example = non_dev_re.sub('', example)
        syllables = [m.group(1) for m in syllable_re.finditer(example)]
        for syll in syllables:
            if is_G_re.search(syll):
                pattern.append('G')
            else:
                pattern.append('L')
        if len(pattern) == 4*n and ('G' in (pattern[n//4 - 1] + pattern[n//2 - 1] + pattern[3*n//4 - 1] + pattern[n - 1])):
            pattern[n//4 - 1] = pattern[n//2 - 1] = pattern[3*n//4 - 1] = pattern[n - 1] = 'G'
        pattern = ''.join(pattern)
        D = {pattern[i:i+n]: pattern.count(pattern[i:i+n]) for i in range(len(pattern) - n + 1)}
        patterns.append(D)

    D = {}
    for pattern in patterns:
        for i in pattern:
            if i in D:
                D[i] += pattern[i]
            else:
                D[i] = pattern[i]

    most_freq = 0
    multi_max = False
    for j in D:
        if D[j] > most_freq:
            most_freq = D[j]
            multi_max = False
        elif D[j] == most_freq:
            multi_max = True
    if multi_max:
        pass#print(examples, patterns)
    return max(D, key=lambda x: D[x])

def edit_distance(s1, s2):
    # Standard edit distance DP (Levenshtein)
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[m][n]

def all_smart_splits(L, pieces=4):
    # Generate all splits of L into 'pieces' segments with length >=1 for each piece
    # Returns a list of tuples, e.g. (len1, len2, len3, len4)
    def helper(so_far, left, depth):
        if depth == pieces-1:
            if left >= 1:
                yield tuple(so_far + [left])
            return
        for x in range(1, left-(pieces-depth-1)+1):
            yield from helper(so_far + [x], left-x, depth+1)
    return list(helper([], L, 0))

def consensus_pattern(parts):
    # For a given list of 4 string segments, compute consensus (majority at each position)
    pattern_length = min(len(p) for p in parts)
    consensus = ''
    for i in range(pattern_length):
        counts = {'G':0, 'L':0}
        for p in parts:
            if i < len(p):
                counts[p[i]] += 1
        consensus += max(counts, key=counts.get)
    return consensus

def pattern_score(parts, pattern):
    # Score = total edit distance from each part to the consensus pattern (truncated to each part's length)
    return sum(edit_distance(part, pattern[:len(part)]) for part in parts)

def find_best_pattern(s):
    L = len(s)
    best_score = float('inf')
    best_pattern = ''
    best_split = ()
    for split in all_smart_splits(L, pieces=4):
        # Partition input string
        indices = [0]
        for l in split:
            indices.append(indices[-1]+l)
        parts = [s[indices[i]:indices[i+1]] for i in range(4)]
        # Compute consensus and edit cost
        pattern = consensus_pattern(parts)
        score = pattern_score(parts, pattern)
        if score < best_score:
            best_score = score
            best_pattern = pattern
            best_split = split
    return best_pattern, best_split, best_score

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

    jaati_re = r'((उ|अत्यु)क्ताया|मध्याया|(सु)?प्रतिष्ठाया|गायत्र्या|उष्णिहि|(अनु|त्रि)ष्टुभि|बृहत्या|प(ङ्क्तौ|क्को|तौ)|(अति)?जगत्या|(अति)?शक्वर्या|अ(त्य)?ष्टौ|(अति)?धृत्या|(प्र|आ|वि|सं|अभि|उत्)?कृतौ)ं?'
    gana = '[यमतरजभनस]'
    ganagl = '[यमतरजभनसलग]'
    yati = '[ग-ण]+ैः'
    g1 = fr'{ganagl}([ोः]|[िीुूृॄॢॣ](ः|र्)|(?=\s*[अआइईउऊऋॠऌॡएऐओऔ])|श्(?=[चछ])|ष्(?=[टठ])|स्(?=[तथ]))'
    g2 = fr'({ganagl}[ािीुूृॄॢॣ्]?)?{ganagl}([ौ]|ा(?=व))'
    g3 = fr'({ganagl}्?{ganagl}{ganagl}|{ganagl}[ािीुूृॄॢॣ्]?{ganagl}्{ganagl})ाः?'

    # Finding sutra indices where number of syllables change
    sutra_changes = []
    for i in evidences:
        if re.search(jaati_re, evidences[i][0]) or re.search(jaati_re, evidences[i][1]):
            sutra_changes.append(i)

    # Extracting patterns and scoring them
    patterns = []
    scores = []
    for i in evidences:
        pass

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
    
    # Testing example_to_pattern()
    n = 0
    for i in evidences:
        if i in sutra_changes:
            n += 1
        if verse := evidences[i][4]:
            pattern, split, score = verse_to_GL(verse, n)
            if not isinstance(pattern, str):
                print(i, verse, pattern, score)
        if verse := evidences[i][5]:
            pattern, split, score = verse_to_GL(verse, n)
            if not isinstance(pattern, str):
                print(i, verse, pattern, score)
