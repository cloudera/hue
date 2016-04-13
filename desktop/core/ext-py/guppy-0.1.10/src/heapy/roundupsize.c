/* From listobject.c */

static int
roundupsize(int n)
{
	unsigned int nbits = 0;
	unsigned int n2 = (unsigned int)n >> 5;

	/* Round up: 
	 * If n <       256, to a multiple of        8.
	 * If n <      2048, to a multiple of       64.
	 * If n <     16384, to a multiple of      512.
	 * If n <    131072, to a multiple of     4096.
	 * If n <   1048576, to a multiple of    32768.
	 * If n <   8388608, to a multiple of   262144.
	 * If n <  67108864, to a multiple of  2097152.
	 * If n < 536870912, to a multiple of 16777216.
	 * ...
	 * If n < 2**(5+3*i), to a multiple of 2**(3*i).
	 *
	 * This over-allocates proportional to the list size, making room
	 * for additional growth.  The over-allocation is mild, but is
	 * enough to give linear-time amortized behavior over a long
	 * sequence of appends() in the presence of a poorly-performing
	 * system realloc() (which is a reality, e.g., across all flavors
	 * of Windows, with Win9x behavior being particularly bad -- and
	 * we've still got address space fragmentation problems on Win9x
	 * even with this scheme, although it requires much longer lists to
	 * provoke them than it used to).
	 */
	do {
		n2 >>= 3;
		nbits += 3;
	} while (n2);
	return ((n >> nbits) + 1) << nbits;
 }


