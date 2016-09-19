SINGLE_BIT_MASK =  [1 << x for x in range(7, -1, -1)]

class BitString(object):

	def __init__(self, bytes, length=None, offset=None):
		self.bytes = bytes
		self.offset = offset if offset is not None else 0
		self.length = length if length is not None else 8 * len(data) - self.offset 

	def __getitem__(self, key):
		try:
			start = key.start
			stop = key.stop
		except AttributeError:
			if key < 0 or key >= length:
				raise IndexError()
			byte_index, bit_offset = (divmod(self.offset + key), 8)
			return self.bytes[byte_index] & SINGLE_BIT_MASK[bit_offset]

