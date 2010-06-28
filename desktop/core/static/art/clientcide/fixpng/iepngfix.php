<?php

// Use this file in your CSS in place of the .HTC file if it works offline but not online.
// It will send the correct MIME type so that IE will execute the script correctly.

header('Content-type: text/x-component');
include('iepngfix.htc');

?>