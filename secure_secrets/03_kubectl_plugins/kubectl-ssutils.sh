#!/bin/bash

function print_usage() {
  echo "Usage:
  kubectl ssutils [-k <keyname>] [-n <namespace>] [-s <secretname>]"

  exit 1
}

function encrypt_value() {
  local encryption_key_name="$1"
  local value_to_encrypt="$2"
  local file_to_encrypt="file_to_encrypt"

  if [ -f $file_to_encrypt ]; then
    rm $file_to_encrypt
  fi

  echo "$value_to_encrypt" > $file_to_encrypt

  gpg --encrypt --armor -r $encryption_key_name $file_to_encrypt
  cat "${file_to_encrypt}.asc"
}

function get_latest_encryption_key() {
  local latest_encryption_key_name=$(kubectl get secrets -n $namespace -o name --sort-by=.metadata.name | grep "${key_name}" | tail -n 1 | cut -d '/' -f 2)

  local private_key_value=$(kubectl get secret -n $namespace $latest_encryption_key_name -o "jsonpath={.data.private_key}" | base64 -d)
  local public_key_value=$(kubectl get secret -n $namespace $latest_encryption_key_name -o "jsonpath={.data.public_key}" | base64 -d)

  local private_encryption_key_file_name="$latest_encryption_key_name"
  local public_encryption_key_file_name="$private_encryption_key_file_name.pub"

  if [ -f $private_encryption_key_file_name ]; then
    rm $private_encryption_key_file_name
  fi
  echo "$private_key_value" > $private_encryption_key_file_name

  if [ -f $public_encryption_key_file_name ]; then
    rm $public_encryption_key_file_name
  fi
  echo "$public_key_value" > $public_encryption_key_file_name
  
  # Return key name
  echo $latest_encryption_key_name
}

function encrypt_single_secret() {
  local encryption_key_name=$(get_latest_encryption_key)
  # echo "Encryption key name: $encryption_key_name"

  local key_value_pairs=$(echo "$1" | sed 's/{//' | sed 's/}//')  # Remove '{' and '}' chars
  IFS=',' read -r -a key_value_pair_list <<< "$key_value_pairs"

  for item in "${key_value_pair_list[@]}"; do
    local key=$(echo $item | cut -d ':' -f 1)
    local value=$(echo $item | cut -d ':' -f 2)
    
    echo "
      Pair to encrypt: key:$key value:$value
    "

    # local encrypted_value=$(encrypt_value $encryption_key_name $value)
    # echo "Encrypted_value: $encrypted_value"
  done
}

function main() {
  if [ -z "$namespace" ]; then
    namespace="default"
  fi

  if [ -z "$key_name" ]; then
    key_name="ssh-key-"
  fi

  if [ -n "$secret_name" ]; then
    local key_value_pairs=$(kubectl get secret -n $namespace $secret_name -o "jsonpath={.data}")
    # echo "Key value pairs: $key_value_pairs"
    encrypt_single_secret $key_value_pairs
  else
    local secret_value=$(kubectl get secrets -n $namespace -o "jsonpath={.items}")
    echo "Secrets in namespace $namespace: $secret_value"
    echo "Further logic to be implemented!"
  fi
}

while getopts n:s:k: flag
do
  case "${flag}" in
    n) namespace=${OPTARG};;
    s) secret_name=${OPTARG};;
    k) key_name=${OPTARG};;
    *) print_usage
  esac
done

main
