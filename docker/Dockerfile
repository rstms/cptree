ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ARG USER
RUN adduser --disabled-password --gecos '' ${USER}
COPY --chmod=0755 entrypoint /entrypoint
ENTRYPOINT ["/entrypoint"]
COPY VERSION /VERSION
USER ${USER}
WORKDIR /home/${USER}
ARG WHEEL
COPY --chown=${USER}:${USER} --chmod=0600 ${WHEEL} .
RUN pip install ${WHEEL}
ENV PATH=/home/${USER}/.local/bin:${PATH}
ARG SERVICE_EXEC
ENV SERVICE_EXEC=${SERVICE_EXEC}
