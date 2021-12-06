#!/bin/sh

gpg_keys=$(gpg --list-keys)

encrypted_text=$(gpg --encrypt)