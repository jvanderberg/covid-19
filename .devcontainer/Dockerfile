FROM continuumio/anaconda3

# Options for common setup script
ARG INSTALL_ZSH="true"
ARG UPGRADE_PACKAGES="false"
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install needed packages and setup non-root user. Use a separate RUN statement to add your own dependencies.
COPY .devcontainer/library-scripts/*.sh /tmp/library-scripts/
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && /bin/bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts

# RUN apt-get update \
#     && apt-get install build-essential -y

# RUN  wget http://www.imagemagick.org/download/ImageMagick.tar.gz \
#     && mkdir ImageMagick && mv ImageMagick.tar.gz ImageMagick \
#     && cd ImageMagick && tar xzvf ImageMagick.tar.gz  --strip=1 \
#     && ./configure && make install

# Copy environment.yml (if found) to a temp locaition so we update the environment. Also
# copy "noop.txt" so the COPY instruction does not fail if no environment.yml exists.
COPY environment.yml* .devcontainer/noop.txt /tmp/conda-tmp/
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; then /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/environment.yml; fi \
    && rm -rf /tmp/conda-tmp

# Install pylint
RUN /opt/conda/bin/pip install pylint
RUN /opt/conda/bin/pip install aiohttp
RUN conda install -y --channel conda-forge cartopy
RUN apt-get update && apt-get install imagemagick -y

ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
