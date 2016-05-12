scrapyd-deploy -l
scrapyd-deploy default -p lj_pudong
curl http://localhost:6800/schedule.json -d project=lj_pudong -d spider=lj_ny
scrapyd-deploy scrapyd -p project1 --version 54	
curl http://localhost:6800/cancel.json -d project=myproject -d job=6487ec79947edab326d6db28a2d86511e8247444

server {
        listen 6801;
 
        location ~ /\.ht {
                deny all;
        }
 
        location / {
                proxy_pass            http://127.0.0.1:6800/;
                auth_basic            "Restricted";
                auth_basic_user_file  /etc/nginx/conf.d/.htpasswd;
        }
}
