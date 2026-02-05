<?php
include "upama/upama.php";

$upama = new Upama();

$comparison1 = $upama->compare('temp.htec.txt','temp.htc.txt', '');
$comparison2 = $upama->compare('temp.htec.txt','temp.htna.txt', '');
$comparison3 = $upama->compare('temp.htec.txt','temp.htnb.txt', '');
$comparison4 = $upama->compare('temp.htec.txt','temp.htp.txt', '');
$comparison5 = $upama->compare('temp.htec.txt','temp.htb.txt', '');
$comparison6 = $upama->compare('temp.htec.txt','temp.htk.txt', '');
$comparison7 = $upama->compare('temp.htec.txt','temp.htet.txt', '');
$comparison8 = $upama->compare('temp.htec.txt','temp.htes.txt', '');

$collation = $upama->collate([$comparison1,$comparison2,$comparison3,$comparison4,$comparison5,$comparison6,$comparison7,$comparison8]);
$stylesheet = 'upama/xslt/with_apparatus.xsl';

echo $upama->transform($collation,$stylesheet);

?>
