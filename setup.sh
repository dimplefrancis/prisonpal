#!/bin/bash

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup completed! To run the application:"
echo "1. Ensure your .env file is configured"
echo "2. Run: streamlit run app.py"
echo
echo "To activate the environment in the future, run:"
echo "source venv/bin/activate"