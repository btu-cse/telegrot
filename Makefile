all: create_cert

build_image: 
	@echo "info - creating docker image with buildpacks"
	pack build --builder=gcr.io/buildpacks/builder:v1 fatiiates/btu-replica-bot

create_cert: 
	@echo "info - creating self-signed ssl certificates"
	openssl req -x509 -out certs/server.crt -keyout certs/server.key \
			-days 365 \
			-newkey rsa:2048 -nodes -sha256 \
			-subj '/CN=localhost'