package py4j.examples;

public class UTFExample {

	private Byte[] array = new Byte[] { 0, 1, 10, 127, -1, -128 };

	public int strangeMéthod() {
		return 2;
	}

	public Byte[] getSurrogateBytes() {
		return new Byte[] { (byte) 0xD8, (byte) 0xD9, (byte) 0xDF };
	}

	public byte[] getSurrogatebytes() {
		return new byte[] { (byte) 0xD8, (byte) 0xD9, (byte) 0xDF };
	}

	public int getPositiveByteValue(byte b) {
		return (int) (b & 0xff);
	}

	public int getJavaByteValue(byte b) {
		return (int) b;
	}

	public int[] getUtfValue(String s) {
		int length = s.length();
		int[] values = new int[length];

		for (int i = 0; i < length; i++) {
			values[i] = s.charAt(i);
		}

		return values;
	}

	public int[] getBytesValue(byte[] bytes) {
		int length = bytes.length;
		int[] values = new int[length];

		for (int i = 0; i < length; i++) {
			values[i] = bytes[i] & 0xff;
		}

		return values;
	}

	public byte[] getBytesValue() {
		return new byte[] { 0, 1, 10, 127, -1, -128 };
	}

	public Byte[] getBytesArray() {
		return array;
	}
}
