echo "-------------------Building-----------------------"
cd build
cmake ..
make -j
cp ./ramulator2 ../ramulator2
