export PORT=2222
docker pull searxng/searxng
# possibly incorporate this into the systemd service
docker run --restart=always \
             -d -p ${PORT}:8080 \
             -v "${PWD}/searxng:/etc/searxng" \
             -e "BASE_URL=http://localhost:$PORT/" \
             -e "INSTANCE_NAME=my-instance" \
             searxng/searxng
