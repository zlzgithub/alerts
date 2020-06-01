#!/bin/sh

set +e
set -x

nginx_conf(){
cat <<EOF
upstream app_server_djangoapp {
    server localhost:8000 fail_timeout=0;
}

server {
    listen 8080;
    access_log  /var/log/alerts_access.log;
    error_log  /var/log/alerts_error.log info;
    keepalive_timeout 5;
    root /var/opt/alerts/main;

    location /static {
        autoindex on;
        alias /var/opt/alerts/main/static;
    }

    location / {
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$http_host;
        proxy_redirect off;
        proxy_connect_timeout 75s;
        proxy_read_timeout 300s;

        if (!-f \$request_filename) {
            proxy_pass http://app_server_djangoapp;
            break;
        }
    }
}
EOF
}

main(){
  echo "`date` starting ..." |tee -a /var/log/start.log
  env |tee -a /var/log/start.log

  SERVER_URL=$(echo "$SERVER_URL" |sed 's/\/$//')

  if [ "443" = "$LISTEN_80_443" ] || [ "80" = "$LISTEN_80_443" ]; then
    # mod nginx conf
    server_name=$(echo "$SERVER_URL" |sed 's/https\?:\/\///;s/:.*$//;s/\/$//')
    sed -i "/SERVER_NAME_BEGIN/,/SERVER_NAME_END/s/\(.*server_name\s*\).*$/\1$server_name;/" /etc/nginx/conf.d/alerts.conf
    if [ "80" = "$LISTEN_80_443" ]; then
      sed -i '/HTTPS_BEGIN/,/HTTPS_END/d' /etc/nginx/conf.d/alerts.conf
      sed -i '/FORCE_HTTPS_BEGIN/,/FORCE_HTTPS_END/d' /etc/nginx/conf.d/alerts.conf
    fi
  else
    nginx_conf > /etc/nginx/conf.d/alerts.conf
  fi

  # mod main/templates/monitor/wx2.html.j2
  # sed -i "s#https\?://\w.*\?/#$SERVER_URL/#" $APP_HOME/main/templates/monitor/wx2.html.j2
  sed -i "s#https\?://[^/]\+/#$SERVER_URL/#" main/templates/monitor/wx2.html.j2

  # run
  supervisord -c /etc/supervisord.conf
  echo "`date` started" |tee -a /var/log/start.log
  mkdir -p /run/nginx
  nginx -g 'daemon off;'
}

main