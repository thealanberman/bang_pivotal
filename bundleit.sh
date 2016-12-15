#!/usr/bin/env bash
confirm() { read -sn 1 -p "$1 [Y/N]? "; [[ $REPLY = [Yy] ]]; }

confirm "Are you in the lambda working directory?" && {
  zip -9 bundle.zip *.py && \
  cd lib/python2.7/site-packages && \
  zip -r9 ../../../bundle.zip * && \
  echo "Now run:"
  echo "aws lambda update-function-code --zip-file fileb://bundle.zip --function-name FUNCTION_NAME"
} || echo; exit
