FROM python:3.7

# download dependencies for backend
RUN apt-get update
RUN git clone https://github.com/Mr-Geekman/english_test_solver.git

# change working directory for instructions below
WORKDIR english_test_solver/backend

# install upgrade pip and dependencies
RUN pip install --upgrade pip
RUN pip install torch==1.8.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir -r requirements.txt 

# download models for backend
RUN mkdir models/bert-base-uncased
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/config.json -O models/bert-base-uncased/config.json
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/vocab.txt -O models/bert-base-uncased/vocab.txt
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/pytorch_model.bin -O models/bert-base-uncased/pytorch_model.bin

RUN mkdir models/gpt2
RUN wget https://huggingface.co/gpt2/resolve/main/config.json -O models/gpt2/config.json
RUN wget https://huggingface.co/gpt2/resolve/main/vocab.json -O models/gpt2/vocab.json
RUN wget https://huggingface.co/gpt2/resolve/main/merges.txt -O models/gpt2/merges.txt
RUN wget https://huggingface.co/gpt2/resolve/main/pytorch_model.bin -O models/gpt2/pytorch_model.bin

# make migrations
RUN python manage.py makemigrations && python manage.py migrate

# run server
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
