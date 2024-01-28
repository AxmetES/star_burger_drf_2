#!/bin/bash
set -e

export MY_NGINX_PASSWORD="123Aes"
static_folder="/home/non-root/opt/star_burger_drf_2/static"


git pull

npm ci --dev

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

source venv/bin/activate

if [ -d "$static_folder" ]; then
    echo "Static folder already exists"
else
    python3 manage.py collectstatic
fi

python3 manage.py migrate

pip install -r requirements.txt

sudo systemctl reload nginx.service

sudo systemctl restart star_burger.service

echo "deploy script done."

