
chunksize = 1000

def read_file(filepath):
	file = open(filepath, 'r')

	data = []
	while True:
		read_chunk = file.read(chunksize)
		if not read_chunk:
			break
		data.append(read_chunk)
	file.close()
	return data


def write_file(data, filepath):
	file = open(path, 'w')
	for bt in data:
		file.write(bt)
	file.close()