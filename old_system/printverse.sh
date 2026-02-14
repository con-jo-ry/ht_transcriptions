#!/bin/bash
python collate_v2.py HT$1

echo $'\n'HTES $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htes.xml

echo $'\n'HTET $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htet.xml

echo $'\n'HTC $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htc.xml

echo $'\n'HTNA $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htna.xml

echo $'\n'HTNAB $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htnab.xml

echo $'\n'HTNB $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htnb.xml

echo $'\n'HTP $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htp.xml

echo $'\n'HTB $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htb.xml

echo $'\n'HTK $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htk.xml
