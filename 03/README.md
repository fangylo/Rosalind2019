### Transposable Elements

You are given a linear genome. Find a string E that appears in the genome on its forward strand at least n times without overlaps such that each occurrence has no more than d errors.

### Input Format
The first line of the input contains three integers n, l and d – the number of times a string should appear, the expected length of the string (important for the scoring) and the maximal number of the errors for the occurrence.

### Output Format
The first line of the output should contain the string E that you found. The next n lines should contain the description of its occurrences in the genome. Each occurrence is specified by the start position of the occurrence in the genome and a CIGAR-like string. CIGAR-like string consists of a list of pairs – the type (four characters 'M', 'X', 'I' and 'D' – match, mismatch, insertion, and deletion) and how many consecutive characters have that type. 'M' means that two corresponding characters in the genome and the string E are equal, 'X' means that two corresponding characters in the genome and the string E are different, 'I' means that the characters exist in the string E but not in the genome, and 'D' means the characters exist in the genome but not in the string E. The sum of 'X', 'I' and 'D' counts should not exceed d. The occurrences of the string E in the genome should be provided in 1-indexing in the increasing order of their start positions.

### Sample Input
```
2 7 3
GAGTCATCGGACGATCC
```

### Sample Output
```
ACGTAGC
2 1M1I2M1D1M1X1M
11 3M1I1M1X1M
```

### Scoring
To get some points the provided string should appear at least n times and with no more than d errors per occurrence. Suppose that the length of your string is L then you will get (min(L,l)l)2 points, where l is given in the input