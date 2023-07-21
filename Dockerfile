FROM mx2542/tink:base

ENV KUBENETES_ENV=production

WORKDIR /tink

COPY . /tink

EXPOSE 8003

# RUN apt-get update
# RUN apt-get install -y git curl
# RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
# RUN chmod 700 get_helm.sh
# RUN ./get_helm.sh
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

CMD ["uvicorn","src.main:app","--reload","--port=8003","--host=0.0.0.0" ]
