!/bin/bash
# run_all.sh - start Ingest, Crawler, and Viewer in tmux

VENV_PATH="/home/amnesia/Persistent/venv"
SESSION="darkwebtool"

# Make sure venv exists
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Kill old session if exists
tmux kill-session -t $SESSION 2>/dev/null

# Create new tmux session
tmux new-session -d -s $SESSION

# Window 1: Ingest API
tmux send-keys -t $SESSION "source $VENV_PATH/bin/activate && uvicorn ingest.app:app --host 127.0.0.1 --port 8000" C-m

# Window 2: Crawler
tmux new-window -t $SESSION
tmux send-keys -t $SESSION:1 "source $VENV_PATH/bin/activate && torsocks python3 -m processor.worker" C-m

tmux new-window -t $SESSION
tmux send-keys -t $SESSION:2 "source $VENV_PATH/bin/activate && python3 -m crawler.tor_crawler_tails"
# Window 3: Viewer
tmux new-window -t $SESSION
tmux send-keys -t $SESSION:3 "source $VENV_PATH/bin/activate && python3 -m viewer.cli_viewer" C-m

echo "Started Ingest, Crawler, and Viewer in tmux."
echo "Attach with: tmux attach -t $SESSION"
