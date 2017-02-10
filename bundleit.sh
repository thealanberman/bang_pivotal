#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR &&
zip -9 bundle.zip *.py && \
cd lib/python2.7/site-packages && \
zip -r9 ../../../bundle.zip * && \
echo "Now run:"
echo "aws lambda update-function-code --zip-file fileb://bundle.zip --function-name bangpivotal"
echo "(assuming your Lambda is named 'bangpivotal')"
exit
