#!/bin/bash
#script creato per ridurre del 30% le immagini gelle cartelle deph, mask e img
#è un semplice script da console ricordo di lanciare il comando chmod a+x script.sh per rendere il programma eseguibile da console
#le nuove immagni verrano salvate nelle cartelle deph2, img2 e mask2 per controlalre il risultato
i=0
#numero del file di partenza
file=4
molt=3
mkdir depth2
mkdir img2
mkdir mask2
for X in $(seq 60)
do
	let "file = file + molt"
	let "i = i + 1"
	cp depth/$file.png depth2/$i.png
	cp img/$file.png img2/$i.png
	cp mask/$file.png mask2/$i.png
		
done
echo fine
