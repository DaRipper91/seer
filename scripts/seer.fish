function seer --description 'Fuzzy find and act on system scripts (AI + SQLite powered)'
    set -l db_path "$HOME/Projects/seer/seer.db"
    
    # Show the flashy splash
    python3 ~/Projects/seer/scripts/seer-splash.py
    
    # Mode: Standard (SQLite) or Semantic (AI)
    set -l query "SELECT name || ' | ' || COALESCE(description, '') || ' | ' || path FROM scripts ORDER BY run_count DESC, mtime DESC"
    
    set -l selected (sqlite3 -separator ' | ' "$db_path" "$query" | fzf \
        --prompt="🔮 Seer Search: " \
        --color="prompt:#af87ff,pointer:#af87ff,hl:#af87ff" \
        --delimiter ' \| ' \
        --with-nth 1,2 \
        --preview 'echo "Path: {3}"; echo "---"; head -n 20 {3}' \
        --header="Enter: Options | Ctrl-S: Semantic Search | Ctrl-R: Refresh" \
        --bind "ctrl-r:execute(seer-refresh)+reload(sqlite3 -separator ' | ' $db_path \"$query\")" \
        --bind "ctrl-s:unbind(ctrl-s)+change-prompt(🧠 AI Seer: )+reload(python3 ~/Projects/seer/scripts/seer-search.py {q})" \
        --bind "ctrl-o:execute($EDITOR {3})")

    if test -n "$selected"
        # Extract path based on result format (Semantic results have an extra column for score)
        if string match -q "*% | *" "$selected"
            set path (echo "$selected" | awk -F ' | ' '{print $NF}')
            set name (echo "$selected" | awk -F ' | ' '{print $2}')
        else
            set path (echo "$selected" | awk -F ' | ' '{print $NF}')
            set name (echo "$selected" | awk -F ' | ' '{print $1}')
        end
        
        echo "📍 Selected: $name"
        echo "Options: [x]ecute, [e]dit, [c]opy path, [q]uit"
        read -l -P "> " choice
        
        switch $choice
            case x
                # Update run count
                sqlite3 "$db_path" "UPDATE scripts SET run_count = run_count + 1, last_run = CURRENT_TIMESTAMP WHERE path = '$path'"
                
                # Execute
                if string match -q "*.fish" "$path"
                    fish "$path"
                else
                    bash "$path"
                end
            case e
                eval $EDITOR "$path"
            case c
                if command -v wl-copy >/dev/null
                    echo -n "$path" | wl-copy
                    echo "📋 Copied path to clipboard."
                else if command -v xclip >/dev/null
                    echo -n "$path" | xclip -selection clipboard
                    echo "📋 Copied path to clipboard."
                else
                    echo "Path: $path"
                end
            case '*'
                return 0
        end
    end
end
