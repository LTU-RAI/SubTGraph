FROM fernand0labra/blender:latest

RUN apt-get update \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install \
        pyyaml==6.0.3 \
        numpy==1.26.4 \
        mathutils==3.3.0 \
        seaborn==0.13.2 \
        matplotlib==3.5.1 \
        scipy==1.15.3 \
        torchmetrics==1.7.4 \
        torch==2.0.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/blender/

EXPOSE 22
CMD [ "/usr/sbin/sshd", "-D" ]