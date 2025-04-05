<?php
include "upama.php";
$upama = new Upama();

// First create the collated text using compare
$collated = $upama->compare('file1.xml', 'file2.xml', 'basename');

// Then generate LaTeX from the collated text
$latex = $upama->latex($collated, 'latex.xsl');   
echo $latex
?>
