#!/bin/sh

for f in *.ui
do
    file=$(echo $f | sed -e "s:\\..*::g" | sed -e 's/\(.*\)/\L\1/')
    echo "Running \"pyuic5 -o ui_${file}.py $f\""
    pyuic5 -o ui_${file}.py $f
done