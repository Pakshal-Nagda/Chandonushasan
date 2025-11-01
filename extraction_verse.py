import re
import numpy as np
from itertools import product

# Score matrix
MATCH = 1
MISMATCH = -1
GAP = -5
score = {}

for chars in product(['G','L','-'], repeat=4):
    a,b,c,d = chars
    G = (a=='G') + (b=='G') + (c=='G') + (d=='G')
    L = (a=='L') + (b=='L') + (c=='L') + (d=='L')
    total_score = (G*(G-1)//2 + L*(L-1)//2) * MATCH + (G*L) * MISMATCH
    if '-' in chars:
        total_score += GAP
    score[chars] = total_score

def multi_align_4D(s1, s2, s3, s4):
    a, b, c, d = len(s1), len(s2), len(s3), len(s4)
    D = np.full((a+1, b+1, c+1, d+1), -np.inf)
    back = np.empty((a+1, b+1, c+1, d+1), dtype=object)

    D[0,0,0,0] = 0
    for i in range(a+1):
        for j in range(b+1):
            for k in range(c+1):
                for l in range(d+1):
                    if i == j == k == l == 0:
                        continue
                    best_score = -np.inf
                    best_move = None
                    for use in product([0,1], repeat=4):
                        if not any(use):
                            continue
                        ii = i - use[0]
                        jj = j - use[1]
                        kk = k - use[2]
                        ll = l - use[3]
                        if ii < 0 or jj < 0 or kk < 0 or ll < 0:
                            continue
                        prev = D[ii, jj, kk, ll]
                        if prev == -np.inf:
                            continue
                        chars = (
                            s1[ii] if use[0] else '-',
                            s2[jj] if use[1] else '-',
                            s3[kk] if use[2] else '-',
                            s4[ll] if use[3] else '-'
                        )
                        gapcount = 4 - sum(use)
                        move_score = score[chars] + GAP * gapcount
                        cur_score = prev + move_score
                        if cur_score > best_score:
                            best_score = cur_score
                            best_move = (ii, jj, kk, ll, use)
                    D[i, j, k, l] = best_score
                    back[i, j, k, l] = best_move

    # Traceback to reconstruct aligned sequences
    aligned = ["", "", "", ""]
    i, j, k, l = a, b, c, d
    seqs = [s1, s2, s3, s4]

    while (i, j, k, l) != (0, 0, 0, 0):
        ii, jj, kk, ll, use = back[i, j, k, l]
        prev_indices = [ii, jj, kk, ll]
        
        for idx in range(4):
            if use[idx]:  # This sequence contributed a character
                # Use the character at position prev_indices[idx]
                aligned[idx] = seqs[idx][prev_indices[idx]] + aligned[idx]
            else:  # Gap
                aligned[idx] = '-' + aligned[idx]

        i, j, k, l = ii, jj, kk, ll

    return D[a, b, c, d], aligned

def splits(L, n, tol=1, pieces=4):
    '''Returns a list of all possible splits of a string of length `L` into `pieces` number of pieces,
    where each piece is within `n` ± `tol`.'''
    lo, hi = max(1, n - tol), n + tol
    def helper(so_far, left, depth):
        if depth == pieces - 1:
            if lo <= left <= hi:
                yield tuple(so_far + [left])
            return
        for x in range(lo, min(hi, left - (pieces - depth - 1)) + 1):
            yield from helper(so_far + [x], left - x, depth + 1)
    return list(helper([], L, 0))

def consensus_pattern(L, n):
    '''Makes the consensus pattern of length n given a list of aligned patterns'''
    assert len(L) == 4
    assert len(L[0]) == len(L[1]) == len(L[2]) == len(L[3])
    m = len(L[0])
    to_remove = n - m
    consensus = ''
    for i in range(m):
        pos = [j[i] for j in L]
        if i == m - 1:
            consensus += 'L' if 'G' not in pos else 'G'
        elif pos.count('-') >= 2:
            if not to_remove:
                consensus += max('G', 'L', key=pos.count)
            else:
                to_remove -= 1
        elif pos.count('G') > pos.count('L'):
            consensus += 'G'
        elif pos.count('L') > pos.count('G'):
            consensus += 'L'
        else:
            consensus += '?'
    return consensus

def find_best_pattern(s, n):
    '''Finds the best split of string s such that the pieces are the most aligned to each other'''
    best_score = -np.inf
    best_pattern = ['', '', '', '']
    for split in splits(len(s), n, pieces=4):
        # Partition input string according to split
        indices = [0]
        for l in split:
            indices.append(indices[-1]+l)
        parts = [s[indices[i]:indices[i+1]] for i in range(4)]
        score, aligned = multi_align_4D(*parts)
        if score > best_score:
            best_score = score
            best_pattern = aligned

    if best_score == -np.inf:
        return 'G', 0
    return consensus_pattern(best_pattern, n), best_score / ((n*(n-1)/2) * MATCH)

def verse_to_GL(verse, n):
    '''Finds the best underlying pada pattern in a verse with errors'''
    non_dev_re = re.compile(r"[^अ-औक-हा-्ॠॡॢॣंः]")
    syllable_re = re.compile(r"((([क-ह]्)*[क-ह][ा-ॄॢॣेैोौ]?|[अ-ऌॠॡएऐओऔ])[ंः]?([क-ह]्)?)")
    is_G_re = re.compile(r"[ाीूॄॣेैोौ्]$|[ंः]$|[आईऊॠॡएऐओऔ]")

    full_pattern = ''
    verse = non_dev_re.sub('', verse)
    syllables = [m.group(1) for m in syllable_re.finditer(verse)]
    for syll in syllables:
        if is_G_re.search(syll):
            full_pattern += 'G'
        else:
            full_pattern += 'L'

    if len(full_pattern) == 4*n:
        pat = full_pattern[:n-1]
        if full_pattern[n:2*n-1] == full_pattern[2*n:3*n-1] == full_pattern[3*n:-1]:
            last = 'L' if full_pattern[n-1] == full_pattern[2*n-1] == full_pattern[3*n-1] == full_pattern[-1] == 'L' else 'G'
            return pat + last, 1
    
    if len(full_pattern) > 4*n + 4:
        candidates = [find_best_pattern(full_pattern[:4*n], n),
                      find_best_pattern(full_pattern[-4*n:], n)]
        return max(candidates, key=lambda x: x[1])
    return find_best_pattern(full_pattern, n)
