import os


def remove_comment_fld(fld):
	for fname in os.listdir(fld):
		if fname.endswith('.tex'):
			remove_comment(fld + '/' + fname)

def remove_comment(path):
	lines = []
	for line in open(path, encoding='utf-8'):
		if '%' in line:
			ix = line.index('%')
			line = line[:ix]
			if len(line.strip()) == 0:
				continue
		lines.append(line.strip('\n'))
	with open(path, 'w', encoding='utf-8') as f:
		f.write('\n'.join(lines) + '\n')

