import re
import json
from collections import Counter
from itertools import product

with open('GL.json', 'r') as f:
    GL = json.load(f)

D = {}
for i in GL:
    n = int(GL[i]['len'])
    patterns = Counter(GL[i]['pattern'][:2] + GL[i]['pattern'][2:4] * 2 + GL[i]['pattern'][4:] * 3)

    # Cleaning
    to_remove = {'', None}
    for j in patterns:
        if (j is not None and len(j) != n):
            to_remove.add(j)
    if not all('?' in j for j in set(patterns) - to_remove):
        for j in patterns:
            if '?' in j:
                to_remove.add(j)
    for j in iter(to_remove):
        patterns.pop(j, None)

    # Determination of correct pattern
    if not patterns:
        continue
    elif len(patterns) == 1:
        pattern = list(patterns.keys())[0]
    elif patterns.most_common(1)[0][1] >= patterns.total() / 2:
        pattern = patterns.most_common(1)[0][0]
    assert len(pattern) == n

    D[i] = ([pattern, min(GL[i]['name'], key=len), max(GL[i]['yati'], key=len)])

# Manual edits

# Name and yati edits
D['9'][1] = 'दुःख'
D['21'][1] = 'सुमति'
D['25'][1] = 'पङ्क्ति'
D['30'][1] = 'सावित्री'
D['31'][1] = 'घनपङ्क्ति'
D['33'][1] = 'सावित्री'
D['37'][1] = 'गुरुमध्या'
D['53'][1] = 'उष्णिक्'
D['61'][1] = 'सरल'
D['68'][1] = 'कुमुद्वती'
D['73'][1] = 'अनुष्टुप्'
D['74'][1] = 'विद्युन्माला'
D['74'][2] = [4]
if '87' in D: D.pop('87')
D['108'][1] = 'पङ्क्तिका'
if '156' in D: D.pop('156')
if '157' in D: D.pop('157')
D['170'][1] = 'भुजङ्गप्रयात'
D['172'][1] = 'मौक्तिकदाम'
D['175'][1] = 'ललिता'
D['192'][1] = 'ह्री'
D['206'][1] = 'मञ्जुभाषिणी'
D['216'][1] = 'कोद्दुम्भ'
D['238'][1] = 'इन्दुवदना'
D['240'][1] = 'शरभा'
D['247'][1] = 'चन्द्रोद्योत'
D['250'][1] = 'चन्द्रलेखा'
D['251'][1] = 'चन्द्रलेखा'
D['257'][1] = 'गौ'
D['299'][1] = 'वाणिनी'
D['303'][1] = 'चित्रलेखा'
D['314'][1] = 'निशा'
D['316'][1] = 'सुरभि'
D['320'][1] = 'बुद्बुद'
D['346'][1] = 'कथागति'
D['358'][1] = 'अश्वललित'
D['361'][1] = 'हंसगति'
D['362'][1] = 'चित्रक'
D['366'][1] = 'ललितलता'
D['367'][1] = 'मेघमाला'
D['380'][1] = 'सुधाकलश'
D['384'][1] = 'ललितलता'
D['384'][2] = [10]*3
if '386' in D: D.pop('386')

# Vitan (87)
anustup = [pat for pat, name, yati in D.values() if len(pat) == 8]
vitan = [''.join(pat) for pat in product('GL', repeat=7)]
for i, pat in enumerate(vitan):
    if pat + 'G' not in anustup and any(pattern.startswith(pat + 'G') for pattern, name, yati in D.values()):
        D[f'87_{i}'] = [pat + 'G', 'वितान', []]

# Pipilika additions (386)
names = ['करभ', 'पणव', 'माला']
for i in range(len(names)):
    D[f'386_{i}'] = [D['385'][0][:22] + 'L' * (5*(i+1)) + D['385'][0][22:], names[i], [8, 15 + 5*(i+1)]]

# Chandavrushti additions (388)
names = ['अर्ण', 'अर्णव', 'व्याल', 'जीमूत', 'लीलाकर', 'उद्दाम', 'शङ्ख', 'समुद्र', 'भुजंग']
for i in range(len(names)):
    D[f'388_{i}'] = [D['387'][0] + 'GLG' * (i+1), names[i], []]

# Prachit etc (389)
names = ['प्रचित', 'अर्ण', 'अर्णव', 'व्याल', 'जीमूत', 'लीलाकर', 'उद्दाम', 'शङ्ख', 'समुद्र', 'भुजंग']
for i in range(len(names)):
    for j in ['LGG', 'GGG', 'GGL', 'LGG', 'GLL']:
        D[f'389_{i}_{j}'] = ['LLLLLL' + j * (i+7), names[i], []]

# Pannag etc (390)
names = ['पन्नग', 'दम्भोलि', 'हेलावली', 'मालती', 'केलि', 'कङ्केल्लि', 'लीलाविलास']
for i in range(len(names)):
    D[f'390_{i}'] = ['LLLG' + 'GLG' * (i+8), names[i], []]

# Chandakaal (391)
for i in range(7): # This can be replaced by any number
    D[f'391_{i}'] = ['LLLLL' + 'GLG' * (i+8), 'चण्डकाल', []]

# Simhavikrant (392)
for i in range(7): # This can be replaced by any number
    D[f'392_{i}'] = ['LLLLL' + 'LGG' * (i+8), 'सिंहविक्रान्त', []]

# Meghmala (393)
for i in range(6): # This can be replaced by any number
    D[f'393_{i}'] = ['LLLLLLGGG' + 'LGG' * (i+6), 'मेघमाला', []]

# Mattamaatang etc (394 - 400)
names = [D[str(i)][1] for i in range(394, 401)]
gana = ['GLG', 'LLG', 'LGG', 'LG', 'GL', 'GGL', 'GLL']
for i in range(len(names)):
    repeat = 14 if len(gana[i]) == 2 else 9
    for j in range(7): # This can be replaced by any number
        pattern = gana[i] * (j+repeat)
        if gana[i] in ['GGL', 'GLL']:
            pattern += 'GG'
        D[f'{i+394}_{j}'] = [pattern, names[i], []]

for i in range(388, 402):
    if str(i) in D: D.pop(str(i))

# Renaming corrections
for i in D:
    D[i][1] = re.sub(r'ं(?=[क-ङ])', 'ङ्', D[i][1])
    D[i][1] = re.sub(r'ं(?=[च-ञ])', 'ञ्', D[i][1])
    D[i][1] = re.sub(r'ं(?=[ट-ण])', 'ण्', D[i][1])
    D[i][1] = re.sub(r'ं(?=[त-न])', 'न्', D[i][1])
    D[i][1] = re.sub(r'ं(?=[प-म])', 'म्', D[i][1])
for i in D:
    if int(i.split('_')[0]) > 386:
        D[i][1] += ' दण्डक'

data = {}
for pat, name, yati in D.values():
    current = data
    for j in pat:
        if not current.get(j):
            current[j] = {}
        current = current[j]
    current['name'] = name
    if yati:
        current['yati'] = yati

with open('docs/data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False)
