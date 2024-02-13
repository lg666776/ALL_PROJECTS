# Attach to the tmux session
tmux attach-session -t RSI5

# Select window 0
tmux select-window -t RSI5:0
tmux send-keys 'python3 LOGIN.PY' C-m
tmux send-keys 'python3 WS.PY' C-m

# Select window 1
tmux select-window -t RSI5:1

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:1.0
tmux send-keys 'python3 AXISBK.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:1.1
tmux send-keys 'python3 BAJFIN.PY' C-m

# Select window 2
tmux select-window -t RSI5:2

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:2.0
tmux send-keys 'python3 BAJFSV.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:2.1
tmux send-keys 'python3 DLF.PY' C-m

# Select window 3
tmux select-window -t RSI5:3

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:3.0
tmux send-keys 'python3 HINDALCO.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:3.1
tmux send-keys 'python3 INDUSBK.PY' C-m

# Select window 4
tmux select-window -t RSI5:4

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:4.0
tmux send-keys 'python3 INFY.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:4.1
tmux send-keys 'python3 ITC.PY' C-m

# Select window 5
tmux select-window -t RSI5:5

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:5.0
tmux send-keys 'python3 JSW.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:5.1
tmux send-keys 'python3 KOTAKBK.PY' C-m

# Select window 6
tmux select-window -t RSI5:6

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:6.0
tmux send-keys 'python3 MM.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:6.1
tmux send-keys 'python3 SBIN.PY' C-m

# Select window 7
tmux select-window -t RSI5:7

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:7.0
tmux send-keys 'python3 TCS.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:7.1
tmux send-keys 'python3 TITAN.PY' C-m

# Select window 8
tmux select-window -t RSI5:8

# Select Panel split 0 in window 1 and send command
tmux select-pane -t RSI5:8.0
tmux send-keys 'python3 TML.PY' C-m

# Select Panel split 1 in window 1 and send command
tmux select-pane -t RSI5:8.1
tmux send-keys 'python3 TSL.PY' C-m