# Attach to the tmux session
tmux attach-session -t RSI

# Select window 0
tmux select-window -t RSI:0
tmux send-keys 'python3 LOGIN.PY' C-m
tmux send-keys 'python3 LTP.PY' C-m

# Select window 1
tmux select-window -t RSI:1

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI:1.0
tmux send-keys 'python3 AXISBK.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI:1.1
tmux send-keys 'python3 BAJAJFINSERV.PY' C-m

# Select Panel split 2 in window 1 and send command
tmux select-pane -t RSI:1.2
tmux send-keys 'python3 DLF.PY' C-m

# Select Panel split 3 in window 1 and send command
tmux select-pane -t RSI:1.3
tmux send-keys 'python3 HINDALCO.PY' C-m

# Select window 2
tmux select-window -t RSI:2

# Select Panel split 0 in window 2 and send command
tmux select-pane -t RSI:2.0
tmux send-keys 'python3 INDUSINDBK.PY' C-m

# Select Panel split 1 in window 2 and send command
tmux select-pane -t RSI:2.1
tmux send-keys 'python3 ITC.PY' C-m

# Select Panel split 2 in window 2 and send command
tmux select-pane -t RSI:2.2
tmux send-keys 'python3 JSWSTL.PY' C-m

# Select Panel split 3 in window 2 and send command
tmux select-pane -t RSI:2.3
tmux send-keys 'python3 KOTAKBK.PY' C-m

# Select window 3
tmux select-window -t RSI:3

# Select Panel split 0 in window 3 and send command
tmux select-pane -t RSI:3.0
tmux send-keys 'python3 MM.PY' C-m

# Select Panel split 1 in window 3 and send command
tmux select-pane -t RSI:3.1
tmux send-keys 'python3 SBIN.PY' C-m

# Select Panel split 2 in window 3 and send command
tmux select-pane -t RSI:3.2
tmux send-keys 'python3 TATAMOTORS.PY' C-m

# Select Panel split 3 in window 3 and send command
tmux select-pane -t RSI:3.3
tmux send-keys 'python3 TATASTEEL.PY' C-m

# Select window 4
tmux select-window -t RSI:4

# Select Panel split 0 in window 4 and send command
tmux select-pane -t RSI:4.0
tmux send-keys 'python3 TCS.PY' C-m

# Select Panel split 1 in window 4 and send command
tmux select-pane -t RSI:4.1
tmux send-keys 'python3 TITAN.PY' C-m


...................................................................
# Select Panel split 2 in window 4 and send command
tmux select-pane -t RSI:4.2
tmux send-keys 'python3 BFSRSI.PY' C-m

# Select Panel split 3 in window 4 and send command
tmux select-pane -t RSI:4.3
tmux send-keys 'python3 BAUTORSI.PY' C-m

# Select window 5
tmux select-window -t RSI:5

# Select Panel split 0 in window 5 and send command
tmux select-pane -t RSI:5.0
tmux send-keys 'python3 ICICIRSI.PY' C-m

# Select Panel split 1 in window 5 and send command
tmux select-pane -t RSI:5.1
tmux send-keys 'python3 HULRSI.PY' C-m

# Select Panel split 2 in window 5 and send command
tmux select-pane -t RSI:5.2
tmux send-keys 'python3 LTRSI.PY' C-m

# Select Panel split 3 in window 5 and send command
tmux select-pane -t RSI:5.3
tmux send-keys 'python3 KOTAKRSI.PY' C-m

