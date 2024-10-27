#!/bin/bash

echo "-------------------Building-----------------------"
if [ ! -d build ]; then
    echo "Creating build folder"
    mkdir build
fi

cd build
cmake ..
make -j
cp ./ramulator2 ../ramulator2

