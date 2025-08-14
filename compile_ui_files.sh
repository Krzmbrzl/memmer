#!/bin/bash

set -e

# From https://stackoverflow.com/a/246128
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for current in "$SCRIPT_DIR/"*.ui; do
	pyside6-uic -o "$SCRIPT_DIR/ui_$( basename "$current" ".ui" ).py" "$current"
done
