# Defined in /home/daripper/.config/fish/functions/scout.fish @ line 1
function scout --description 'Fuzzy find and act on system scripts'
    set -l inventory "$HOME/scripts_inventory.txt"
    
    if not test -f "$inventory"
        echo "⚠️ Inventory not found. Running scout-refresh..."
        scout-refresh
    end

    set -l selected (cat "$inventory" | fzf \
        --prompt="🔍 Search Scripts: " \
        --preview 'head -n 20 {}' \
        --header="Enter: Options | Ctrl-O: Edit | Ctrl-R: Refresh" \
        --bind "ctrl-r:execute(scout-refresh)+reload(cat $inventory)" \
        --bind "ctrl-o:execute($EDITOR {})")

    if test -n "$selected"
        echo "📍 Selected: $selected"
        echo "Options: [e]dit, [x]ecute, [c]opy path, [q]uit"
        read -l -P "> " choice
        
        switch $choice
            case e
                eval $EDITOR "$selected"
            case x
                # Determine runner based on extension or shebang
                if string match -q "*.fish" "$selected"
                    fish "$selected"
                else
                    bash "$selected"
                end
            case c
                if command -v wl-copy >/dev/null
                    echo -n "$selected" | wl-copy
                    echo "📋 Copied to clipboard (Wayland)."
                else if command -v xclip >/dev/null
                    echo -n "$selected" | xclip -selection clipboard
                    echo "📋 Copied to clipboard (X11)."
                else
                    echo "Path: $selected"
                end
            case '*'
                return 0
        end
    end
end
