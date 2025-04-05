#!/bin/bash

for value in {1..11}; do
	python extract_patalas.py htec.txt 1.$value
	python extract_patalas.py htes.txt 1.$value
	python extract_patalas.py htet.txt 1.$value
	python extract_patalas.py htc.txt 1.$value
	python extract_patalas.py htna.txt 1.$value
	python extract_patalas.py htnb.txt 1.$value
	python extract_patalas.py htp.txt 1.$value	
	python extract_patalas.py htk.txt 1.$value
done

for value in {1..12}; do
	python extract_patalas.py htec.txt 2.$value
	python extract_patalas.py htes.txt 2.$value
	python extract_patalas.py htet.txt 2.$value
	python extract_patalas.py htc.txt 2.$value
	python extract_patalas.py htna.txt 2.$value
	python extract_patalas.py htnb.txt 2.$value
	python extract_patalas.py htp.txt 2.$value	
	python extract_patalas.py htk.txt 2.$value
done
