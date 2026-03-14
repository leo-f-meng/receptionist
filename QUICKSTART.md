# Quick Start
1. Open VS Code and Clone the code to local.
2. Open a terminal in VS Code. Create Python virtual environment using Python 3.14.3.
```bash
 uv venv --python 3.14.3
```
3. Run 
```bash
uv sync
uv run src/agent.py download-files
```
4. Open LiveKit dashboard (https://cloud.livekit.io/) and go to Setting -> API keys. Create a new API key. 

5. Create a new file '.evn.local' in project's root folder and put API keys in it. Eg.
```bash
LIVEKIT_URL="wss://receptionshard-xxxxx.livekit.cloud"
LIVEKIT_API_KEY="APIfd12bwxTPvv"
LIVEKIT_API_SECRET="XLQpLM7h0vdfasfdsa1e23r84yrVxXoRrdOORhjQFo8E"
```

NOTE: This is a dummy key, please use your own API keys.

6. Run 
```bash
uv run src/agent.py console
```