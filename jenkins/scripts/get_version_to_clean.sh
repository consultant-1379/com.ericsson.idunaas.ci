#!/bin/bash

INT_CHART_VERSION=$1
INSTALLED_CHART_VERSION=$2


function check_string_format {
    local VALUE="$1"
    local VAR_NAME="$2"

    # check if it is in the format N.N.N-N (where N is an arbitary positive integer number)
    echo $VALUE  | grep -q '^[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*-[0-9][0-9]*$'; CHECK1=$?
    echo $VALUE  | grep -q '^[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*$'; CHECK2=$?
    if [ $CHECK1 -ne 0 -a $CHECK2 -ne 0 ]; then
        echo "Error: ${VAR_NAME}=${VALUE} is neither in the format N.N.N-N nor N.N.N"
        exit -1
    fi

}

check_string_format "$INT_CHART_VERSION" INT_CHART_VERSION

if [ "X$INSTALLED_CHART_VERSION" == "X" \
     -o "X$(echo $INSTALLED_CHART_VERSION | tr '[:upper:]' '[:lower:]')" == "Xnone"    \
     -o "X$(echo $INSTALLED_CHART_VERSION | tr '[:upper:]' '[:lower:]')" == "Xnull"    \
     -o "X$(echo $INSTALLED_CHART_VERSION | tr '[:upper:]' '[:lower:]')" == "Xnil"     \
     -o "X$(echo $INSTALLED_CHART_VERSION | tr '[:upper:]' '[:lower:]')" == "Xfalse"   \
     -o "X$(echo $INSTALLED_CHART_VERSION | tr '[:upper:]' '[:lower:]')" == "Xdefault" \
   ]; then
    VERSION_TO_CLEAN=$INT_CHART_VERSION
else
    check_string_format "$INSTALLED_CHART_VERSION" INSTALLED_CHART_VERSION
    VERSION_TO_CLEAN=$INSTALLED_CHART_VERSION
fi

echo "VERSION_TO_CLEAN=$VERSION_TO_CLEAN" > artifact.properties