FROM ubuntu:jammy

ARG TERRAFORM_VERSION
ENV TERRAFORM_ZIP="terraform_${TERRAFORM_VERSION}_linux_amd64.zip"

WORKDIR /usr/src

RUN sudo apt-get update -y && \
    sudo apt-get install -y unzip wget

RUN wget "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/${TERRAFORM_ZIP}" \
    && unzip ${TERRAFORM_ZIP} \
    && mv terraform /usr/local/bin/ \
    && rm ${TERRAFORM_ZIP} \
    && terraform --version

# Install python and tflocal
RUN sudo apt-get install -y python3-pip \
    && pip3 install terraform-local
