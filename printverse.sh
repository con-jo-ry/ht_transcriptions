#!/bin/bash
python collate.py HT$1

echo $'\n'HTES $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htes.txt

echo $'\n'HTET $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htet.txt

echo $'\n'HTC $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htc.txt

echo $'\n'HTNA $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htna.txt

echo $'\n'HTNAB $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htnab.txt

echo $'\n'HTNB $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htnb.txt

echo $'\n'HTP $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htp.txt

echo $'\n'HTK $1
sed -n "/\"HT$1\"/, /<\/\(lg\|p\)>/{ /HT$1/! { /<\/\(lg\|p\)>/! p } }" htk.txt
