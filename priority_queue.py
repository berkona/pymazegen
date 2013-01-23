class PriorityQueue:

	def __init__(self):
		self.array = []

	@property
	def size(self):
		return len(self.array)

	@property
	def isEmpty(self):
		return len(self.array) == 0
	
	def insert(self, element):
		self.array.append(element)
		self._siftDown(0, len(self.array) - 1)
	
	def insertAll(self, elements):
		for element in elements:
			self.insert(element)
	
	def deleteMin(self):
		last = self.array.pop()
		if not self.array:
			return last
		
		tmp = self.min
		self.array[0] = last
		self._siftUp(0)
		return tmp
	
	@property
	def min(self):
		return self.array[0]
	
	def _siftUp(self, pos):
		endpos = len(self.array)
		startpos = pos
		newitem = self.array[pos]
	
		# Bubble up until a leaf
		childpos = 2*pos + 1
		while childpos < endpos:
			# set childpos to index of smaller child
			rightpos = childpos + 1
			if (rightpos < endpos 
				and not self.array[childpos] 
					< self.array[rightpos]):
				childpos = rightpos
			self.array[pos] = self.array[childpos]
			pos = childpos
			childpos = 2*pos + 1
	
		self.array[pos] = newitem
		self._siftDown(startpos, pos)
	
	def _siftDown(self, startpos, pos):
		newitem = self.array[pos]
		while pos > startpos:
			parentpos = (pos - 1) >> 1
			parent = self.array[parentpos]
			if newitem < parent:
				self.array[pos] = parent
				pos = parentpos
				continue
			break
		self.array[pos] = newitem
