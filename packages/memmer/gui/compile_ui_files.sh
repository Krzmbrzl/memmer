#!/bin/bash

set -e

# From https://stackoverflow.com/a/246128
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for current in "$SCRIPT_DIR/ui_files/"*.ui; do
	output_file="$SCRIPT_DIR/compiled_ui_files/ui_$( basename "$current" ".ui" ).py"
	pyside6-uic \
		--no-autoconnection \
		--output "$output_file" \
		"$current"

	# It seems like options customizing the import commands are ignored by pyside6-uic so we
	# have to patch the import statements for custom widgets ourselves.
	sed -i 's/^from \([[:alnum:]]\+\) /from ..\1 /g' "$output_file"
done
