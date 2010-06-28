File Browser, File Viewer, and File Editor
==========================================
<a target="FileBrowser"><img src="/filebrowser/static/art/icon_large.png" class="help-logo"/></a>

<img src="/filebrowser/static/help/images/filex.gif"/>
  
File Browser
------------
The File Browser exposes a graphical view of your
file system.  You can use it to examine the files,
download and upload them, change permissions, etc.

Many of the operations are exposed through a right-click
menu.  Double click to step into a directory.

### Permission Denied Errors

You may often see errors like the following: 
<pre><code>Permission denied: user=alice, access=WRITE, inode="secret":bob:supergroup:rwxr-xr-x"</pre></code>  

This indicates that the user "alice" (that's you in this case) is not
able to access the file or directory "secret", which is
owned by "bob" and has the permissions you see.

Typically, <a target="FileBrowser" href="/filebrowser/view/tmp">/tmp</a>
is world-writable, so you can stick output there.  Your system
administrator should also have set up a home directory (`/user/foo`)
for you.

File Viewer
-----------
Double-clicking on a file (or using the right-click menu)
lets you see the contents of a file.  If the file is
a binary file, switch to the "binary" view to see a hexdump.
The viewer is paged, so that you only see portions of the
file at a time.  This allows the file viewer to display
very very large files.

File Editor
-----------
For very small files, typically configuration files, you
can use the file editor to edit files directly on the
remote file system, without downloading and then
re-uploading them.
