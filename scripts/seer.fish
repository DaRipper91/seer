function seer --description 'Fuzzy find and act on system scripts (AI + SQLite powered)'
    set -l db_path "$HOME/Projects/seer/seer.db"
    
    # Show the flashy splash
    python3 ~/Projects/seer/scripts/seer-splash.py
    
    # Colors for the terminal
    set -l PURPLE (set_color af87ff)
    set -l GOLD (set_color d7af00)
    set -l RESET (set_color normal)

    # Mode: Standard (SQLite) or Semantic (AI)
    # We include tags in the visible search and link configs in the hidden columns
    set -l query "SELECT name || ' | ' || COALESCE(description, '') || ' | ' || COALESCE(tags, '') || ' | ' || path || ' | ' || COALESCE(linked_configs, '') || ' | ' || run_count || ' | ' || COALESCE(last_run, 'Never') FROM scripts ORDER BY run_count DESC, last_run DESC, mtime DESC"
    
    # Preview Command: Uses pygmentize for colors and shows "The Crystal Ball" (stats)
    set -l preview_cmd '
        set -l file {4}
        set -l tags {3}
        set -l configs {5}
        set -l runs {6}
        set -l last {7}
        echo -e "\033[1;35m🔮 THE CRYSTAL BALL\033[0m"
        echo -e "\033[33mRuns:\033[0m $runs | \033[33mLast Run:\033[0m $last"
        echo -e "\033[33mTags:\033[0m $tags"
        if test -n "$configs"
            echo -e "\033[33mConfigs:\033[0m $configs"
        end
        echo -e "\033[1;34m--- Source ---\033[0m"
        pygmentize -g $file | head -n 40
    '

    set -l selected (sqlite3 -separator ' | ' "$db_path" "$query" | fzf \
        --prompt="🔮 Seer Search: " \
        --height=80% --layout=reverse --border=rounded \
        --color="bg+:#262626,fg+:#af87ff,hl:#5fafd7,hl+:#5fafd7" \
        --color="border:#875faf,header:#af87ff,gutter:#262626" \
        --color="pointer:#af87ff,info:#af87ff,prompt:#5fafd7" \
        --delimiter ' \| ' \
        --with-nth 1,2,3 \
        --preview "$preview_cmd" \
        --header="Enter: Options | Ctrl-S: Semantic Search | Ctrl-R: Refresh | Ctrl-T: Tag" \
        --bind "ctrl-r:execute(python3 ~/Projects/seer/scripts/seer-index.py)+reload(sqlite3 -separator ' | ' $db_path \"$query\")" \
        --bind "ctrl-s:unbind(ctrl-s)+change-prompt(🧠 AI Seer: )+reload(python3 ~/Projects/seer/scripts/seer-search.py {q})" \
        --bind "ctrl-o:execute($EDITOR {4})" \
        --bind "ctrl-t:execute(read -P 'New Tags: ' ntags; sqlite3 $db_path \"UPDATE scripts SET tags = '$ntags' WHERE path = '{4}'\")+reload(sqlite3 -separator ' | ' $db_path \"$query\")")

    if test -n "$selected"
        set -l parts (string split " | " "$selected")
        set -l name $parts[1]
        set -l path $parts[4]
        set -l configs $parts[5]
        
        echo -e "\n📍 $PURPLE Selected:$RESET $GOLD$name$RESET"
        set -l prompt "Options: [$PURPLE x$RESET]ecute, [$PURPLE e$RESET]dit, [$PURPLE c$RESET]opy path"
        if test -n "$configs"
            set prompt "$prompt, [$PURPLE v$RESET]iew config"
        end
        set prompt "$prompt, [$PURPLE q$RESET]uit"
        
        echo -e $prompt
        read -l -P "> " choice
        
        switch $choice
            case x
                echo -e "🔮 $PURPLE Manifesting script...$RESET"
                
                # Casting Animation
                set -l frames "⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏"
                for i in (seq 1 20)
                    set -l frame $frames[(math "$i % 10 + 1")]
                    echo -ne "\r$PURPLE $frame Casting Incantation... [ "(math $i \* 5)"% ]$RESET"
                    sleep 0.05
                end
                echo -e "\r✅ $GOLD Incantation Complete! Manifesting...$RESET"

                # Update run count
                sqlite3 "$db_path" "UPDATE scripts SET run_count = run_count + 1, last_run = CURRENT_TIMESTAMP WHERE path = '$path'"
                
                # Backup to Chronos Vault
                python3 ~/Projects/seer/scripts/seer-chronos.py backup "$path"
                
                # Execute and catch errors for the Alchemist
                set -l tmp_err (mktemp)
                
                if string match -q "*.fish" "$path"
                    fish "$path" 2> $tmp_err
                else if string match -q "*.py" "$path"
                    python3 "$path" 2> $tmp_err
                else
                    bash "$path" 2> $tmp_err
                end
                
                set -l exit_status $status
                
                # Show the error output as it normally would appear
                cat $tmp_err >&2

                if test $exit_status -ne 0
                    echo -e "\n\033[31m⚠️  The ritual was interrupted! (Exit code: $exit_status)\033[0m"
                    read -l -P "🧪 Consult the Alchemist to diagnose the failure? [y/N] " heal_choice
                    if test "$heal_choice" = "y" -o "$heal_choice" = "Y"
                        cat $tmp_err | python3 ~/Projects/seer/scripts/seer-healer.py "$path" "$exit_status"
                    end
                end
                
                rm -f $tmp_err
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
            case v
                if test -n "$configs"
                    set -l config_list (string split "," "$configs")
                    eval $EDITOR $config_list[1]
                else
                    echo "No linked configs found."
                end
            case '*'
                return 0
        end
    end
end
