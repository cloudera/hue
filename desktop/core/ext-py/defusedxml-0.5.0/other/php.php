#!/usr/bin/php
<?php

// $options = 0;
// $options = LIBXML_NONET;
$options = LIBXML_NOENT;

/* LIBXML_NOENT doesn't have any effect but
   libxml_disable_entity_loader(true) works */

$xml = simplexml_load_file($argv[1], "SimpleXMLElement", $options);
$data = (string)$xml;
echo strlen($data);
echo $data;
?>

