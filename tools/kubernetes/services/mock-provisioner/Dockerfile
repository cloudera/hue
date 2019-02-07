# Use an official Ubuntu Xenial as a parent image
FROM ubuntu:16.04

# Install Node.js 8 and npm 5
RUN apt-get update
RUN apt-get install -y build-essential curl gettext
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash
RUN apt-get install -y nodejs

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl && mv ./kubectl /usr/local/bin/kubectl

# Install Helm
ENV HELM_FILENAME helm-v2.10.0-linux-amd64.tar.gz
ENV HELM_URL https://storage.googleapis.com/kubernetes-helm/${HELM_FILENAME}

RUN echo $HELM_URL

RUN curl -o /tmp/${HELM_FILENAME} ${HELM_URL} \
  && tar -zxvf /tmp/${HELM_FILENAME} -C /tmp \
  && mv /tmp/linux-amd64/helm /bin/helm \
  && rm -rf /tmp/linux-amd64 \
  && rm -rf /tmp/${HELM_FILENAME}

RUN helm init --client-only

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container
ADD . /app

# Install any needed packages specified in requirements.txt
RUN npm install

CMD ["npm", "start"]
