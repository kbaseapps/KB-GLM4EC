FROM kbase/sdkbase2:python
MAINTAINER saeedeh.davoudi@ucdenver.edu
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update
RUN apt-get update
# Install dependencies
RUN pip install --upgrade pip && pip install cython && pip install tensorflow && \
pip install tensorflow_addons && \
pip install numpy && \
pip install pandas && \
pip install h5py && \
pip install lxml && \
pip install pyfaidx && \
pip install IPython && \
pip install joblib

# -----------------------------------------

RUN echo '14' >/dev/null && mkdir deps && cd deps && \
	git clone --branch main https://github.com/cshenry/KBBaseModules.git

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
