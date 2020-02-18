import os, sys


def remove_comment_fld(fld):
	for fname in os.listdir(fld):
		path = fld + '/' + fname
		if fname.endswith('.tex'):
			remove_comment(path)
		elif os.path.isdir(path):
			remove_comment_fld(path)

def remove_comment(path):
	print(path)
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


if __name__ == '__main__':
	fld = sys.argv[1]
	remove_comment_fld(fld)