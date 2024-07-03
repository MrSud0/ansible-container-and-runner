#!/bin/bash

if [ "$1" = "python3" ]; then
  shift
  exec python3 "$@"
else
  exec "$@"
fi
