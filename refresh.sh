if [ $# -lt 1 ]; then
  echo "Error: Please provide the version number as an argument. Example: ./refresh.sh 0.0.1"
  exit 1
fi

kubectl delete deployment sysmodel
docker build --tag sysmodel:$1 . --no-cache
docker tag sysmodel:$1 localhost:5000/sysmodel:latest
docker push localhost:5000/sysmodel:latest
kubectl replace -f sysmodel-deployment.yaml --force
