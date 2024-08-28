#!/bin/bash

FL="$1"
[ -z "$FL" ] && echo "Error: need the site_values file as parameter." && exit -1
[ ! -e "$FL" ] && echo "Error: file '$FL' does not exist." && exit -2

TLS=$(cat <<"EOF" | base64 -w 0
  security:
    tls:
      enabled: true
EOF
)
GLOBAL=$(yq -o json eval '.' $FL | jq -r -c .global.security);
if [ "$GLOBAL" == "null" ]; then
    TMPFILE=.tmp.$RANDOM.txt
    N=$(cat -n $FL  | cat -A | grep -F '^Iglobal:'| cut -d ^ -f 1)
    M=$(expr $N + 1)

    head -n  $N   $FL           > $TMPFILE
    echo -n  $TLS | base64 -d  >> $TMPFILE
    tail -n +$M   $FL          >> $TMPFILE
    mv $TMPFILE $FL
else
   echo "Error: in the site_values there is already the section .global.security"
   exit -1;
fi

# check if the syntax is still ok
cat $FL | yq eval . - > /dev/null
