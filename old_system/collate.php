<?php
include "upama/upama.php";

$upama = new Upama();

$comparison1 = $upama->compare('temp.htec.xml','temp.htc.xml', '');
$comparison2 = $upama->compare('temp.htec.xml','temp.htna.xml', '');
$comparison3 = $upama->compare('temp.htec.xml','temp.htnb.xml', '');
$comparison4 = $upama->compare('temp.htec.xml','temp.htp.xml', '');
$comparison5 = $upama->compare('temp.htec.xml','temp.htb.xml', '');
$comparison6 = $upama->compare('temp.htec.xml','temp.htk.xml', '');
$comparison7 = $upama->compare('temp.htec.xml','temp.htet.xml', '');
$comparison8 = $upama->compare('temp.htec.xml','temp.htes.xml', '');

$collation = $upama->collate([$comparison1,$comparison2,$comparison3,$comparison4,$comparison5,$comparison6,$comparison7,$comparison8]);
$stylesheet = 'upama/xslt/with_apparatus.xsl';

echo $upama->transform($collation,$stylesheet);

?>
