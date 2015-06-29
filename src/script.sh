#!/bin/bash
#script creato per ridurre del 30% le immagini gelle cartelle deph, mask e img
#è un semplice script da console ricordo di lanciare il comando chmod a+x script.sh per rendere il programma eseguibile da console
#le nuove immagni verrano salvate nelle cartelle deph2, img2 e mask2 per controlalre il risultato
#configurazione
i=1
file=4
molt=3
#crea le cartelle
mkdir depth2
mkdir img2
mkdir mask2
#60 Perché mi permette di al file 181.png
for X in $(seq 60)
do
	cp depth/$file.png depth2/$i.png
	cp img/$file.png img2/$i.png
	cp mask/$file.png mask2/$i.png
	let "file = file + molt"
	let "i = i + 1"
done
echo fine
