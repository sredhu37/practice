#!/bin/sh

# Create random passphrase
passphrase=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
date_time=$(date +"%Y-%m-%d-%H-%M-%S")
params_path="./gpg-params-${date_time}"

# Create gpg params file

cat >$params_path <<EOF
  %echo Generating a basic OpenPGP key
  Key-Type: DSA
  Key-Length: 1024
  Subkey-Type: ELG-E
  Subkey-Length: 1024
  Name-Real: gpg-key-${date_time}
  # Name-Comment: with stupid passphrase
  # Name-Email: joe@foo.bar
  Expire-Date: 1y
  Passphrase: $passphrase
  # Do a commit here, so that we can later print "done" :-)
  %commit
  %echo done
EOF

# Create gpg key
gpg --batch --generate-key $params_path

# Cleanup
rm $params_path
