#!/usr/bin/env python3

import argparse
from Bio import SeqIO
import re
import statistics as st
import random

parser = argparse.ArgumentParser(description="From a fasta file, will export a table of rarefied observations. If an abundance table is given, abundances will be taken into consideration.")

requiredArgs = parser.add_argument_group('required arguments')

requiredArgs.add_argument("-f", "--file", dest="fastaFile", required=True,
                    help="A fasta file.")

parser.add_argument("-a", "--abundance", dest="abundance", required=False, default=None,
                    help="If selected, will accomodate sequence abundance for the rarification. Then a tab separated table will be needed with two columns: the name of the sequence and the abundance.")

parser.add_argument("-o", "--output", dest="output", required=False, default=None,
                    help="The output name of the rarefied table. By default will add '_rarefied.tsv' to file name excluding the extension.")

parser.add_argument("-r", "--range", dest="iterations", required=False, type=int, nargs=2, default=[0, 20000],
                    help="The range of iterations. Will take the minimum and maximum values and create a range of 'steps' for random sampling. Default: '0 20000'.")

parser.add_argument("-s", "--steps", dest="steps", required=False, type=int, default="100",
                    help="The increase of sampling steps. Default: '100'.")

parser.add_argument("-n", "--replicates", dest="replicates", required=False, type=int, default="100",
                    help="The number of rarefaction replicates. Default: '100'.")

parser.add_argument("-i", "--identifier", dest="identifier", required=False, action="store_true",
                    help="If selected, will sample sequence identifiers and not sequences. Useful if (e.g.) there are duplicated sequences in your fasta file.")

parser.add_argument("-R", "--replacement", dest="replacement", required=False, action="store_true",
                    help="If selected, the random sampling will be done without replacement.")

parser.add_argument("-v", "--verbose", dest="verbose", required=False, action="store_false",
                    help="If selected, will not print information in the console.")

args = parser.parse_args()

# Setting parameters _______________________________________________________________________________
if args.output is None:
	outFile = re.sub("\\.[^\\.]+$", "_rarefied.tsv", args.fastaFile)
else:
	outFile = args.output

rangeIter = [min(args.iterations), max(args.iterations)]
steps = list()
for i in range(rangeIter[0], rangeIter[1], args.steps):
	steps.append(i)
steps.append(rangeIter[1])

# Reading fasta ____________________________________________________________________________________
if args.verbose:
	print("  Reading fasta", args.fastaFile)
fasta = {}
for i in SeqIO.parse(open(args.fastaFile), "fasta"):
	fasta[i.id] = str(i.seq)

# Reading abundances _______________________________________________________________________________
if args.abundance is not None:
	abundance = {}
	if args.verbose:
		print("  Reading abundance table", args.abundance)
	for line in open(args.abundance):
		line = line.strip().split()
		abundance[line[0]] = line[1]

# Extracting reads _________________________________________________________________________________
reads = list()
if args.abundance is not None:
	if args.verbose:
		print("  Replicating reads by abundance", end="")
		i = 0
	for key, value in fasta.items():
		if args.verbose:
			i += 1
			I = round(i/len(fasta)*100)
			if I != i:
				print("\r  Replicating reads by abundance ", I, "%", sep="", end="")
		if args.identifier:
			for j in range(int(abundance[key])):
				reads.append(key)
		else:
			for j in range(int(abundance[key])):
				reads.append(value)
else:
	if args.verbose:
		print("  Extracting reads", end="")
		i = 0
	for key, value in fasta.items():
		if args.verbose:
			i += 1
			I = round(i/len(fasta)*100)
			if I != i:
				print("\r  Extracting reads ", I, "%", sep="", end="")
		if args.identifier:
			reads.append(key)
		else:
			reads.append(value)

if args.verbose:
	if args.identifier:
		reading = "identifiers"
	else:
		reading = "sequences"
	if args.abundance is not None:
		print("\n  Rarefication will be done:\n      -from", min(steps), "to", max(steps),
		"sampling size\n      -by steps of", steps[1]-steps[0],
		"\n      -with", args.replicates, "replicates\n      -in the total",
		len(reads), reading, "after replicating.")
	else:
		print("\n  Rarefication will be done:\n      -from", min(steps), "to", max(steps),
		"sampling size\n      -by steps of", steps[1]-steps[0],
		"\n      -with", args.replicates, "replicates\n      -in the total",
		len(reads), reading)

if args.replacement:
	if max(steps) > len(reads):
		print("\n\nWarning! You have selected a maximum sampling of", max(steps),
		"yet the sample has", len(reads),
		"reads.\nPlease consider using a smaller range or removing the replacement option.\nStopping\n")
		import sys
		sys.exit(1)

# Rarefying ________________________________________________________________________________________
out = {}
if args.verbose:
	print("  Rarefying", end="")
	i = 0
for s in steps:
	if args.verbose:
		i += 1
		I = round(i/len(steps)*100)
		if I != i:
			print("\r  Rarefying ", I, "%", sep="", end="")
	sample = list()
	for j in range(0, args.replicates):
		random.seed()
		if args.replacement:
			tmp = len(set(random.sample(reads, k=s)))
		else:
			tmp = len(set(random.choices(reads, k=s)))
		sample.append(tmp)
	out[s] = [st.mean(sample), st.stdev(sample), min(sample),
		   sorted(sample)[int(len(sample)*0.05)], sorted(sample)[int(len(sample)*0.25)],
		   sorted(sample)[int(len(sample)*0.5)], sorted(sample)[int(len(sample)*0.75)],
		   sorted(sample)[int(len(sample)*0.95)], max(sample)]

# Exporting _______________________________________________________________________________________
if args.verbose:
	print("\n  Writing table to", outFile)
with open(outFile, 'w') as outfile:
	print("sampleSize\tmean\tsd\tmin\tp05\tp25\tp50\tp75\tp95\tmax", file=outfile)
	for key, value in out.items():
		line = str(str(key) + '\t' + str(value[0]) + '\t' + str(value[1]) + '\t' + str(value[2]) + '\t' + str(value[3]) + '\t' + str(value[4]) + '\t' + str(value[5]) + '\t' + str(value[6]) + '\t' + str(value[7]) + '\t' + str(value[8]))
		print(line, file=outfile)

if args.verbose:
	print("  Final summary report:")
	print("    Fasta has a total of", len(fasta), "entries and", len(set(fasta.values())), "unique sequences.")
	sampling = max([len(fasta), len(set(fasta.values()))])
	tmp = list()
	for j in range(0, args.replicates):
		if args.replacement:
			random.seed()
			tmp1 = len(set(random.sample(reads, k=sampling)))
		else:
			random.seed()
			tmp1 = len(set(random.choices(reads, k=sampling)))
		tmp.append(tmp1)
	tmp = st.mean(tmp)
	print("    When sampling ", sampling, " ", reading, ", an average of ", tmp, " unique ", reading, " are retrieved (", round(tmp/sampling*100, 2), "%)", sep="")
	if args.abundance is not None:
		tmp = list()
		for j in range(0, args.replicates):
			random.seed()
			if args.replacement:
				tmp1 = len(set(random.sample(reads, k=len(reads))))
			else:
				tmp1 = len(set(random.choices(reads, k=len(reads))))
			tmp.append(tmp1)
		tmp = st.mean(tmp)
		print("    When sampling ", len(reads), " ", reading, ", an average of ", tmp, " unique ", reading, " are retrieved (", round(tmp/sampling*100, 2), "%)", sep="")

# __________________________________________________________________________________________________
if args.verbose:
	print("Done")
