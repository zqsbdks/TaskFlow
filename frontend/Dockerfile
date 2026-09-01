FROM nginx:1.27-alpine

RUN rm -rf /usr/share/nginx/html/* \
    && mkdir -p /usr/share/nginx/html/app /usr/share/nginx/html/static

COPY index.html /usr/share/nginx/html/app/index.html
COPY styles.css app.js i18n.js /usr/share/nginx/html/static/
COPY themes /usr/share/nginx/html/static/themes
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
