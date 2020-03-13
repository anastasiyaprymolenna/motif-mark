# motif-mark

## Description
motif-mark is a program that searches introns and exons in a genetic sequence for motifs of interest in order to output an image that highlights the present motifs on a simple model of the gene.

## Required
Requires (python 3+)
Requires (pycairo)
Requires (re)
Requires (matplotlib)


## How to use this tool:

(Standard): User needs to supply two input files:

1. A FASTA formatted file of gene sequences with exons denoted in uppercase letters and introns in lowercase

2. A text file of motifs with 1 motif per line and no spaces

example files of fasta and motifs can be found on github (listed as <example.file>)

Input on the command line requires the user to specify "-f" flag for the name of fasta file to be used and the "-m" flag for the name of the motif file to be used.

Example of how to run this script from terminal:

```./motif_mark.py -f example.fasta -m example.motif
```

The script will generate a single-line fasta file as the program assumes the input was a multi-line fasta. This output can be disregarded if the input is already a single-line fasta.

The output of the script will be an SVG image outputted to the directory from which the script was run and be titled "motif_mark.svg".
