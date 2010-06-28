/**
 * Escaper
 *
 * Escapes all the backslashes which are not translated correctly in the Flash -> JavaScript Interface
 *
 * Adapted from http://swfupload.googlecode.com/
 *
 * These functions had to be developed because the ExternalInterface has a bug that simply places the
 * value a string in quotes (except for a " which is escaped) in a JavaScript string literal which
 * is executed by the browser.  These often results in improperly escaped string literals if your
 * input string has any backslash characters. For example the string:
 * 		"c:\Program Files\uploadtools\"
 * is placed in a string literal (with quotes escaped) and becomes:
 * 		var __flash__temp = "\"c:\Program Files\uploadtools\\"";
 * This statement will cause errors when executed by the JavaScript interpreter:
 * 	1) The first \" is succesfully transformed to a "
 *  2) \P is translated to P and the \ is lost
 *  3) \u is interpreted as a unicode character and causes an error in IE
 *  4) \\ is translated to \
 *  5) leaving an unescaped " which causes an error
 *
 * I fixed this by escaping \ characters in all outgoing strings.  The above escaped string becomes:
 * 		var __flash__temp = "\"c:\\Program Files\\uploadtools\\\"";
 * which contains the correct string literal.
 *
 * Note: The "var __flash__temp = " portion of the example is part of the ExternalInterface not part of
 * my escaping routine.
 */

package
{
	public class Escaper
	{
		public static function escape(message:*):*
		{
			if (message == null || message is Function) return null;
			
			if (message is String) return escapeString(message);
			if (message is Array) return escapeArray(message);
			if (message is Boolean || message is Number) return message;
			if (message is Date) return message.valueOf();
			if (message is Object) return escapeObject(message);
			
			return message;
		}
		
		public static function escapeString(message:String):String
		{
			return message.replace(/\\/g, "\\\\");
		}
		
		public static function escapeArray(message_arr:Array):Array
		{
			var length:int = message_arr.length;
			var ret:Array = new Array(length);
			
			for (var i = 0; i < length; i++) {
				ret[i] = escape(message_arr[i]);
			}
			
			return ret;
		}
		
		public static function escapeObject(message_obj:*):Object
		{
			var ret:Object = { };
			
			for (var name:String in message_obj) {
				ret[escapeString(name)] = escape(message_obj[name]);
			}
			
			return ret;
		}
	}
}