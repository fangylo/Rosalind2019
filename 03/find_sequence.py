import re
import argparse
from logzero import loglevel, logger
from argparse import RawTextHelpFormatter
from collections import namedtuple, Counter
from typing import List, NamedTuple, Optional, Tuple


MATCH_TYPE = "M"
INSERT_TYPE = "I"
DELETE_TYPE = "D"
SUBSTITUTION_TYPE = "X"

class DistanceMatchTypePair(object):
    def __init__(self, distance: int, matching_types: str) -> None:
        self.distance = distance
        self.matching_types = matching_types

    def __le__(self, other: 'DistanceMatchTypePair') -> bool:
        return self.distance <= other.distance

    def __eq__(self, other: 'DistanceMatchTypePair') -> bool:
        return self.distance == other.distance

    def __lt__(self, other: 'DistanceMatchTypePair') -> bool:
        return self.distance < other.distance

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(distance = {str(self.distance)}, matching_types = "{self.matching_types}")'

    def get_total_mismatch(self) -> int:
        counter = Counter(self.matching_types)
        return counter[INSERT_TYPE] + counter[DELETE_TYPE] + counter[SUBSTITUTION_TYPE]


    @staticmethod
    def shortest(distance_matchingtypes: List['DistanceMatchTypePair']) -> Tuple[int,'DistanceMatchTypePair']:
        result = distance_matchingtypes[0]
        idx = 0
        for i in range(0, len(distance_matchingtypes)):
            if distance_matchingtypes[i].distance < result.distance:
                result = distance_matchingtypes[i]
                idx = i
        return idx, result


class LevenensteinMatrix(object):
    """
    An object used as result cache that stores the matrix with distance and
    matching types
    """
    def __init__(self, width: int, height: int) -> None:
        self.width = width + 1
        self.height = height + 1
        self.matrix = []
        for _ in range(0, width + 1):
            self.matrix.append([DistanceMatchTypePair(0, "") for _ in range(0, height + 1)])

    def elementAt(self, i: int, j: int) -> 'DistanceMatchTypePair':
        return self.matrix[i][j]

    def distanceAt(self, i: int, j: int) -> int:
        return self.matrix[i][j].distance

    def matchingTypeAt(self, i: int, j: int) -> str:
        return self.matrix[i][j].matching_types

    def setElementAt(self, i: int, j: int, distance_matchingtype: 'DistanceMatchTypePair') -> None:
        self.matrix[i][j] = distance_matchingtype

    def setDistanceAt(self, i: int, j: int, distance: int) -> None:
        self.matrix[i][j].distance = distance

    def setMatchingTypeAt(self, i: int, j: int, matching_type: str) -> None:
        self.matrix[i][j].matching_types = str(matching_type)


def levenshtein(s: str, t: str, max_mismatch: Optional[int] = None) -> Optional['DistanceMatchTypePair']:
    """
    Calculate the Levenshtein distance and record type of macthing of two
    strings: s and t

    Note:
        Insertion / deletion is based on the persepctive from string `s`

    Returns:
        - A DistanceMatchTypePair object that describes:
            - Levenshtein distance between the two strings
            - A CIGAR like string with matching type from the perspective of `s`
    """
    # Build a matrix that stores (1) the levenshtein distance and (2) the
    # matching type CIGAR like string for each position

    # Initiate the LevenensteinMatrix obj:
    # Result cache is a matrix with dimension len(s) + 1 * len(t) +1
    s_len = len(s)
    t_len = len(t)
    cached_matrix: 'LevenensteinMatrix' = LevenensteinMatrix(s_len, t_len)
    # logger.debug(f'cached matrix has width = {str(cached_matrix.width)}, height = {str(cached_matrix.height)}')
    # logger.debug(f'cached matrix first dim length = {len(cached_matrix.matrix)}')
    # logger.debug(f'After inititalization matrix[1]: {cached_matrix.matrix[1]}')

    # Inistiate the first row and column.
    # Width of the matrix is len(s) + 1
    for i in range(1, s_len + 1):
        cached_matrix.setDistanceAt(i, 0, distance = i)
        cached_matrix.setMatchingTypeAt(i, 0, matching_type = INSERT_TYPE * i)


    for j in range(1, t_len + 1):
        cached_matrix.setDistanceAt(0, j, distance = j)
        cached_matrix.setMatchingTypeAt(0, j, matching_type = DELETE_TYPE * j)

    # Loop through two strings & update the cached_matrix accordingly by finding
    # the minimum distance within the L shape. For each (i,j), look for minimum
    # among -  left (i-1, j),  corner (i-1, j-1), up(i, j-1)
    # Note that the index on the cached matrix is one base more than length of string
    for i in range(0, s_len):
        for j in range(0, t_len):

            i_at_cached_matrix = i + 1
            j_at_cached_matrix = j + 1

            left = cached_matrix.elementAt(i_at_cached_matrix - 1, j_at_cached_matrix)
            corner = cached_matrix.elementAt(i_at_cached_matrix - 1, j_at_cached_matrix - 1)
            up= cached_matrix.elementAt(i_at_cached_matrix, j_at_cached_matrix - 1)


            if s[i] == t[j]:
                this_base_distance = 0
                this_base_matching_type = MATCH_TYPE
            else:
                this_base_distance = 1
                this_base_matching_type = SUBSTITUTION_TYPE

            from_left = DistanceMatchTypePair(distance = left.distance + 1,
                matching_types = left.matching_types + INSERT_TYPE)
            from_up = DistanceMatchTypePair(distance = up.distance + 1,
                matching_types = up.matching_types + DELETE_TYPE)
            from_corner = DistanceMatchTypePair(distance = corner.distance + this_base_distance,
                matching_types = corner.matching_types + this_base_matching_type)

            _, choice = DistanceMatchTypePair.shortest([from_left, from_up, from_corner])
            cached_matrix.setElementAt(i_at_cached_matrix, j_at_cached_matrix, choice)

            # logger.debug(f'i={i}, j={j}, choice={choice}')

            if max_mismatch is not None:
                current_mismatch = choice.get_total_mismatch()
                if current_mismatch > max_mismatch:
                    logger.info(f'"{str(s[0:i])}" and "{str(t[0:j])}" has mismatch number={str(current_mismatch)},'
                        f' greater than max allowed mismatch: {str(max_mismatch)}, stop iteration. ')
                    return

    return cached_matrix.elementAt(s_len , t_len)


def read_test_file(file: str) -> NamedTuple:
    """
    Read in test file with set format and return test parameters used
    Return:
        A namedtuple with:
            - num_occurence
            - seq_length
            - max_mismatch
            - genome_seq
    """
    Seq = namedtuple("Seq", ["number_occurence", "seq_length", "max_mismatch", "genome_seq"])
    with open(file) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    num_occurence, seq_len, max_mismatch = lines[0].split()
    genome_seq = lines[1].strip()
    result = Seq(int(num_occurence), int(seq_len), int(max_mismatch), str(genome_seq))
    return result


def number_of_occurence_of(sequence1: str, in_sequence2: str,
        max_mismatch: int = 0) -> Tuple[List[int], List['DistanceMatchTypePair']]:
    """
    Count the number of occurence of sequence1 within the sequence2,
    starting from the first base and move one by one. If a match is found, jump to the next
    no-overlapping base.

    Args:
        - sequence1
        - in_sequence2: The sequence that sequence1 is matched to
        - max_mismatch: maximum number of allowed mismatch
    Returns:
        - Tuple of:
            - A list of starting position in 1-base index
            - A list of `DistanceMatchTypePair` that describes the corresponding matching distance and matching types
    """
    logger.debug(f'seq1={sequence1}')
    logger.debug(f'seq2={in_sequence2}')
    length = len(sequence1)
    matched_start_positions = []
    matched_distance_matchtype_pairs = []
    i = 0
    while i <= (len(in_sequence2) - (length)):
        # Here make a new Levenenstein algorithm:
        end_indices = range(i + length - max_mismatch, i + length + max_mismatch + 1)
        distance_matching_pairs = []
        logger.debug(f'i={i}')
        for idx in end_indices:
            distance_matching_pairs.append(levenshtein(sequence1, in_sequence2[i : idx]))
            logger.debug(in_sequence2[i : idx])
        logger.debug(f'distance_matching_pairs={distance_matching_pairs}')
        logger.debug(f'end_indices={end_indices}')
        x, distance_matching_pair = DistanceMatchTypePair.shortest(distance_matching_pairs)

        # Which one got chosen?
        # If same length,
        chosen_end_inx = end_indices[x]

        # distance_matching_pair = levenshtein(sequence1, in_sequence2[i : (i + length + max_mismatch)])
        logger.debug(f'i={i},distance_matching_pair={distance_matching_pair}, x={str(x)}')

        if distance_matching_pair.distance <= max_mismatch:
            matched_start_positions.append(i + 1)
            matched_distance_matchtype_pairs.append(distance_matching_pair)
            # Jump to next non-overlapping site

            i = chosen_end_inx

        else:
            # If match not found, move forward 1 base every time
            i = i + 1
    return (matched_start_positions, matched_distance_matchtype_pairs)


def find_string(number_occurence: int, seq_length: int, max_mismatch: int, genome_seq: str):
    """
    Find a substring in `genome_seq` that matches the `genome_seq` at least
    `number_occurence` times. Stops after finding one.

    args:
        - number_occurence: how many times this string occur in genome
        - seq_length: length of string to be found
        - max_mismatch: number of maximum mismatch allowed
        - genome_seq: string of genome sequence

    Returns:
        string
    """
    current_idx = 0
    found = False

    while not found and current_idx <= (len(genome_seq) - seq_length):
        current_str = genome_seq[current_idx : (current_idx + seq_length)]
        found_str = None
        found_matched_start_positions = None

        current_matched_start_positions, current_matched_distance_matchtype_pairs = number_of_occurence_of(current_str, genome_seq, max_mismatch)
        logger.debug(f"current_idx={current_matched_start_positions}, num_occ = {str(len(current_matched_distance_matchtype_pairs))}")

        if number_occurence <= len(current_matched_start_positions):
            found = True
            found_str = current_str
            found_matched_start_positions = current_matched_start_positions
            found_matched_distance_matchtype_pairs = current_matched_distance_matchtype_pairs
            break
        else:
            current_idx = current_idx + 1

    return found_str, found_matched_start_positions, found_matched_distance_matchtype_pairs

def to_counted_string(seq: str):
    """
    Examples:
        >>> to_counted_string('MXXIDXMMMD')
        '1M2X1I1D1X3M1D'

    """
    cached_count = 1
    result = ''

    for i in range(1, len(seq)):
        if seq[i]==seq[i-1]:
            if i != (len(seq) - 1):
                cached_count = cached_count + 1
            else:
                # logger.debug(f'At i={str(i)}, cached_count={str(cached_count)}')
                result = result + str(cached_count + 1) + seq[i]
        else:
            result = result + str(cached_count) + seq[i-1]
            if i == (len(seq) - 1):
                result = result + str(1) + seq[i]
            cached_count = 1
    # logger.debug(f'i={str(i)},seq[i]={seq[i]},seq[i-1]={seq[i-1]},result="{result}"')

    return result

def test_levenshtein(str1: str,str2: str, max_mismatch: Optional[int] = None):
    """
    Examples:
        >>> test_levenshtein("AGG", "AG")
        >>> test_levenshtein("AGG", "AGTFCGTA", 2)
    """
    result = levenshtein(str1,str2, max_mismatch)
    if result is not None:
        print(f'Distance between {str1} and {str2}: {str(result.distance)}')
        print(f'Matching types: {str(result.matching_types)}')
    else:
        print(f'Number of error greater than allowed: {str(max_mismatch)}')
    print("-----------")


if __name__ == "__main__":
    loglevel(level = 30)
    parser = argparse.ArgumentParser(
        description='''

        ''',
        formatter_class=RawTextHelpFormatter,
    )
    parser = argparse.ArgumentParser(description='Find sequence.')
    parser.add_argument('input', action='store',  help='Input file')
    parser.add_argument('output', action='store',  help='Output file')
    args = parser.parse_args()
    logger.debug(args)



    # test_levenshtein("", "")
    # test_levenshtein("a", "a")
    # test_levenshtein("a", "b")
    # test_levenshtein("a", "bb")
    # test_levenshtein("ba", "bb")
    # test_levenshtein("aaa", "")
    # test_levenshtein("", "aaa")
    # test_levenshtein("xxhappyyy", "xy")
    # test_levenshtein("AGG", "AG")
    # test_levenshtein("AGG", "AGT", 2)
    # a = number_of_occurence_of("AGG","AGGTAGGTATGTT",2)
    # print(a)
    # found_str, found_matched_start_positions, found_matched_distance_matchtype_pairs = find_string(
    #     2, 3, 0, 'ATGCCATGCTCG'
    # )

    data = read_test_file(args.input)

    found_str, found_matched_start_positions, found_matched_distance_matchtype_pairs = find_string(
        data.number_occurence, data.seq_length, data.max_mismatch, data.genome_seq
    )
    print(found_str)
    for i in range(0, data.number_occurence):
        pos = found_matched_start_positions[i]
        match_str = found_matched_distance_matchtype_pairs[i].matching_types
        print(f'{str(pos)} {to_counted_string(match_str)}')

    with open(args.output, "w") as f:
        print(found_str, file = f)
        for i in range(0, data.number_occurence):
            pos = found_matched_start_positions[i]
            match_str = found_matched_distance_matchtype_pairs[i].matching_types
            print(f'{str(pos)} {to_counted_string(match_str)}', file = f)