import re
import json

# Extracting chandas (sutra, pattern, example) from text (sq.txt and si.txt)
chandas = {i: [] for i in range(6, 402)}
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
        chandas[i].append(match)

    for file in [sq, si]:
        match = re.search(pattern_re, file, re.DOTALL)
        match = match.group() if match is not None else None
        chandas[i].append(match)

    for file in [sq, si]:
        match = re.search(ex_re, file, re.DOTALL) or re.search(ex2_re, file, re.DOTALL) or re.search(ex3_re, file, re.DOTALL)
        match = match.group() if match is not None else None
        chandas[i].append(match)

# Save chandas
with open('chandas.json', 'w') as f:
    json.dump(chandas, f, indent=4, ensure_ascii=False)
