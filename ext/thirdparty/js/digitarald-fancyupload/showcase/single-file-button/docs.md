### What happens?

The PHP script does not save the files but [logs](../script.log) every request. Check the Firebug console for event debugging logs.

1. Select an image smaller than 2 Mb.
	* If the file is too big, the uploader gives you a warning.
	* After selecting a file, the browse button gets disabled.
2. The image is uploaded, the button changes its text to the progress info.
3. The server-side [PHP script](../script.php) logs the upload (**see [.log](../script.log)**).
	* This demo appends the browsers cookie data automatically (option `appendCookieData`), therefore the POST values contain the `SID`.
4. A JSON response is returned, including a *MD5 hash*, [generated](http://docs.php.net/manual/en/function.md5-file.php) from the file content.
5. The hash is used to get a [monsterid](http://scott.sherrillmix.com/blog/blogger/wp_monsterid/) from [gravatar](http://en.gravatar.com/site/implement/url), so every file has an unique gravatar (nothing actually useful, just to show off the server-side processing, since we don't save the file)

Update messages are presented by [Roar Notifications](http://digitarald.de/project/roar/).