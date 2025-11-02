import re
import numpy as np
from itertools import product
from concurrent.futures import ThreadPoolExecutor
from numba import njit, prange

# Score matrix
MATCH = 1
MISMATCH = -1
GAP = -5

@njit
def calculate_score(a, b, c, d):
    """Calculate score for a 4-character alignment column"""
    G = (a == ord('G')) + (b == ord('G')) + (c == ord('G')) + (d == ord('G'))
    L = (a == ord('L')) + (b == ord('L')) + (c == ord('L')) + (d == ord('L'))
    total_score = (G*(G-1)//2 + L*(L-1)//2) * MATCH + (G*L) * MISMATCH
    gaps = (a == ord('-')) + (b == ord('-')) + (c == ord('-')) + (d == ord('-'))
    if gaps > 0:
        total_score += GAP
    return total_score

MOVES = [use for use in product((0,1), repeat=4) if any(use)]
moves_array = np.array(MOVES, dtype=np.int8)

from numba import njit, prange
import numpy as np

@njit(parallel=True)
def multi_align_4D_njit(s1, s2, s3, s4):
    a, b, c, d = len(s1), len(s2), len(s3), len(s4)
    D = np.full((a+1, b+1, c+1, d+1), -128, dtype=np.int8)
    D[0, 0, 0, 0] = 0
    # Backtrack arrays
    back_move = np.full((a+1, b+1, c+1, d+1, 4), -1, dtype=np.int8)
    back_prev = np.full((a+1, b+1, c+1, d+1, 4), -1, dtype=np.int8)

    max_diag = a + b + c + d
    for diag_sum in range(1, max_diag + 1):
        # Collect candidates for parallel processing
        candidates = []
        for i_idx in range(max(0, diag_sum - (b + c + d)), min(a, diag_sum) + 1):
            for j_idx in range(max(0, diag_sum - i_idx - (c + d)), min(b, diag_sum - i_idx) + 1):
                for k_idx in range(max(0, diag_sum - i_idx - j_idx - d), min(c, diag_sum - i_idx - j_idx) + 1):
                    l_idx = diag_sum - i_idx - j_idx - k_idx
                    if 0 <= l_idx <= d:
                        candidates.append((i_idx, j_idx, k_idx, l_idx))

        candidates_arr = np.array(candidates, dtype=np.int8)

        # Parallel loop over candidates on this diagonal
        for idx in prange(len(candidates_arr)):
            i, j, k, l = candidates_arr[idx]
            best_score = -128
            best_move_idx = -1
            best_prev = np.array([-1, -1, -1, -1], dtype=np.int8)
            for move_idx in range(len(moves_array)):
                use = moves_array[move_idx]
                ii = i - use[0]
                jj = j - use[1]
                kk = k - use[2]
                ll = l - use[3]
                if ii < 0 or jj < 0 or kk < 0 or ll < 0:
                    continue
                if D[ii, jj, kk, ll] == -128:
                    continue
                char_a = s1[ii] if use[0] else ord('-')
                char_b = s2[jj] if use[1] else ord('-')
                char_c = s3[kk] if use[2] else ord('-')
                char_d = s4[ll] if use[3] else ord('-')
                gapcount = 4 - (use[0] + use[1] + use[2] + use[3])
                move_score = calculate_score(char_a, char_b, char_c, char_d) + GAP * gapcount
                cur_score = D[ii, jj, kk, ll] + move_score
                if cur_score > best_score:
                    best_score = cur_score
                    best_move_idx = move_idx
                    best_prev = np.array([ii, jj, kk, ll], dtype=np.int8)
            if best_move_idx != -1:
                D[i, j, k, l] = best_score
                back_move[i, j, k, l] = moves_array[best_move_idx]
                back_prev[i, j, k, l] = best_prev

    return D[a, b, c, d], back_move, back_prev, a, b, c, d

@njit
def traceback_alignment(s1, s2, s3, s4, back_move, back_prev, a, b, c, d):
    """Numba-optimized traceback"""
    max_len = a + b + c + d
    aligned_chars = np.full((4, max_len), ord('-'), dtype=np.int8)
    i, j, k, l = a, b, c, d
    pos = 0

    while i > 0 or j > 0 or k > 0 or l > 0:
        use = back_move[i, j, k, l]
        prev = back_prev[i, j, k, l]
        aligned_chars[0, pos] = s1[prev[0]] if use[0] else ord('-')
        aligned_chars[1, pos] = s2[prev[1]] if use[1] else ord('-')
        aligned_chars[2, pos] = s3[prev[2]] if use[2] else ord('-')
        aligned_chars[3, pos] = s4[prev[3]] if use[3] else ord('-')
        i, j, k, l = prev[0], prev[1], prev[2], prev[3]
        pos += 1

    actual_len = pos
    result = ['', '', '', '']
    for seq_idx in range(4):
        chars = []
        for idx in range(actual_len-1, -1, -1):
            chars.append(chr(aligned_chars[seq_idx, idx]))
        result[seq_idx] = ''.join(chars)

    return result

def multi_align_4D(s1, s2, s3, s4):
    """Wrapper for numba-optimized alignment"""
    s1_arr = np.array([ord(c) for c in s1], dtype=np.int8)
    s2_arr = np.array([ord(c) for c in s2], dtype=np.int8)
    s3_arr = np.array([ord(c) for c in s3], dtype=np.int8)
    s4_arr = np.array([ord(c) for c in s4], dtype=np.int8)

    score, back_move, back_prev, a, b, c, d = multi_align_4D_njit(s1_arr, s2_arr, s3_arr, s4_arr)
    aligned = traceback_alignment(s1_arr, s2_arr, s3_arr, s4_arr, back_move, back_prev, a, b, c, d)

    return score, aligned

@njit
def splits_helper(L, n, tol, pieces):
    """Numba-optimized splits generation - no nested functions"""
    lo = max(1, n - tol)
    hi = n + tol
    max_splits = 50
    result = np.empty((max_splits, pieces), dtype=np.int8)
    count = 0

    # Generate all valid 4-tuples (a, b, c, d) where a+b+c+d=L
    # and lo <= a, b, c, d <= hi
    for a in range(lo, hi + 1):
        for b in range(lo, hi + 1):
            for c in range(lo, hi + 1):
                d = L - a - b - c
                if lo <= d <= hi and count < max_splits:
                    result[count, 0] = a
                    result[count, 1] = b
                    result[count, 2] = c
                    result[count, 3] = d
                    count += 1

    valid_result = np.zeros((count, pieces), dtype=np.int8)
    for i in range(count):
        for j in range(pieces):
            valid_result[i, j] = result[i, j]

    return valid_result

def splits(L, n, tol=1, pieces=4):
    """Returns a list of all possible splits of a string of length L"""
    splits_array = splits_helper(L, n, tol, pieces)
    return [tuple(splits_array[i]) for i in range(len(splits_array))]

@njit
def consensus_pattern_njit(aligned_array, n):
    """Numba-optimized consensus pattern generation"""
    m = aligned_array.shape[1]
    to_remove = m - n
    consensus = np.full(n, ord('?'), dtype=np.int8)
    consensus_pos = 0

    for i in range(m):
        if to_remove < 0:
            break

        g_count = 0
        l_count = 0
        gap_count = 0

        for j in range(4):
            char = aligned_array[j, i]
            if char == ord('G'):
                g_count += 1
            elif char == ord('L'):
                l_count += 1
            elif char == ord('-'):
                gap_count += 1

        if gap_count >= 2 and to_remove > 0:
            to_remove -= 1
            continue

        if consensus_pos >= n:
            break

        if i == m - 1:
            consensus[consensus_pos] = ord('L') if g_count == 0 else ord('G')
        elif g_count > l_count:
            consensus[consensus_pos] = ord('G')
        elif l_count > g_count:
            consensus[consensus_pos] = ord('L')
        else:
            consensus[consensus_pos] = ord('?')

        consensus_pos += 1

    return consensus

def consensus_pattern(L, n):
    """Makes the consensus pattern"""
    assert len(L) == 4
    assert len(L[0]) == len(L[1]) == len(L[2]) == len(L[3])

    m = len(L[0])
    aligned_array = np.zeros((4, m), dtype=np.int8)
    for i in range(4):
        for j in range(m):
            aligned_array[i, j] = ord(L[i][j])

    consensus_chars = consensus_pattern_njit(aligned_array, n)
    return ''.join(chr(c) for c in consensus_chars if c != ord('?') or c == ord('?'))

def do_split(split, s):
    indices = [0]
    for l in split:
        indices.append(indices[-1]+l)
    parts = [s[indices[i]:indices[i+1]] for i in range(4)]
    score, aligned = multi_align_4D(*parts)
    return score, aligned

def find_best_pattern(s, n):
    best_score = -100
    best_pattern = ['', '', '', '']
    all_splits = splits(len(s), n, pieces=4)
    
    with ThreadPoolExecutor() as executor:
        results = executor.map(do_split, all_splits, [s] * len(all_splits))
        for score, aligned in results:
            if score > best_score:
                best_score = score
                best_pattern = aligned
    
    if best_score == -100:
        return '', 0
    return consensus_pattern(best_pattern, n), best_score / (15 * n * MATCH)

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
        if full_pattern[n:2*n-1] == full_pattern[2*n:3*n-1] == full_pattern[3*n:-1] == pat:
            last = 'L' if full_pattern[n-1] == full_pattern[2*n-1] == full_pattern[3*n-1] == full_pattern[-1] == 'L' else 'G'
            return pat + last, 1

    if len(full_pattern) > 4*n + 4:
        candidates = [find_best_pattern(full_pattern[:4*n], n),
                      find_best_pattern(full_pattern[-4*n:], n)]
        return max(candidates, key=lambda x: x[1])
    return find_best_pattern(full_pattern, n)
