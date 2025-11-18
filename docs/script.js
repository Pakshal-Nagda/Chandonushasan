let currentRoot = null;
let originalRoot = null;
let svg, g, partition, arc, radius;

// ---------- Initialization ----------
async function init() {
    const response = await fetch('data.json');
    originalRoot = await response.json();

    setupSVG();
    renderSunburst(originalRoot);

    document.getElementById('textInput').addEventListener('input', handleTextInput);
    document.getElementById('scriptDropdown').addEventListener('change', handleTextInput);
    document.getElementById('inputTypeDropdown').addEventListener('change', handleTextInput);
    document.getElementById('maxLength').addEventListener('input', handleMaxLengthChange);
}

function setupSVG() {
    const container = document.getElementById('sunburst');
    const width = container.offsetWidth;
    const height = container.offsetHeight;
    const basePadding = 0;

    radius = Math.min(width / 2, height - basePadding - 20);
    d3.select(container).selectAll('svg').remove();

    svg = d3.select(container).append('svg')
        .attr('width', width)
        .attr('height', height);

    g = svg.append('g')
        .attr('transform', `translate(${width / 2}, ${height - basePadding})`);

    partition = d3.partition().size([Math.PI, radius]);
    arc = d3.arc()
        .startAngle(d => d.x0 - Math.PI / 2)
        .endAngle(d => d.x1 - Math.PI / 2)
        .innerRadius(d => d.y0)
        .outerRadius(d => d.y1);
}

// ---------- Data Conversion ----------
function convertDataToHierarchy(data, key = '') {
    const children = Object.entries(data)
        .filter(([k]) => k !== 'name' && k !== 'yati')
        .map(([k, v]) => convertDataToHierarchy(v, k));
    return children.length
        ? { key, name: data.name || null, yati: data.yati || null, children }
        : { key, name: data.name || null, yati: data.yati || null };
}

function getHierarchy(data) {
    const hierarchy = convertDataToHierarchy(data);
    return d3.hierarchy(hierarchy)
        .sum(d => d.children ? 0 : 1)
        .sort((a, b) => d3.ascending(getPath(a), getPath(b)));
}

function getPath(node) {
    const parts = [];
    while (node.parent) {
        if (node.data.key) parts.unshift(node.data.key);
        node = node.parent;
    }
    return parts.join('');
}

// ---------- Color Helpers ----------
function levenshteinDistance(a, b) {
    const dp = Array.from({ length: a.length + 1 }, (_, i) =>
        Array.from({ length: b.length + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0))
    );
    for (let i = 1; i <= a.length; i++)
        for (let j = 1; j <= b.length; j++)
            dp[i][j] = a[i - 1] === b[j - 1]
                ? dp[i - 1][j - 1]
                : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
    return dp[a.length][b.length];
}

function getColorFromDistance(d, max) {
    if (d === 0) return '#00a000';
    const ratio = Math.min(d / Math.max(max, 1), 1);
    return `rgb(${Math.round(256 * ratio)},0,0)`;
}

function computeFill(d, targetPattern, inputText) {
    if (!d.data.name) return '#ffff00';
    const pattern = getPath(d);
    if (inputText && targetPattern) {
        const dist = levenshteinDistance(pattern, targetPattern);
        return getColorFromDistance(dist, Math.max(pattern.length, targetPattern.length));
    }
    return '#ff0000';
}

// ---------- Script Conversion ----------
function text2GL(text, type, script) {
    if (type !== 'pada') {
        alert('Sorry, this input type is not supported currently.');
        document.getElementById('inputTypeDropdown').value = 'pada'
    }

    if (script === 'GL') return text.replace(/[^GL]/g, '');

    if (script === 'Devanagari') {
        const nonDev = /[^अ-औक-हा-्ॠॡॢॣंः]/g;
        text = text.replace(nonDev, '');

        const subs = ['अ','आ','इ','ई','उ','ऊ','ऋ','ॠ','ऌ','ॡ','ए','ऐ','ओ','औ'];
        const reps = ['','ा','ि','ी','ु','ू','ृ','ॄ','ॢ','ॣ','े','ै','ो','ौ'];
        subs.forEach((s, i) => text = text.replace(new RegExp('्' + s, 'g'), reps[i]));

        const syllableRe = /((([क-ह]्)*[क-ह][ा-ॄॢॣेैोौ]?|[अ-ऌॠॡएऐओऔ])[ंः]?([क-ह]्)?)/g;
        const isGRe = /[ाीूॄॣेैोौ्]$|[ंः]$|[आईऊॠॡएऐओऔ]/;
        let m, GL = '';
        while ((m = syllableRe.exec(text)) !== null)
            GL += isGRe.test(m[1]) ? 'G' : 'L';
        return GL;
    }

    if (script === 'IAST') {
        text = text.replace(/[^aāiīuūṛṝḷḹeokgṅcjñṭḍṇtdnpbmyrlvśṣshṁḥ\s]/g, '')

        const S = '(a[iu]?|[āiīuūṛṝḷḹeo])';
        const V = '([kgcjṭḍtdpb]h|[kgṅcjñṭḍṇtdnpbmyrlvśṣshṁḥ])';

        const G = new RegExp('^' + V + '*(a[iu]|[āīūṝḹeo]|' + S + '(?=\\s*' + V + '(?!' + S + ')))');
        const L = new RegExp('^' + V + '*[aiuṛḷ](?=' + V + S + '|\\s|$)');

        let GL = '';
        let pos = 0;
        let gMatch, lMatch;

        while (pos < text.length) {

            gMatch = G.exec(text.slice(pos));
            lMatch = L.exec(text.slice(pos));

            if (lMatch) {
                GL += 'L';
                pos += lMatch[0].length;
            } else if (gMatch) {
                GL += 'G';
                pos += gMatch[0].length;
            } else {
                pos += 1;
            }
        }
        console.log(GL)

        return GL;
    }

    return text;
}

// ---------- Visualization ----------
function renderSunburst(data) {
    g.selectAll('*').remove();
    const root = getHierarchy(data);
    currentRoot = root;
    partition(root);

    const maxLength = +document.getElementById('maxLength').value || 26;
    const visibleNodes = root.descendants().filter(d => d.depth <= maxLength);

    const maxVisibleDepth = d3.max(visibleNodes, d => d.depth);
    const scaleY = d3.scaleLinear()
        .domain([0, maxVisibleDepth])
        .range([0, radius]);
    visibleNodes.forEach(d => {
        d.y0 = scaleY(d.depth);
        d.y1 = scaleY(d.depth + 1);
    });

    g.selectAll('path')
        .data(visibleNodes)
        .join('path')
        .attr('class', 'node')
        .attr('d', arc)
        .style('fill', d => computeFill(d))
        .on('click', handleNodeClick)
        .on('mouseover', showTooltip)
        .on('mouseout', hideTooltip);
}

function updateVisualization(root) {
    const inputText = document.getElementById('textInput').value;
    const type = document.getElementById('inputTypeDropdown').value;
    const script = document.getElementById('scriptDropdown').value;
    const targetPattern = text2GL(inputText, type, script);

    const maxLength = document.getElementById('maxLength').value || 26;
    const visibleNodes = root.descendants().filter(d => d.depth <= maxLength);

    const maxVisibleDepth = d3.max(visibleNodes, d => d.depth);
    const scaleY = d3.scaleLinear()
        .domain([0, maxVisibleDepth])
        .range([0, radius]);
    visibleNodes.forEach(d => {
        d.y0 = scaleY(d.depth);
        d.y1 = scaleY(d.depth + 1);
    });

    const cells = g.selectAll('path').data(visibleNodes, d => d.data.key);
    cells.join(
        enter => enter.append('path')
            .attr('class', 'node')
            .attr('d', arc)
            .style('fill', d => computeFill(d, targetPattern, inputText))
            .on('click', handleNodeClick)
            .on('mouseover', showTooltip)
            .on('mouseout', hideTooltip)
            .call(enter => enter.transition().duration(0).attr('d', arc)),
        update => update.transition().duration(0)
            .attr('d', arc)
            .style('fill', d => computeFill(d, targetPattern, inputText)),
        exit => exit.remove()
    );
}

function handleNodeClick(event, d) {
    event.stopPropagation();
    const root = (d === currentRoot && originalRoot)
        ? getHierarchy(originalRoot)
        : (d.children ? d : currentRoot);

    currentRoot = root;
    partition(root);
    updateVisualization(root);
}

// ---------- Tooltip ----------
const JATI = ['उक्ता', 'अत्युक्ता', 'मध्या', 'प्रतिष्ठा', 'सुप्रतिष्ठा', 'गायत्री', 'उष्णिह्', 'अनुष्टुप्', 'बृहती', 'पङ्क्ति', 'त्रिष्टुप्', 'जगती', 'अतिजगती', 'शक्वरी', 'अतिशक्वरी', 'अष्टि', 'अत्यष्टि', 'धृति', 'अतिधृति', 'कृति', 'प्रकृति', 'आकृति', 'विकृति', 'संकृति', 'अभिकृति', 'उत्कृति', 'शेषजाति'];

function showTooltip(event, d) {
    let pattern = getPath(d);
    const name = d.data.name ? `छन्दः - ${d.data.name}<br>` : '';
    let jati = JATI[pattern.length - 1] || JATI[JATI.length - 1];
    if (d.data.name && d.data.name.endsWith('दण्डक')) {
        jati = 'दण्डक';
    }

    // --- Insert yati markers (dashes) in pattern ---
    let displayPattern = pattern;
    if (Array.isArray(d.data.yati)) {
        const chars = pattern.split('');
        let insertPos = 0;

        d.data.yati.forEach(count => {
            insertPos += count;
            if (insertPos >= 0 && insertPos < chars.length + 1) {
                chars.splice(insertPos, 0, '-');
                insertPos += 1; // increase offset after insertion
            }
        });

        displayPattern = chars.join('');
    }

    const yatiLine = Array.isArray(d.data.yati)
        ? `<br>यतिः - ${d.data.yati.join(', ')}`
        : '';

    // --- Create tooltip (use .html for line breaks) ---
    const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('position', 'absolute')
        .style('visibility', 'hidden')
        .html(`${name}जातिः - ${jati} (${pattern.length})<br>चिह्नम् - ${displayPattern}${yatiLine}`);

    // Measure dimensions
    const tooltipNode = tooltip.node();
    const tooltipRect = tooltipNode.getBoundingClientRect();
    const padding = 12;
    let left = event.pageX + padding;
    let top = event.pageY + padding;

    // Clamp within viewport
    const maxLeft = window.innerWidth - tooltipRect.width - padding;
    const maxTop = window.innerHeight - tooltipRect.height - padding;
    left = Math.min(left, maxLeft);
    top = Math.min(top, maxTop);

    // Position and show
    tooltip
        .style('left', `${left}px`)
        .style('top', `${top}px`)
        .style('visibility', 'visible');
}
function hideTooltip() { d3.selectAll('.tooltip').remove(); }

// ---------- Input Reaction ----------
function handleMaxLengthChange() {
    if (currentRoot) updateVisualization(currentRoot);
}

function handleTextInput() {
    const inputText = document.getElementById('textInput').value;
    const type = document.getElementById('inputTypeDropdown').value;
    const script = document.getElementById('scriptDropdown').value;
    const targetPattern = text2GL(inputText, type, script);

    g.selectAll('path').transition().duration(300)
        .style('fill', d => computeFill(d, targetPattern, inputText));

    highlightBestNode(targetPattern, inputText);    
}    

function highlightBestNode(targetPattern, inputText) {
    hideTooltip();
    if (!inputText || !targetPattern) return;

    let best = null, min = Infinity;
    g.selectAll('path').each(function(d) {
        if (!d.data.name) return;
        const dist = levenshteinDistance(getPath(d), targetPattern);
        if (dist < min) { min = dist; best = { d, el: this }; }
    });

    if (best) {
        // Use the existing showTooltip, but fake an event at the centroid of the node
        const el = best.el;
        const [x, y] = arc.centroid(best.d);
        const pt = el.getCTM();
        const rect = svg.node().getBoundingClientRect();
        const event = { 
            pageX: rect.left + pt.e + x,
            pageY: rect.top + pt.f + y
        };
        showTooltip(event, best.d);
    }

}

// ---------- Resize ----------
window.addEventListener('resize', () => {
    d3.select('#sunburst svg').remove();
    setupSVG();
    updateVisualization(currentRoot || getHierarchy(originalRoot));
});

init();
