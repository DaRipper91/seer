function seer --description 'Fuzzy find and act on system scripts (AI + SQLite powered)'
    set -l db_path "$HOME/Projects/seer/seer.db"
    
    # Show the flashy splash
    python3 ~/Projects/seer/scripts/seer-splash.py
    
    # Colors for the terminal
    set -l PURPLE (set_color af87ff)
    set -l GOLD (set_color d7af00)
    set -l CYAN (set_color 5fafd7)
    set -l RESET (set_color normal)

    # Mode: Standard (SQLite) or Semantic (AI)
    set -l query "SELECT name || ' | ' || COALESCE(description, '') || ' | ' || COALESCE(tags, '') || ' | ' || path || ' | ' || COALESCE(linked_configs, '') || ' | ' || run_count || ' | ' || COALESCE(last_run, 'Never') FROM scripts ORDER BY run_count DESC, last_run DESC, mtime DESC"
    
    # Adaptive Preview Command
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
        pygmentize -g $file 2>/dev/null | head -n 40 || cat $file | head -n 40
    '

    set -l selected (sqlite3 -separator ' | ' "$db_path" "$query" | fzf \
        --prompt="🔮 Seer: " \
        --height=90% --layout=reverse --border=double \
        --color="bg+:#262626,fg+:#af87ff,hl:#5fafd7,hl+:#5fafd7" \
        --color="border:#875faf,header:#af87ff,gutter:#262626" \
        --color="pointer:#af87ff,info:#af87ff,prompt:#5fafd7" \
        --delimiter ' \| ' \
        --with-nth 1,2 \
        --preview "$preview_cmd" \
        --preview-window="right:60%:wrap:border-left" \
        --header="[Enter] Manifest | [Ctrl-S] AI Scry | [Ctrl-T] Tag | [Ctrl-E] Edit | [Ctrl-C] Copy" \
        --bind "ctrl-r:execute(python3 ~/Projects/seer/scripts/seer-index.py)+reload(sqlite3 -separator ' | ' $db_path \"$query\")" \
        --bind "ctrl-s:unbind(ctrl-s)+change-prompt(🧠 AI Seer: )+reload(python3 ~/Projects/seer/scripts/seer-search.py {q})" \
        --bind "ctrl-e:execute($EDITOR {4})" \
        --bind "ctrl-c:execute(echo -n {4} | wl-copy || echo -n {4} | xclip -selection clipboard)+become(echo '📋 Path captured in the ether.')" \
        --bind "ctrl-t:execute(read -P 'New Tags: ' ntags; sqlite3 $db_path \"UPDATE scripts SET tags = '$ntags' WHERE path = '{4}'\")+reload(sqlite3 -separator ' | ' $db_path \"$query\")")

    if test -n "$selected"
        set -l parts (string split " | " "$selected")
        set -l name $parts[1]
        set -l path $parts[4]
        set -l configs $parts[5]
        
        # Clean the name if it has a match percentage
        set -l display_name (string replace -r "^\[[0-9]+%\] " "" "$name")

        # Action Selection Menu (UX Improvement: Don't just prompt, make it a ritual)
        echo -e "\n📍 $PURPLE Manifesting:$RESET $GOLD$display_name$RESET"
        
        set -l action "Execute"
        if test -n "$configs"
            set action (printf "Execute\nEdit Script\nView Config\nCancel" | fzf --height=5 --layout=reverse --border=rounded --prompt="✨ Select Ritual: " --color="border:#875faf,prompt:#af87ff,pointer:#af87ff")
        end

        switch $action
            case "Execute" "" # Default is execute if fzf wasn't triggered
                echo -e "🔮 $PURPLE Casting Incantation...$RESET"
                
                # Casting Animation
                set -l frames "⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏"
                for i in (seq 1 15)
                    set -l frame $frames[(math "$i % 10 + 1")]
                    echo -ne "\r$PURPLE $frame Manifesting... [ "(math $i \* 7)"% ]$RESET"
                    sleep 0.04
                end
                echo -e "\r✅ $GOLD Incantation Complete!$RESET"

                # Update stats and backup
                sqlite3 "$db_path" "UPDATE scripts SET run_count = run_count + 1, last_run = CURRENT_TIMESTAMP WHERE path = '$path'"
                python3 ~/Projects/seer/scripts/seer-chronos.py backup "$path"
                
                # Execution
                set -l tmp_err (mktemp)
                if string match -q "*.fish" "$path"; fish "$path" 2> $tmp_err
                else if string match -q "*.py" "$path"; python3 "$path" 2> $tmp_err
                else; bash "$path" 2> $tmp_err; end
                
                set -l exit_status $status
                cat $tmp_err >&2

                if test $exit_status -ne 0
                    echo -e "\n\033[31m⚠️  Ritual Interrupted! (Code: $exit_status)\033[0m"
                    read -l -P "🧪 Consult the Alchemist? [y/N] " heal_choice
                    if test "$heal_choice" = "y" -o "$heal_choice" = "Y"
                        cat $tmp_err | python3 ~/Projects/seer/scripts/seer-healer.py "$path" "$exit_status"
                    end
                end
                rm -f $tmp_err
            case "Edit Script"
                eval $EDITOR "$path"
            case "View Config"
                set -l config_list (string split "," "$configs")
                eval $EDITOR $config_list[1]
            case "*"
                return 0
        end
    end
end
