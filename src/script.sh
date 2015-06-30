#!/bin/bash
#script creato per ridurre del 30% le immagini gelle cartelle deph, mask e img
#è un semplice script da console ricordo di lanciare il comando chmod a+x script.sh per rendere il programma eseguibile da console
#le nuove immagni verrano salvate nelle cartelle deph2, img2 e mask2 per controlalre il risultato
#configurazione
i=1
file=8
molt=3
#reset cartelle di appoggio
rm -r depth2 
rm -r img2 
rm -r mask2
rm -r depth_corr2
mkdir depth2
mkdir img2
mkdir mask2
mkdir depth_corr2
for X in $(seq 60)
do
	cp depth/$file.png depth2/$i.png
	cp img/$file.png img2/$i.png
	cp mask/$file.png mask2/$i.png
	cp depth_corr/$file.png depth_corr2/$i.png
	let "file = file + molt"
	let "i = i + 1"
done
rm -r depth
rm -r img
rm -r mask
rm -r depth_corr
mv depth2 depth
mv img2 img
mv mask2 mask 
mv depth_corr2 depth_corr
echo fine
#consiglio di svuotare il cestino!!!
