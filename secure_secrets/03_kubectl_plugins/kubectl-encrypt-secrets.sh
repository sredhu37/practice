#!/bin/bash

function print_usage() {
  echo "Usage:
  kubectl encrypt-secrets -n <namespace> [-s <secretname>]"

  exit 1
}

function encrypt_value() {
  local gpg_key_name="$1"
  local value_to_encrypt="$2"
  local file_to_encrypt="file_to_encrypt"

  if [ -f $file_to_encrypt ]; then
    rm $file_to_encrypt
  fi

  echo "$value_to_encrypt" > $file_to_encrypt

  gpg --encrypt --armor -r $gpg_key_name $file_to_encrypt
  cat "${file_to_encrypt}.asc"
}

function get_latest_gpg_key() {
  local public_gpg_key_file_name="public_gpg.key"
  local latest_gpg_key_name=$(kubectl get secrets -n $namespace -o name --sort-by=.metadata.name | grep 'gpg-key-' | tail -n 1 | cut -d '/' -f 2)
  local key_value=$(kubectl get secret -n $namespace $latest_gpg_key_name -o "jsonpath={.data.key}" | base64 -d)

  if [ -f $public_gpg_key_file_name ]; then
    rm $public_gpg_key_file_name
  fi

  echo "$key_value" > $public_gpg_key_file_name
  gpg --import $public_gpg_key_file_name

  local imported_gpg_key_name=$(echo "${latest_gpg_key_name/-gpg-key/''}")
  # gpg --sign-key $imported_gpg_key_name

  # Return imported gpg-key name
  echo $imported_gpg_key_name
}

function encrypt_single_secret() {
  local gpg_key_name=$(get_latest_gpg_key)
  local key_value_pairs=$(echo "$1" | sed 's/{//' | sed 's/}//')  # Remove '{' and '}' chars
  IFS=',' read -r -a key_value_pair_list <<< "$key_value_pairs"

  for item in "${key_value_pair_list[@]}"; do
    local key=$(echo $item | cut -d ':' -f 1)
    local value=$(echo $item | cut -d ':' -f 2)
    local encrypted_value=$(encrypt_value $gpg_key_name $value)
    echo "Encrypted_value: $encrypted_value"
  done
}

function main() {
  if [ -z "$namespace" ]; then
    namespace="default"
  fi

  if [ -n "$secret_name" ]; then
    local key_value_pairs=$(kubectl get secret -n $namespace $secret_name -o "jsonpath={.data}")
    encrypt_single_secret $key_value_pairs
  else
    local secret_value=$(kubectl get secrets -n $namespace -o "jsonpath={.items}")
    echo "Secrets in namespace $namespace: $secret_value"
    echo "Further logic to be implemented!"
  fi
}

while getopts n:s: flag
do
  case "${flag}" in
    n) namespace=${OPTARG};;
    s) secret_name=${OPTARG};;
    *) print_usage
  esac
done

main
