# make sure the localhost has the same version of the code as the remote server
git pull

# re-deploy the image
docker-compose --file docker-compose-staging.yml pull
docker-compose --file docker-compose-staging.yml down --remove-orphans
docker-compose --file docker-compose-staging.yml up --detach

# clean up docker garbage to preserve disc space.
docker system prune --force --all --volumes
