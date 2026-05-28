#!/bin/sh

set -e

export PATH="${HOME}/.local/bin:${PATH}"

if command -v python >/dev/null 2>&1; then
	pycmd="python"
elif command -v python3 >/dev/null 2>&1; then
	pycmd="python3"
else
	echo "Python not found. Please install Python using your package manager or via PyEnv."
	exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
	echo "uv not found. Installing uv..."
	"$pycmd" -m pip install --upgrade uv || "$pycmd" -m pip install --user --upgrade uv
fi

if ! command -v uv >/dev/null 2>&1; then
	echo "uv installation failed. Please install uv manually:"
	echo "  python -m pip install -U uv"
	exit 1
fi

case "$(uname -s)" in
Darwin)
	default_extras="cpu"
	;;
*)
	default_extras="cuda"
	;;
esac

RVC_EXTRAS="${RVC_EXTRAS:-$default_extras}"
sync_args=""

for extra in $RVC_EXTRAS; do
	sync_args="$sync_args --extra $extra"
done

echo "Syncing dependencies with uv using extras: ${RVC_EXTRAS}"
uv sync $sync_args

uv run python web.py --pycmd python
