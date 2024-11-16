#!/bin/bash
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path> <permissions>"
    exit 1
fi
path=$1
permissions=$2

chmod "$permissions" "$path"
echo "Permissions for $path updated to $permissions"
