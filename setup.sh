#!/usr/bin/env bash

# Sets up this repo, installing all the things

echo "Initializing submodules"
git submodule update --recursive

echo "Compiling fastText"
cd fastText
make

if [ $? != 0 ]; then
    echo "Could not compile fastText"
    exit $?
fi

echo "Testing for MatLAB"
python -c "import matlab"
if [ $? != 0 ]; then
    echo "Could not import MatLab. Please ensure that it's installed on your system and follow the instructions at https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html"
    exit $?
fi