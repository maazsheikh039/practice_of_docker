FROM nginx:latest
LABEL maintainer="Maaz Ghufran <maazsheikh039@gmail.com>"
LABEL version="v1.0"
LABEL description="This image build for practical and learning purpose."
WORKDIR /app
COPY /app /usr/share/nginx/html
EXPOSE 80