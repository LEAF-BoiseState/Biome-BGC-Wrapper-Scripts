
infilename  = "temp_ini.txt"
outfilename = "temp_out.txt"

keys   = ("keyOffsetTmax","keyOffsetTmin","keyMultPrcp","keyMultVPD","keyMultSWR")
values = ("0.0","0.0","1.0","1.0","1.0")

infile  = open(infilename,'r')
outfile = open(outfilename,'w')

for line in infile:
	for check, repl in zip(keys, values):
		line = line.replace(check, repl)
	outfile.write(line)

infile.close()
outfile.close()

