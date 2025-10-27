import re
from extraction_verse import verse_to_GL
from extraction_sutra import sutra_to_GL
from extraction_pattern import pattern_to_GL

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

    jaati = r'((उ|अत्यु)क्ताया|मध्याया|(सु)?प्रतिष्ठाया|गायत्र्या|उष्णिहि|(अनु|त्रि)ष्टुभि|बृहत्या|प(ङ्क्तौ|क्को|तौ)|(अति)?जगत्या|(अति)?शक्वर्या|अ(त्य)?ष्टौ|(अति)?धृत्या|(प्र|आ|वि|सं|अभि|उत्)?कृतौ)ं?'

    # Finding sutra indices where number of syllables change
    sutra_changes = []
    for i in evidences:
        if re.search(jaati, evidences[i][0]) or re.search(jaati, evidences[i][1]):
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
    
    ## Testing verse_to_GL()
    #n = 0
    #for i in evidences:
    #    if i in sutra_changes:
    #        n += 1
    #    if verse := evidences[i][4]:
    #        pattern, split, score = verse_to_GL(verse, n)
    #        if not isinstance(pattern, str):
    #            print(i, verse, pattern, score)
    #    if verse := evidences[i][5]:
    #        pattern, split, score = verse_to_GL(verse, n)
    #        if not isinstance(pattern, str):
    #            print(i, verse, pattern, score)

    ## Testing sutra_to_GL()
    #n = 0
    #k = 0
    #for i in evidences:
    #    if i in sutra_changes:
    #        n += 1
    #    if sutra := evidences[i][0]:
    #        #print(i, sutra)
    #        if GL := sutra_to_GL(sutra):
    #            if len(GL[1]) == n:
    #                print(i, GL)
    #                k+=1
    #    if sutra := evidences[i][1]:
    #        #print(i, sutra)
    #        if GL := sutra_to_GL(sutra):
    #            if len(GL[1]) == n:
    #                print(i, GL)
    #                k+=1
    #print(k)

    for i in evidences:
        if evidences[i][2]:
            #print(i, evidences[i][0], '\n', evidences[i][2], '\n')
            pattern_to_GL(evidences[i][2])
        if evidences[i][3]:
            #print(i, evidences[i][0], '\n', evidences[i][3], '\n')
            pattern_to_GL(evidences[i][3])
