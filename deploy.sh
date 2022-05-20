# make sure the localhost has the same version of the code as the remote server
git pull

# re-deploy the image
docker-compose pull
docker-compose down --remove-orphans
docker-compose up --detach

# clean up docker garbage to preserve disc space.
docker system prune --force --all --volumes
