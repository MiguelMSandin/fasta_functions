#!/usr/bin/env python3

import argparse
import re
import sys

parser = argparse.ArgumentParser(description="Builds the consensus sequence of an alignment.")

# Add the arguments to the parser
parser.add_argument("-f", "--file", dest="inFile", required=True,
                    help="An aligned fasta file.")

parser.add_argument("-o", "--output", dest="outFile", required=False, default=None,
                    help="The output name of the file to write the consensus sequence (in fasta format). If the file exists, it will append the consensus sequence at the end of the file. By default, the consensus sequence will be printed in the console.")

parser.add_argument("-t", "--threshold", dest="threshold", required=False, action='store', type=float,
					default=0.7,
                    help="The threshold to build a consensus given in percentage (0-100). Default=%(default)s.")

parser.add_argument("-b", "--base", dest="baseThreshold", required=False, action='store', type=float,
					default=0.3,
                    help="The threshold for a base to be considered. Default=%(default)s")

parser.add_argument("-g", "--gaps", dest="gaps", required=False, action='store', type=float,
					default=0.8,
                    help="If the proportion of gaps is more than 'g', the consensus is a gap ('-'). Default=%(default)s")

parser.add_argument("-a", "--ambiguities", dest="ambiguities", required=False, action="store_true",
                    help="If selected, ambiguites will be set to 'N' and not the IUPAC bases.")

parser.add_argument("-m", "--most", dest="most", required=False, action="store_true",
                    help="If selected, the most abundant sequence at each position will be used instead of the IUPAC code.")

parser.add_argument("-r", "--removeGaps", dest="removeGaps", required=False, action="store_true",
                    help="If selected, gaps in the consensus sequence will be remove.")

parser.add_argument("-v", "--verbose", dest="verbose", required=False, action="store_false",
					help="If selected, will not print information to the console.")

args = parser.parse_args()

# Setting variables and functions __________________________________________________________________
def readFasta(fastafile):
	out = {}
	for line in open(fastafile):
		if line.startswith(">"):
			name = line.replace(">", "")
			name = name.replace("\n", "")
			out[name] = str()
		else:
			sequence = line.replace("\n", "")
			sequence = sequence.upper()
			out[name] = (out[name] + sequence)
	return out

def parseAlignment(dictionary, length):
	out = {}
	for i in range(1, length+1):
		out[i] = list()
	for vals in fasta.values():
		i = 0
		for position in list(vals):
			i += 1
			out[i].append(position)
	return out

if args.verbose:
	print("  Setting variables")
	print("    Alignment:  ", args.inFile)
	print("    Threshold:  ", args.threshold, sep="")
	print("    Gaps:       ", args.gaps, sep="")
	print("    Base:       ", args.baseThreshold, sep="")
	if args.outFile is not None:
		print("    Output file: ", args.outFile, sep="")
	if args.ambiguities:
		print("    Ambiguities will be set to 'N'")
	if args.most:
		print("    The most abundant base will be taken for consensus")
	if args.removeGaps:
		print("    Gaps will be removed in output sequence")

iupac = {"A":"A", "C":"C", "G":"G", "T":"T", "AG":"R", "GA":"R", "CT":"Y", "TC":"Y", "GC":"S", "CG":"S", "AT":"W", "TA":"W", "GT":"K", "TG":"K", "AC":"M", "CA":"M", "CGT":"B", "CTG":"B", "TCG":"B", "GCT":"B", "TGC":"B", "GTC":"B", "AGT":"D", "ATG":"D", "GAT":"D", "TAG":"D", "GTA":"D", "TGA":"D", "ACT":"H", "ATC":"H", "CAT":"H", "TAC":"H", "CTA":"H", "TCA":"H", "ACG":"V", "AGC":"V", "CAG":"V", "GAC":"V", "CGA":"V", "GCA":"V"}

# Reading input file and parsing ___________________________________________________________________
if args.verbose:
	print("  Reading and parsing alignment")

fasta = readFasta(args.inFile)

length = set()
for vals in fasta.values():
	length.add(len(vals))

if len(length) != 1:
	print("  Error! Input file is not aligned. Exiting...")
	sys.exit(1)
else:
	length = next(iter(length))

sequences = len(fasta)

fasta = parseAlignment(fasta, length)

if args.verbose:
	print("    Sequences: ", sequences, sep="")
	print("    Positions: ", length, sep="")

# Building consensus _______________________________________________________________________________
if args.verbose:
	print("  Building consensus", end="")
	pcti = 0
consensus = list()
for position, values in fasta.items():
	if args.verbose:
		pct = round(position/length*100)
		if pct > pcti:
			pcti = pct
			print("\r  Building consensus\t", pct, "%", sep="", end="")
	bases = {}
	for b in values:
		if b not in bases.keys():
			bases[b] = 1
		else:
			bases[b] += 1
	# Initialize variables
	base = None
	candidate = list()
	most = None
	mostAbun = 0
	total = sequences
	# Check for gaps
	if "-" in bases.keys():
		c = bases["-"]
		C = c / sequences
		if C >= args.gaps:
			base = "-"
		else:
			total = sequences - c
			del bases["-"]
	# If consensus is not gap, now deal with the bases
	if base is None:
		for b, c in bases.items():
			C = c/total
			if C >= args.threshold:
				base = b
			elif C >= args.baseThreshold:
				candidate.append(b)
			if C > mostAbun:
				most = b
				mostAbun = C
	# Now finally calling the base
	if base is not None:
		if args.removeGaps:
			if base != "-":
				consensus.append(base)
		else:
			consensus.append(base)
	elif args.most:
		consensus.append(most)
	elif len(candidate) > 0:
		base = "".join(candidate)
		base = iupac[base]
		if args.ambiguities:
			if base not in "ACGT":
				base = "N"
		consensus.append(base)

consensusOut = "".join(consensus)

if args.verbose:
	print("\n  Consensus positions:   ", len(consensusOut)-consensusOut.count("-"))
	if args.most is False:
		print("    Of which are ambiguous:", len(consensusOut)-len(re.sub("[^ACTG-]", "", consensusOut)))
	if args.removeGaps is False:
		print("    Of which are gaps:     ", consensusOut.count("-"))
	print("  Consensus sequence:\n")

if args.outFile is not None:
	f = open(args.outFile, "a")
	tmp = re.sub("\\.[^\\.]+$", "", args.inFile)
	f.write(str(">" + str(tmp) + "_consensus_t" + str(args.threshold) + "_b" + str(args.baseThreshold) + "_g" + str(args.gaps) + ext + "\n"))
	f.write(str(str(consensusOut) + "\n"))
	f.close()
else:
	print(str(consensusOut))

# __________________________________________________________________________________________________
if args.verbose:
	print("\nDone")
