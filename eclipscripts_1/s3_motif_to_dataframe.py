#!/usr/bin/python
import os
import commands
import numpy as np
import pandas
from optparse import OptionParser
#
opts=OptionParser()
usage="run step3\nusage:%prog -n protein's name -i motif_files path -o output_path"
opts=OptionParser(usage=usage)
opts.add_option("-n", help="RBP's name")
opts.add_option("-i", help="input motif file path generated by meme ")
opts.add_option("-o", help="output file path")
options,arguments=opts.parse_args()
#
protein_name = options.n
motif_path = options.i
output_path = options.o
try:
	os.popen("mkdir " + output_path)
except:
	pass
max_width = 25
#
def distribute(meme_txt, order, max_width):
    motif_order = str(order)
    lines = open(meme_txt).readlines()
    n_site = 0
    matrix, name = [], []
    for iline, line in enumerate(lines):
        words = line.split()
        if (len(words)>=4):
            if words[3] == 'maxsites=':
                nmax_site = int(words[4])
            if (words[0] == 'MOTIF') & (words[1] == motif_order):
                e_value, n_site, width = float(words[-1]), int(words[8]), int(words[5])
        if ' '.join(words) == 'Motif ' + str(order) + ' block diagrams' :
            nStart_name, nEnd_name = iline + 4, iline + 4 + n_site
        if ' '.join(words) == 'Motif ' + str(order) + ' position-specific probability matrix' :
            nStart_matrix, nEnd_matrix = iline + 3, iline + 3 + width
        if ' '.join(words) == 'Motif ' + str(order) + ' sites sorted by position p-value':
            nStart_begin, nEnd_begin = iline + 4, iline + 4 + n_site
    name = [x.split()[0] for x in lines[nStart_name:nEnd_name]]
    matrix = [x.split() for x in lines[nStart_matrix:nEnd_matrix]]
    matrix = np.asarray(matrix)
    begin = [int(x.split()[1])-1 for x in lines[nStart_begin:nEnd_begin]]
    return e_value, matrix, width, name, begin, n_site
#
def getMatrix():
    meme_files = os.listdir(motif_path)
    meme_txt = [x for x in meme_files if x[-3:]=='txt']
    memetxt_path = motif_path + '/' + meme_txt[0]
    for i in range(1, 6):
        (status, output) = commands.getstatusoutput('grep "Motif ' + str(i) + '" ' + memetxt_path)
        if len(output) > 0:
            evalue, matrix, width, name, begin, n_site = distribute(memetxt_path, i, max_width)
#            if (evalue < 1.0e-50) | ((i==1) & (evalue<1.0e-20)):
            if (n_site>=50) & (evalue<1e-2):
                proteins.append(protein_name+"_"+str(i))
                s_matrix.append(matrix[:, 4])
                m_matrix.append(matrix[:, 3])
                h_matrix.append(matrix[:, 1])
                i_matrix.append(matrix[:, 2])
                tran_name.append(','.join(name))
                begin = list(map(str, begin))
                motif_begin.append(','.join(begin))
            else:
                print protein_name, i, evalue, n_site
#
bases = ['base_'+str(x) for x in np.arange(0, max_width)]
s_matrix, m_matrix, h_matrix, i_matrix = [], [], [], []
proteins, tran_name, motif_begin = [], [], []
getMatrix()
s_matrix, m_matrix = np.asarray(s_matrix), np.asarray(m_matrix)
h_matrix, i_matrix = np.asarray(h_matrix), np.asarray(i_matrix)
#
s_df = pandas.DataFrame(s_matrix, index=proteins, columns=bases)
m_df = pandas.DataFrame(m_matrix, index=proteins, columns=bases)
h_df = pandas.DataFrame(h_matrix, index=proteins, columns=bases)
i_df = pandas.DataFrame(i_matrix, index=proteins, columns=bases)
tran_df = pandas.DataFrame(tran_name, index=proteins, columns=['binding_sites_on_transcripts'])
begin_df = pandas.DataFrame(motif_begin, index=proteins, columns=['motif_start_base'])
s_df.to_csv(output_path + '/stem_' + str(max_width) + '.csv', sep='\t')
m_df.to_csv(output_path + '/multiloop_' + str(max_width) + '.csv', sep='\t')
h_df.to_csv(output_path + '/hairpin_' + str(max_width) + '.csv', sep='\t')
i_df.to_csv(output_path + '/interior_' + str(max_width) + '.csv', sep='\t')
tran_df.to_csv(output_path + '/binding_sites_on_trans_' + str(max_width) + '.csv', sep='\t')
begin_df.to_csv(output_path + '/motif_start_base_' + str(max_width) + '.csv', sep='\t')
#
#