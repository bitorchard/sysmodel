docker rm -f registry
docker rmi -f $(docker images --filter=reference="*sysmodel*" -q)
