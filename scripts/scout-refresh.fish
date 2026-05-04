# Defined in /home/daripper/.config/fish/functions/scout-refresh.fish @ line 1
function scout-refresh --description 'Re-scans the home directory for scripts and updates the inventory'
    set -l inventory "$HOME/scripts_inventory.txt"
    set -l search_dir "$HOME"
    
    echo "🚀 Starting script scan in: $search_dir"
    
    # Use find to locate files by extension
    # We use a subshell/bash call for the complex find command to ensure it's robust with the many exclusions
    bash -c 'find "$1" \
      -type d \( \
        -name "node_modules" -o -name ".git" -o -name ".cache" -o \
        -name ".npm" -o -name ".bun" -o -name ".local" -o \
        -name ".android" -o -name ".cargo" -o -name ".rustup" -o \
        -name "venv" -o -name "__pycache__" -o -name "Android" -o \
        -name "SoftMaker" -o -name "FONTS" \
      \) -prune -o \
      -type f \( \
        -name "*.sh" -o -name "*.bash" -o -name "*.zsh" -o -name "*.fish" -o \
        -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o \
        -name "*.rb" -o -name "*.php" -o -name "*.pl" -o -name "*.lua" -o \
        -name "*.ps1" -o -name "*.bat" -o -name "*.cmd" \
      \) -print > "$2"' -- "$search_dir" "$inventory"

    # Find extensionless scripts via shebang
    bash -c 'find "$1" \
      -type d \( -name "node_modules" -o -name ".git" -o -name ".cache" -o -name ".npm" -o -name ".bun" -o -name ".local" -o -name ".android" -o -name ".cargo" -o -name ".rustup" -o -name "venv" -o -name "__pycache__" -o -name "Android" -o -name "SoftMaker" -o -name "FONTS" \) -prune -o \
      -type f -executable ! -name "*.*" -print0 2>/dev/null | xargs -0 grep -l "^#!" >> "$2" 2>/dev/null' -- "$search_dir" "$inventory"

    # Sort and deduplicate
    sort -u -o "$inventory" "$inventory"
    
    set -l count (wc -l < "$inventory")
    echo "✅ Done! Found $count scripts in $inventory"
end
