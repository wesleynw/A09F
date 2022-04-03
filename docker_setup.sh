docker pull searxng/searxng
# port 2222
# possibly incorporate this into the systemd service
docker run --restart=always \
             -d -p 2222:8080 \
             -v "${PWD}/searxng:/etc/searxng" \
             -e "BASE_URL=http://localhost:2222/" \
             -e "INSTANCE_NAME=my-instance" \
             searxng/searxng

docker run --restart=always \
            --name mongodb -d \
            -p 27017:27017 \
            mongo

