FROM wulan17/mayuri17:buster

# Clone repo and prepare working directory
RUN git clone -b master https://github.com/wulan17/Mayuri /home/mayuri/ \
    && chmod 777 /home/mayuri

RUN python3 -m pip install -r /home/mayuri/requirements.txt

# Copies config.py (if exists)
COPY ./mayuri/sample_config.py ./mayuri/config.py* /home/mayuri/mayuri/

# Setup Working Directory
WORKDIR /home/mayuri

# Finalization
CMD ["python3","-m","mayuri"]
