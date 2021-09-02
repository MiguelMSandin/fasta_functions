#!/usr/bin/env python3

import argparse
from Bio import SeqIO
import re
import statistics
import numpy as np

parser = argparse.ArgumentParser(description="Returns overall statistics and numbers from a fasta file.")

# Add the arguments to the parser
requiredArgs = parser.add_argument_group('required arguments')

requiredArgs.add_argument("-f", "--file", dest="fileIn", required=True,
                    help="An aligned fasta file.")

args = parser.parse_args()

seqs = 0
lengths = []
As = 0
Cs = 0
Gs = 0
Ts = 0
Ns = 0
gaps = 0
ambiguities = list()
for i in SeqIO.parse(open(args.fileIn), "fasta"):
	seqs += 1
	seq = i.seq
	lengths.append(len(seq))
	a = seq.upper().count("A")
	As += a
	c = seq.upper().count("C")
	Cs += c
	g = seq.upper().count("G")
	Gs += g
	t = seq.upper().count("T")
	Ts += t
	gap = seq.upper().count("-")
	gaps += gap
	n = len(seq) - (a + c + g + t + gap) # Count number of ambiguities
	Ns += n
	if n > 0:
		tmp = re.sub("A|C|G|T|-", "", str(seq.upper()))
		ambiguities.append(list(tmp))

ambiguities = [item for l in ambiguities for item in l]
ambiguities = set(ambiguities)

totalbp = As + Cs + Gs + Ts + Ns

print("File:", args.fileIn)
if(len(set(lengths)) > 1):
	print("  Not aligned")
else:
	print("  Aligned")
print("")
print("Number of sequences:", seqs)
print("")
print("Shortest sequence:    ", min(lengths), "bp")
print("  5th percentile:     ", int(np.percentile(lengths, 5)), "bp")
print("  25th percentile:    ", int(np.percentile(lengths, 25)), "bp")
print("  Median:             ", int(np.percentile(lengths, 50)), "bp")
print("Average length:       ", round(statistics.mean(lengths), 2), "bp")
print("  Standard deviation: ", round(statistics.stdev(lengths), 2), "bp")
print("  75th percentile:    ", int(np.percentile(lengths, 75)), "bp")
print("  95th percentile:    ", int(np.percentile(lengths, 95)), "bp")
print("Longest sequence:     ", max(lengths), "bp")
print("")
print("Base composition:")
print("  A:          ", As, "bp\t", round(As/totalbp*100, 2), "%")
print("  C:          ", Cs, "bp\t", round(Cs/totalbp*100, 2), "%")
print("  G:          ", Gs, "bp\t", round(Gs/totalbp*100, 2), "%")
print("  T:          ", Ts, "bp\t", round(Ts/totalbp*100, 2), "%")
if Ns > 0:
	print("  Ambiguities:", Ns, "bp\t", round(Ns/totalbp, 2), "%. Bases:", ", ".join(ambiguities))
else:
	print("  No ambiguities found")
print("Total bases: ", totalbp)
print("")
