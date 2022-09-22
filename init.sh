#!/bin/bash
set -e

# echo "Starting SSH ..."
# service ssh start
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]