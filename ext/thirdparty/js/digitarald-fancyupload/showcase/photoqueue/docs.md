Don't think that the uploader can handle only images! But since this showcase is called "Queued Photo Uploader", the
selectable file-types are limited to images. Check the showcase JavaScript shown under this paragraph for more options.

### What happens?

The PHP script does not save the files but [logs](../script.log) every request. Check the Firebug console for event debugging logs.

1. Select one or more images.
2. The images are uploaded one by one, overall progress and file progress is updated.
3. The server-side [PHP script](../script.php) logs the upload (**see [.log](../script.log)**).
4. A JSON response is returned, containing some information about the images like `mime-type`, width and height.
5. This information is added to the completed file element. We would link the uploaded image, but we don't save any files in this showcase.

#### Do Not:

 * Copy this example and ask why it doesn't upload the files. It only logs the uploaded images!
 * Copy this example without changing the XHTML, the CSS or the images!
 * Skip all validation on the server and blindly move the files!
 
#### Please Do:

 * Take this showcase as a code example about processing and validating the uploaded file and create your own server code.
 * Adapt the XHTML, the CSS and the images to your needs and share them.