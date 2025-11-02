import re

gana = r'(गुर[ुू]|लघ[ुू]|[यमतरजभनस](?=(?:ं?गं?ण|श्च))|[यमतरजभनसलग]{2}(?=ौ)|[यमतरजभनसलग]{3,}(?=ाः?|ेभ्यः)|(?:[लग]्?)?[लग][ौः]|[यमतरजभनसलग]?(?:द्व(?:र्)?य|त्रय(?!ोदश)|चतुष्टय|चत्वार|प[ञर]्चक?|षट|सप्तक|ष्टक)(?!भि))'
yati = r'(त्रि|चतुर्?|पञ्च|षड्?|सप्त|ष्ट.?|नव|(?:[ेए]का|द्वा|त्रयो|चतुर्|पञ्च)?दश)भि'

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

def pattern_to_GL(pattern):
    # Pattern handling
    patterns = re.findall(gana, pattern)
    GL = ''

    for i in range(len(patterns)):
        patterns[i] = re.sub(r'द्व(र्)?य', '2', patterns[i])
        patterns[i] = re.sub(r'त्रय', '3', patterns[i])
        patterns[i] = re.sub(r'(चतुष्टय|चत्वार)', '4', patterns[i])
        patterns[i] = re.sub(r'प[ञर]्चक?', '5', patterns[i])
        patterns[i] = re.sub(r'षट', '6', patterns[i])
        patterns[i] = re.sub(r'सप्तक', '7', patterns[i])
        patterns[i] = re.sub(r'ष्टक', '8', patterns[i])

    first = None
    for pat in patterns:
        if re.match(r'^\d$', pat):
            if GL:
                GL += GL[-1] * (int(pat) - 1)
            else:
                first = int(pat)
        else:
            pat = re.sub(r'गुर[ुू]', 'ग', pat)
            pat = re.sub(r'लघ[ुू]', 'ल', pat)
            pat = re.sub(r'[^यमतरजभनसलग\d]', '', pat)
            if first:
                assert len(pat) == 1
                GL += pat * first
                first = None
            else:
                num = re.search(r'\d', pat)
                num = int(num.group()) if num else 1
                GL += re.match(r'^\D+', pat).group() * num
    GL = ''.join(gana_to_GL[i] for i in GL)

    # Yati handling
    if 'यति' in pattern:
        yatis = re.findall(yati, pattern)
        for i in range(len(yatis)):
            if re.match(r'^त्रि$', yatis[i]): yatis[i] = 3
            elif re.match(r'^चतुर्?$', yatis[i]): yatis[i] = 4
            elif re.match(r'^पञ्च$', yatis[i]): yatis[i] = 5
            elif re.match(r'^षड्?$', yatis[i]): yatis[i] = 6
            elif re.match(r'^सप्त$', yatis[i]): yatis[i] = 7
            elif re.match(r'^ष्ट.?$', yatis[i]): yatis[i] = 8
            elif re.match(r'^नव$', yatis[i]): yatis[i] = 9
            elif re.match(r'^दश$', yatis[i]): yatis[i] = 10
            elif re.match(r'^[ेए]कादश$', yatis[i]): yatis[i] = 11
            elif re.match(r'^द्वादश$', yatis[i]): yatis[i] = 12
            elif re.match(r'^त्रयोदश$', yatis[i]): yatis[i] = 13
            elif re.match(r'^चतुर्दश$', yatis[i]): yatis[i] = 14
            elif re.match(r'^पञ्चदश$', yatis[i]): yatis[i] = 15
            else: raise ValueError(yatis[i])
    elif 'ैरिति वर्तते' in pattern:
        yatis = [-1]
    else:
        yatis = []

    return GL, yatis
