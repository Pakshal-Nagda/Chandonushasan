import re
import json
from extraction_verse import verse_to_GL
from extraction_sutra import sutra_to_GL, jaati
from extraction_pattern import pattern_to_GL

# Opening saved chandas
with open('chandas.json', 'r') as f:
    chandas = json.load(f)

# Finding sutra indices where number of syllables change
sutra_changes = []
for i in chandas:
    if re.search(jaati, chandas[i][0]) or re.search(jaati, chandas[i][1]):
        sutra_changes.append(i)

# Extracting metrical data
extracted = {i:{'len': 0, 'name': ['']*2, 'pattern': ['']*6, 'score': [0]*2, 'yati': [[] for _ in range(4)]} for i in chandas}
n = 0
for i in chandas:
    print(i)
    if i in sutra_changes:
        n += 1
        if n > 26:
            n = 0

    if chandas[i][0]:
        extracted[i]['name'][0], extracted[i]['pattern'][0], extracted[i]['yati'][0]  = sutra_to_GL(chandas[i][0])
    if chandas[i][1]:
        if chandas[i][1] == chandas[i][0]:
            extracted[i]['name'][1], extracted[i]['pattern'][1], extracted[i]['yati'][1] = extracted[i]['name'][0], extracted[i]['pattern'][0], extracted[i]['yati'][0]
        else:
            extracted[i]['name'][1], extracted[i]['pattern'][1], extracted[i]['yati'][1]  = sutra_to_GL(chandas[i][1])

    if chandas[i][2]:
        extracted[i]['pattern'][2], extracted[i]['yati'][2] = pattern_to_GL(chandas[i][2])
    if chandas[i][3]:
        if chandas[i][3] == chandas[i][2]:
            extracted[i]['pattern'][3], extracted[i]['yati'][3] = extracted[i]['pattern'][2], extracted[i]['yati'][2]
        else:
            extracted[i]['pattern'][3], extracted[i]['yati'][3] = pattern_to_GL(chandas[i][3])

    if chandas[i][4]:
        extracted[i]['pattern'][4], extracted[i]['score'][0] = verse_to_GL(chandas[i][4], n)
    if chandas[i][5]:
        if chandas[i][5] == chandas[i][4]:
            extracted[i]['pattern'][5], extracted[i]['score'][1] = extracted[i]['pattern'][4], extracted[i]['score'][0]
        else:
            extracted[i]['pattern'][5], extracted[i]['score'][1] = verse_to_GL(chandas[i][5], n)

    extracted[i]['len'] = n or max(len(extracted[i]['pattern'][4]), len(extracted[i]['pattern'][5]))
    
# Post-processing
for i in extracted:
    for j in range(2):
        if extracted[i]['name'][j] == 'वा':
            extracted[i]['name'][j] = extracted[str(int(i)-1)]['name'][j]
        if extracted[i]['yati'][2+j] == [-1]:
            extracted[i]['yati'][2+j] = extracted[str(int(i)-1)]['yati'][2+j]
        if extracted[i]['yati'][j] and any(error := [k for k in extracted[i]['yati'][j] if k >= extracted[i]['len']]):
            for k in error:
                extracted[i]['yati'][j].remove(k)
        if extracted[i]['yati'][2+j] and any(error := [k for k in extracted[i]['yati'][2+j] if k >= extracted[i]['len']]):
            for k in error:
                extracted[i]['yati'][2+j].remove(k)

# Saving data
with open('GL.json', 'w') as f:
    json.dump(extracted, f, indent=4, ensure_ascii=False)
