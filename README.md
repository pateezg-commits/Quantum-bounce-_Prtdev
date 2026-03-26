# Quantum-bounce-_Prtdev
A game that is built in python bypassing random.random we use Quantum Circuit to decide the "bounce. and qiskit

1. Install Python (The Foundation)
Quantum libraries run on Python. If you don't have it yet:

Go to python.org.

Crucial: During installation, check the box that says "Add Python to PATH." If you miss this, your computer won't know where to find Python when you type commands.

2. Set Up a Virtual Environment
It is a "best practice" to keep your quantum tools in their own little bubble so they don't clash with other projects.

Open your Command Prompt (cmd) or PowerShell.

Type these commands one by one:

Bash
# Create a folder for your game
mkdir quantum_game
cd quantum_game

# Create the virtual environment named 'qenv'
python -m venv qenv

# Activate it
qenv\Scripts\activate
Note: Once activated, you’ll see (qenv) appear at the start of your command line.

3. Install Qiskit and Game Tools
Now we install the actual "Quantum Engine" and a library to handle the game graphics (pygame).

Run this command:

Bash
pip install qiskit qiskit-aer pygame
qiskit: The main framework.

qiskit-aer: The local simulator that mimics a quantum computer on your CPU.

pygame: The library we’ll use to draw the ball and paddle.

####fixes major incase of errors in Windows
1. If your version of Python is too new (like 3.12 or 3.13), there might not be a pre-built "wheel" yet. In that case, the easiest way to code quantum on Windows without hair-pulling is Anaconda or Miniconda.

Download Miniconda for Windows.

Open the "Anaconda Prompt" from your Start Menu.

Run this:

Bash
conda create -n qgame python=3.10
conda activate qgame
pip install qiskit qiskit-aer pygame
Conda manages those pesky C++ dependencies much better than standard Pip on Windows.

EASY setup if you dont want developmnent stuff

make sure to run 
pip install -r requirements.txt

this install dependencies including 3d .
make sure to update gpu drivers.



thats it ... deploy with python quantum_bounce.py
