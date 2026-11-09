set -e

echo "======================================"
echo "       AVINAV INSTALLER 1.0"
echo "======================================"

if [ -z "$PREFIX" ]; then
    echo "This installer is designed for Termux."
    exit 1
fi

echo "[1/3] Updating packages..."
pkg update -y

echo "[2/3] Installing requirements..."
pkg install python git -y

echo "[3/3] Checking project..."
if [ ! -f "run.py" ]; then
    echo "run.py not found. Run this from the AVINAV folder."
    exit 1
fi

chmod +x run.py

echo ""
echo "AVINAV installation completed!"
echo "Start using: python run.py"
echo ""
echo "Optional battery support:"
echo "pkg install termux-api"
echo "Install the compatible Termux:API Android app."
