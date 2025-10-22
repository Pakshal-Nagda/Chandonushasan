import re

def cache_num(match):
    number = match.group(2)
    number = re.sub(r'\s', '', number)
    number = number\
        .replace('.', '_')\
        .replace('०', '0')\
        .replace('१', '1')\
        .replace('२', '2')\
        .replace('३', '3')\
        .replace('४', '4')\
        .replace('५', '5')\
        .replace('६', '6')\
        .replace('७', '7')\
        .replace('८', '8')\
        .replace('९', '9')
    return f' |{number}|\n'

def raw2cleaned(filelist):
    for file in filelist:
        with open('raw/' + file, 'r') as f:
            text = f.read()
        cleaned = re.sub(r'[-*]{10,}', 'पृष्ठान्तम्॥', text)
        cleaned = re.sub(r'[^\u0900-\u0970\s.]', '', cleaned)
        cleaned = re.sub(r'।\s*।', '॥', cleaned)
        cleaned = re.sub(r'(\s*[॥।]([०१२३४५६७८९\s.]*)[॥।])', cache_num, cleaned)
        cleaned = re.sub(r'(छंदोनुशासन|छन्दोऽनुशासनम्|द्वितीयोऽध्यायः)[।\s]+', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'[.०१२३४५६७८९]', '', cleaned)
        cleaned = cleaned\
            .replace('॥', '॥\n')\
            .replace('।', '।\n')\
            .replace('|', '॥')\
            .replace('_', '.')
        cleaned = re.sub(r'(\n[\d॥।\s.]*)+', '\n', cleaned)
        with open('cleaned/' + file, 'w') as f:
            f.write(cleaned)

def extract_ch2(filelist):
    for file in filelist:
        with open('cleaned/' + file, 'r') as f:
            text = f.read()
        start = 'उक्तायां गः श्रीः'
        end = 'दण्डकप्रकरणम्'
        ch2 = text[text.find(start): text.find(end) + 16]
        ch2 = re.sub(r'\n', ' ', ch2, flags=re.DOTALL)
        ch2 = re.sub(r'(॥[\d.]+॥|[॥।]) ', lambda x: x.group(1) + '\n', ch2)
        ch2 = re.sub(r'(?<=[॥।]\n)\s*यथा\s*', 'यथा\n', ch2, flags=re.DOTALL)
        with open('ch2/' + file, 'w') as f:
            f.write(ch2)

def renumber(filelist):
    for file in filelist:
        with open('ch2/' + file, 'r') as f:
            text = f.read()

        max_num = 6
        buffer = None
        corrections = []
        for match in re.finditer(r'[\d.]+', text):
            try:
                number = float(match.group())
            except:
                number = -1
            if max_num <= number < max_num + 3:
                if buffer:
                    prev, next = max_num, number
                    if prev % 1 == 0 and next == prev + 1:
                        correction = f'{int(prev)}.1'
                    elif next % 1 == 0 and int(next) == int(prev) + 1:
                        correction = f'{int(prev)}.1'
                    elif int(next) == int(prev) + 1:
                        correction = f'{int(next)}'
                    elif int(next) == int(prev) + 2:
                        correction = f'{int(prev) + 1}'
                    else:
                        correction = '?'
                    corrections.append((buffer, correction))
                    buffer = None
                max_num = number
            else:
                buffer = match

        diff = 0
        for match, correct in corrections:
            start, end = match.span()
            start += diff
            end += diff
            diff += len(correct) - (end - start)
            text = text[:start] + correct + text[end:]

        with open('ch2/' + file, 'w') as f:
            f.write(text)

if __name__ == '__main__':
    filelist = ['sq.txt', 'si.txt', 'ch.txt']
    raw2cleaned(filelist)
    extract_ch2(filelist)
    renumber(filelist[:-1])
