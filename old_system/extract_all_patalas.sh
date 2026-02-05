#!/bin/bash

for value in {1..11}; do
	python extract_patalas.py htec.xml 1.$value
	python extract_patalas.py htes.xml 1.$value
	python extract_patalas.py htet.xml 1.$value
	python extract_patalas.py htc.xml 1.$value
	python extract_patalas.py htna.xml 1.$value
	python extract_patalas.py htnb.xml 1.$value
	python extract_patalas.py htp.xml 1.$value	
	python extract_patalas.py htb.xml 1.$value	
	python extract_patalas.py htk.xml 1.$value
done

for value in {1..12}; do
	python extract_patalas.py htec.xml 2.$value
	python extract_patalas.py htes.xml 2.$value
	python extract_patalas.py htet.xml 2.$value
	python extract_patalas.py htc.xml 2.$value
	python extract_patalas.py htna.xml 2.$value
	python extract_patalas.py htnb.xml 2.$value
	python extract_patalas.py htp.xml 2.$value	
	python extract_patalas.py htb.xml 2.$value	
	python extract_patalas.py htk.xml 2.$value
done
