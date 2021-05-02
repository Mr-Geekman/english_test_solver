FROM python:3.7

fix problem with timezon
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# clone repository (add later)

# download dependencies for backend
RUN apt-get update && apt-get upgrade -y
RUN pip install torch==1.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
# заменить на pip install -r requirements.txt
RUN pip install transformers django djangorestframework importlib_metadata

# download models for backend
# создать еще и соответствующие директории
# https://huggingface.co/bert-base-uncased/tree/main

# start container in compiled library
# WORKDIR ~/PatternsCollection
