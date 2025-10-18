import re

def cache_num(match):
    number = match.group(3)
    number = re.sub(r'\s', '', number)
    number = re.sub(r'\.', '_', number)
    return f'|{number}|\n'

def raw2cleaned(filelist):
    for file in filelist:
        with open('raw/' + file, 'r') as f:
            text = f.read()
        cleaned = re.sub(r'[^\u0900-\u0970\s.]', '', text)
        cleaned = re.sub(r'।\s*।', '॥', cleaned)
        cleaned = re.sub(r'(([॥।])([०१२३४५६७८९\s.]*)\2)', cache_num, cleaned)
        cleaned = re.sub(r'यथा\s*', 'यथा\n', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'(छंदोनुशासन|छन्दोऽनुशासनम्)[।\s]+', '', cleaned, flags=re.DOTALL)
        cleaned = cleaned\
            .replace('॥', '॥\n')\
            .replace('।', '।\n')\
            .replace('|', '॥')\
            .replace('.', '')\
            .replace('_', '.')
        cleaned = re.sub(r'(\n\s*)+', '\n', cleaned)
        with open('cleaned/' + file, 'w') as f:
            f.write(cleaned)

def extract_ch2(filelist):
    for file in filelist:
        with open('cleaned/' + file, 'r') as f:
            text = f.read()
        start = 'उक्तायां गः श्रीः'
        end = 'दण्डकप्रकरणम्'
        ch2 = text[text.find(start): text.find(end) + 16]
        with open('ch2/' + file, 'w') as f:
            f.write(ch2)

if __name__ == '__main__':
    filelist = ['sq.txt', 'si.txt', 'ch.txt']
    raw2cleaned(filelist)
    extract_ch2(filelist)
