#!/bin/zsh

set -euo pipefail

DOTFILES_DIR="${0:A:h}"

ensure_dir() {
  mkdir -p "$1"
}

link_children_as_symlinks() {
  local src_dir="$1"
  local dest_dir="$2"
  local child

  [[ -d "$src_dir" ]] || return 0

  ensure_dir "$dest_dir"

  for child in "$src_dir"/*(N/); do
    ln -sfn "$child" "$dest_dir/${child:t}"
  done
}

link_children_as_symlinks "$DOTFILES_DIR/skills" "$HOME/.agents/skills"
