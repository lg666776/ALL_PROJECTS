# Attach to the tmux session
tmux attach-session -t RSI

# Select window 0
tmux send-keys -t RSI:0 C-c
tmux send-keys -t RSI:0 C-c
tmux send-keys -t RSI:0 C-c
tmux send-keys -t RSI:0 C-l

# Select window 1
tmux select-window -t RSI:1

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI:1.0
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI:1.1
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 2 in window 1 and send command
tmux select-pane -t RSI:1.2
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 3 in window 1 and send command
tmux select-pane -t RSI:1.3
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select window 2
tmux select-window -t RSI:2

# Select Panel split 0 in window 2 and send command
tmux select-pane -t RSI:2.0
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 1 in window 2 and send command
tmux select-pane -t RSI:2.1
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 2 in window 2 and send command
tmux select-pane -t RSI:2.2
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 3 in window 2 and send command
tmux select-pane -t RSI:2.3
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select window 3
tmux select-window -t RSI:3

# Select Panel split 0 in window 3 and send command
tmux select-pane -t RSI:3.0
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 1 in window 3 and send command
tmux select-pane -t RSI:3.1
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 2 in window 3 and send command
tmux select-pane -t RSI:3.2
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 3 in window 3 and send command
tmux select-pane -t RSI:3.3
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select window 4
tmux select-window -t RSI:4

# Select Panel split 0 in window 4 and send command
tmux select-pane -t RSI:4.0
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l

# Select Panel split 1 in window 4 and send command
tmux select-pane -t RSI:4.1
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-c
tmux send-keys C-l