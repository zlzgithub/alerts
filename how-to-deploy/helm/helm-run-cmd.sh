# 1.
helm repo add \
  --ca-file tls.crt \
  --key-file tls.key \
  --username xxx \
  --password xxxxxx \
  devops https://harbor.keep.com/chartrepo/devops/

helm push -u xxx -p xxxxxx ./ devops

helm repo update

# 2.
helm install --name alerts --namespace test  \
  --set serverURL="http://alerts.keep.com/" \
  --set listen_80_443=no \
  --set image.tag=1.2.5 \
  --set image.pullPolicy=Always \
  --set ingress.hosts[0].host="alerts.keep.com" \
  --set ingress.hosts[0].paths[0]="/" \
  --set ingress.annotations."kubernetes\.io/ingress\.class"= \
  devops/alerts
