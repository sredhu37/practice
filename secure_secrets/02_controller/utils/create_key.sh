#!/bin/sh

print_help () {
  echo "Usage: ./create_key.sh <namespace> <date_time>
  namespace: normal string
  date_time: should be in the format of '%Y-%m-%d %H:%M:%S' (Don't forget the quotes)
  "
}

main () {
  namespace="$1"
  date_time="$2"

  key_name="$namespace-$date_time"
  params_path="./params-$key_name"
  public_key_path="./public-$key_name.gpg"
  passphrase="passphrase-$key_name"

  # Create gpg params file
  cat >$params_path <<EOF
  %echo Generating a basic OpenPGP key
  Key-Type: DSA
  Key-Length: 1024
  Subkey-Type: ELG-E
  Subkey-Length: 1024
  Name-Real: $key_name
  Expire-Date: 1y
  Passphrase: $passphrase
  # Do a commit here, so that we can later print "done" :-)
  %commit
  %echo done
EOF

  # Create gpg key
  gpg --batch --armor --generate-key $params_path

  # Print public gpg key
  gpg --output $public_key_path --armor --export $key_name
  cat $public_key_path

  # Cleanup
  rm $params_path
  rm $public_key_path
}

if [ "$#" -ne 2 ]; then
  print_help
  exit 1
else
  date_time=$(date -d "$2" +"%Y-%m-%d-%H-%M-%S")
  main "$1" "$date_time"
fi