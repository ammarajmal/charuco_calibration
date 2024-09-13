#!/bin/bash

# Arguments: $1 is the source file, $2 is the destination file
if [ -f "$1" ]; then
  cp "$1" "$2"
  echo "Copied $1 to $2"
else
  echo "Source file $1 does not exist"
fi
