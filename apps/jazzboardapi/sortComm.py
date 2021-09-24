def sortedComment(y):
	for ys in y:
		if ys['toComment'] == None:
			ys['toComment'] = ys['id']
		else:
			ys['toComment'] = int(ys['toComment'])

	for i in range(1, len(y)):
		j = i - 1
		key = y[i]
		while y[j]['toComment'] > key['toComment'] and j >= 0:
			y[j+1] = y[j]
			j = j - 1
		y[j+1] = key

	for ys in y:
		if ys['toComment'] == ys['id']:
			ys['toComment'] = None
		else:
			ys['toComment'] = str(ys['toComment'])

	for i in range(len(y)):
		if y[i]['toComment'] == None:
			pass
		else:
			for j in range(i-1):
				if y[j]['id'] == int(y[i]['toComment']) or y[j]['toComment'] == y[i]['toComment']:
					if y[j+1]['toComment'] != y[i]['toComment']:
						saveY = y[i]
						del y[i]
						y.insert(j+1, saveY)
						break
					
	
	return y


