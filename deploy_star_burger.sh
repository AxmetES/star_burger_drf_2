#!/bin/bash

set -e 

static_folder=/home/non-root/opt/star_burger_drf_2/static

source venv/bin/activate

git pull

pip install -r requirements.txt

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

if [ -d "$static_folder" ]; then
    echo "Static folder already exists"
else
    python3 manage.py collectstatic
fi

python3 manage.py migrate

sudo systemctl reload nginx.service

sudo systemctl restart star_burger.service

source /home/non-root/opt/star_burger_drf_2/.env

commit_hash=$(git rev-parse --short HEAD)
echo $commit_hash

commit_comment=$(git log --format=%B -n 1 $commit_hash)
echo $commit_comment

commit_author=$(git log --format='%an' -n 1 $commit_hash)
echo $commit_author

payload='{
  "environment": "production",
  "revision": "'$commit_hash'",
  "rollbar_name": "Yerkin1984",
  "local_username": "'$commit_author'",
  "comment": "'$commit_comment'",
  "status": "succeeded"
}'

curl -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d "$payload"

echo "deploy script done."

