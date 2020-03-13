#!/usr/bin/env python3
import argparse
import re
import cairo
import matplotlib.cm as cm

def get_args(): # Usage for user input
	parser = argparse.ArgumentParser(description='Motif_Mark is a Python script to visualize motifs on sequences as an SVG image output. This program can handle both DNA and RNA sequences with multiple sequences and multiple motifs. This script can identify ambiguous motifs but cannot identify gapped motifs.')
	parser.add_argument("-f", "--file", help = "This user input file needs to be a FASTA file of a gene with exons and introns. Introns must be indentifiable as lowercase and exons as uppercase.", required = True)
	parser.add_argument("-m", "--motif", help = "This user input file needs to be a text file of motifs separated by new lines.", required = True)
	return parser.parse_args()
args = get_args()

fasta_file = args.file # read in user input and save as a file record
motifs_file = args.motif # read in the user input for the mutant name

read_fasta = open(fasta_file, "r") # open input fasta file for reading
cmap = cm.get_cmap('gist_rainbow') # set the color map gradient

def convert_fasta(fastaFILE):
	'''Convert a multiline fasta to a single line fasta'''
	length_count = 0
	max_length = 0
	seq_count = 0
	read_file = open(fastaFILE, "r")
	write_file = open("fasta_one_line.fa", "w")
	for line in read_file:
		line=line.strip()
		if ">" in line:
			write_file.write("\n"+line+"\n")
			seq_count+=1
			length_count=0
		else:
			length_count+=len(line)
			write_file.write(line)
			if length_count > max_length:
				max_length = length_count
	read_file.close()
	write_file.close()
	return(max_length,seq_count)

def parse_motif(motifFILE):
	'''This will parse the motif file to read them into a list'''
	read_file = open(motifFILE, "r")
	motif_list = []
	for line in read_file:
		line = line.strip()
		motif_list.append(line)
	read_file.close()
	return motif_list


pic_width, pic_height = convert_fasta(fasta_file)
motifs_list = parse_motif(motifs_file) # save all the possible motifs in a list to be used later

IUPAC_dict = {"Y":"[C|T|c|t|U|u]", "y":"[C|T|c|t|U|u]", "R":"[A|G|a|g]", "r":"[A|G|a|g]", "a":"[A|a]", "A":"[A|a]", "c":"[C|c]", "C":"[C|c]", "g":"[G|g]", "G":"[G|g]", "T":"[T|t|U|u]", "t":"[T|t|U|u]", "U":"[T|t|U|u]", "u":"[T|t|U|u]", "S":"[C|c|G|g]", "s":"[C|c|G|g]", "W":"[a|A|t|T]", "w":"[a|A|t|T]", "K":"[g|G|t|T]", "k":"[a|A|t|T]", "M":"[a|A|c|C]", "m":"[a|A|c|C]", "B":"[c|C|g|G|t|T]", "b":"[c|C|g|G|t|T]", "D":"[A|a|g|G|t|T]", "d":"[A|a|g|G|t|T]", "H":"[A|a|c|C|t|T]", "h":"[A|a|c|C|t|T]", "V":"[A|a|c|C|g|G]", "v":"[A|a|c|C|g|G]", "N":"[A|a|c|C|g|G|T|t|U|u]", "n":"[A|a|c|C|g|G|T|t|U|u]"}

####### make all possible motifs through regex
extended_motifs = {}
for motif in motifs_list:
	length=len(motif)
	new = "(?=("
	for letter in motif:
		if letter in IUPAC_dict:
			new=new+IUPAC_dict[letter]
			continue
		if letter not in IUPAC_dict:
			new=new+letter
			continue
	new=new+"))"
	extended_motifs[new]=length

###customize the image size loop
surface = cairo.SVGSurface("motif_mark.svg", pic_width+300, pic_height*250 ) #initialize image drawing. (NAME, WIDTH, HEIGHT)
context = cairo.Context(surface) # set the image drawing surface

read_file = open("fasta_one_line.fa","r")
first_line_blank = read_file.readline()
name = "" # blank variable for storing gene names as loop iterates
ref_dict={} # key = (start, stop, motif),  value = "description"

current_text = 50 # counter to keep track of where the text should be drawin in the image
current_gene = 100 # counter to keep track of where the gene should be drawin in the image

color_increment = 254/(len(motifs_list)+1) # divide color palate by number of motifs
color_count = 0 # counter to keep colors straight in loops

for line in read_file: # iteate over the file
	if ">" in line: #working with the def lines
		line=line.strip()
		### draw the gene label
		context.set_source_rgb (0, 0, 0)
		context.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		context.set_font_size(16)
		context.move_to(50, current_text)
		context.show_text(line)
		context.stroke() # end drawing the gene label
		current_text += 150 # increment text position in figure
	if ">" not in line:
		line=line.strip()
		seq_length=len(line)
		### draw the line representing the gene
		context.set_line_width(2)
		context.set_source_rgb (0, 0, 0)
		context.move_to(100,current_gene) # start right, start down (make horizontal line)
		context.line_to(100+seq_length,current_gene) # start right, start down
		context.stroke() # end drawing gene
		### draw the exon(s)
		for exon in re.finditer("([A-Z]+)", line):
			context.rectangle(100+exon.start(), current_gene-10, exon.end()-exon.start(), 20) #start right, start down, width, height
			context.fill()
		###### draw motifs
		for i in extended_motifs:
			rgba = cmap(round((color_count*color_increment)+1))
			for m in re.finditer(i,line):
				context.set_source_rgba (rgba[0],rgba[1],rgba[2],rgba[3]) # we need three numbers, but cmap gives 4 returned as one tuple
				context.move_to(m.start()+100,current_gene-10) # start right, start down (make horizontal line)
				context.line_to(m.start()+100,current_gene+10) # start right, start down
				context.stroke()
			color_count+=1
			continue
		color_count=0
		current_gene += 150
		continue
	continue

# make legend
legend_start = current_gene-40
context.rectangle(50, legend_start, 300, len(motifs_list)*35)
context.set_source_rgb (0, 0, 0)
context.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
context.set_font_size(16)
context.move_to(50, legend_start-10)
context.show_text("MOTIF LEGEND")
context.stroke()

for motif in motifs_list:
	rgba = cmap(round((color_count*color_increment)+1))
	legend_start+=30
	context.set_source_rgba(rgba[0],rgba[1],rgba[2],rgba[3]) #for text
	context.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
	context.set_font_size(16)
	context.move_to(100, legend_start)
	context.show_text(motif)
	context.stroke()
	context.set_source_rgba(rgba[0],rgba[1],rgba[2],rgba[3]) #for boxes
	context.rectangle(60, legend_start-10, 16, 16) #for boxes
	context.fill()
	context.stroke() #for boxes
	color_count+=1

print ("Motif Mark has generated an output image: File name 'motif_mark.svg' ")
read_file.close()
