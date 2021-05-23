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
RUN mkdir models/BertBase
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/config.json -O models/BERTBase/config.json
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/vocab.txt -O models/BERTBase/vocab.txt
RUN wget https://huggingface.co/bert-base-uncased/resolve/main/pytorch_model.bin -O models/BERTBase/pytorch_model.bin

RUN mkdir models/GPTBase
RUN wget https://huggingface.co/gpt2/resolve/main/config.json -O models/GPTBase/config.json
RUN wget https://huggingface.co/gpt2/resolve/main/vocab.json -O models/GPTBase/vocab.json
RUN wget https://huggingface.co/gpt2/resolve/main/merges.txt -O models/GPTBase/merges.txt
RUN wget https://huggingface.co/gpt2/resolve/main/pytorch_model.bin -O models/GPTBase/pytorch_model.bin

# make migrations
RUN python manage.py makemigrations && python manage.py migrate

# run server
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
