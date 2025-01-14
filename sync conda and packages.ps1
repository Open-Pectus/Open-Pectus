conda env update -p="./conda" --file=environment.yml --prune
pip install -e '.[development]'
