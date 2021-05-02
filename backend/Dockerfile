FROM python:3.7

# download dependencies for backend
RUN apt-get update
RUN git clone https://github.com/Mr-Geekman/english_test_solver.git

# change working directory for instructions below
WORKDIR english_test_solver/backend

# install dependencies
RUN pip install torch==1.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir -r requirements.txt 

# download models for backend
RUN mkdir models/BertBase
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/config.json -O models/BertBase/config.json
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/vocab.txt -O models/BertBase/vocab.txt
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/pytorch_model.bin -O models/BertBase/pytorch_model.bin

# make migrations
RUN python manage.py makemigrations && python manage.py migrate

# run server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
