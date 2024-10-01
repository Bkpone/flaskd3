PROJECT_DIR=$1

echo "changing to working dir"
cd $PROJECT_DIR

echo "Starting Build of library"
python3 -m build

echo "Installing locally"
python3 -m pip install -e $PROJECT_DIR
