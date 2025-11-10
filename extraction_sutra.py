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

jaati = r'(((उ|अत्यु)क्ताया|मध्याया|(सु)?प्रतिष्ठाया|गायत्र्या|उष्णिहि|(अनु|त्रि)ष्टुभि|बृहत्या|प(ङ्क्तौ|क्को|तौ)|(अति)?जगत्या|(अति)?शक्वर्या|अ(त्य)?ष्टौ|(अति)?धृत्या|(प्र|आ|वि|सं|अभि|उत्)?कृतौ|शेषजात.)ं?)'
visarga = r'(ः\s+|(ो|(?<=ा))\s+(?=[गघजझड-णद-नब-मयरलवह])|\s*श्(?=[चछश])|\s*ष्(?=[टठष])|\s*स्(?=[तथ])|(?<=[िीुू])\s*(ः|र्\s*)|\s+(?=[आ-औ])|(?<=ा)\s+(?=[अ-औ]))'
au = r'(ौ\s+|ाव)'
gana = r'[यमतरजभनसलग]'
g1 = fr'{gana}[िीुूृॄॢॣ]?{visarga}'
g2 = fr'({gana}[िीुूृॄॢॣ्\s]?)?{gana}{au}'
gn = fr'({gana}[िीुूृॄॢॣ्\s]?){{,6}}{gana}ा{visarga}'
gm = fr'{gana}[िीुूृॄॢॣ]\s*'
y = r'([ग-ह]+ैः)'

def extract_name(sutra):
    if (match := re.search(fr'(?P<name>\S+)(\s+{y})?$', sutra)):
        name = match.group('name')
        name = re.sub(r'\s', '', name)
        name = re.sub(r'(ं|ै?ः|[मशषस]्)$', '', name)
        name = name.rstrip('अआइईउऊऋॠऌॡएऐओऔेैोौंः')
        name = re.sub(r'^(.्.ो(?=.[^्])|[यग]ो)', '', name)
        return name

def sutra_to_pattern(sutra):
    match = re.match(fr'^{jaati}?\s*(?P<pattern>({g1}|{g2}|{gn}|{gm})*({g1}|{g2}|{gn}))(?P<name>.+)$', sutra)
    if match:
        pattern, name = match.group('pattern'), match.group('name')

        # Handling vriddhi sandhi of au
        if pattern.endswith('ाव'):
            if re.match(r'^[क-ह]', name): name = 'अ' + name
            elif re.match(r'^ा', name): name = 'आ' + name[1:]
            elif re.match(r'^ि', name): name = 'इ' + name[1:]
            elif re.match(r'^ी', name): name = 'ई' + name[1:]
            elif re.match(r'^[ु॑]', name): name = 'उ' + name[1:]
            elif re.match(r'^ू', name): name = 'ऊ' + name[1:]
            elif re.match(r'^े', name): name = 'ए' + name[1:]
            pattern = pattern[:-2] + 'ौ'

        # Handling accidental breaks of name
        elif re.match(r'^[ा-ौ्]', name):
            idx = pattern.find(' ')
            name = pattern[idx:] + name
            pattern = pattern[:idx]

        # Finding yati
        if yati := re.search(fr'{y}$', name):
            yati = yati.group()
            name = name[:-len(yati)]

        # Cleaning visarga sandhis and spaces
        extracted = [pattern, name, yati]
        for i in range(len(extracted)):
            if not extracted[i]:
                continue
            element = re.sub(r'\s', '', extracted[i])
            element = re.sub(r'(ं|ै?ः|[मशषस]्)$', '', element)
            if i == 1:
                element = element.rstrip('अआइईउऊऋॠऌॡएऐओऔेैोौंः')
                element = re.sub(r'^(.्.ो(?=.[^्])|[यग]ो)', '', element)
            extracted[i] = element
        
        # Fallback for name extraction
        if extracted[1] == '':
            extracted[1] = extract_name(sutra)

        return extracted

    else:
        return ['', extract_name(sutra), None]

def decode_yati(yati):
    key = '_कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह'
    return [key.index(i) for i in yati]

def pattern_to_GL(pattern):
    pattern = re.sub('([यमतरजभनसलग])्?([यमतरजभनसलग])ौ', lambda x: x.group(1) + x.group(2), pattern)
    pattern = re.sub('([यमतरजभनसलग])ौ', lambda x: x.group(1) * 2, pattern)
    pattern = re.sub('[ाो्ंः ]', '', pattern)
    GL = ''
    for i in range(len(pattern)-1):
        if pattern[i] in 'ािीुूृॄेैोौॢॣद':
            continue
        elif pattern[i+1] == 'ा':
            k = 2
        elif pattern[i+1] == 'ि':
            k = 3
        elif pattern[i+1] == 'ी':
            k = 4
        elif pattern[i+1] == 'ु':
            k = 5
        elif pattern[i+1] == 'ू':
            k = 6
        elif pattern[i+1] == 'ृ':
            k = 7
        elif pattern[i+1] == 'ॄ':
            k = 8
        elif pattern[i+1] == 'ॢ':
            k = 9
        elif pattern[i+1] == 'ॣ':
            k = 10
        else:
            k = 1
        GL += gana_to_GL[pattern[i]] * k
    GL += gana_to_GL.get(pattern[-1], '')
    return GL

def sutra_to_GL(sutra):
    pattern, name, yati = sutra_to_pattern(sutra)
    yati = decode_yati(yati) if yati else []
    GL = pattern_to_GL(pattern) if pattern else ''
    return name, GL, yati
