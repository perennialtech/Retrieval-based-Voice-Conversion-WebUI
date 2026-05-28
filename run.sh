#!/bin/sh

set -e

export PATH="${HOME}/.local/bin:${PATH}"

if command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
	:
else
	echo "Python not found. Please install Python using your package manager or via PyEnv."
	exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
	echo "uv not found. Installing uv..."
	if command -v curl >/dev/null 2>&1; then
		curl -LsSf https://astral.sh/uv/install.sh | sh
	elif command -v wget >/dev/null 2>&1; then
		wget -qO- https://astral.sh/uv/install.sh | sh
	else
		echo "curl or wget is required to install uv automatically."
		echo "Install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
		exit 1
	fi
fi

if ! command -v uv >/dev/null 2>&1; then
	echo "uv installation failed. Please install uv manually:"
	echo "  https://docs.astral.sh/uv/getting-started/installation/"
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

uv run rvc-web --pycmd python
