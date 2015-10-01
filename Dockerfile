FROM heroku/cedar:14

# Internally, we arbitrarily use port 3000
ENV PORT 3000

# Which version of Python?
ENV PYTHON_VERSION python-2.7.10

# Add Python binaries to path.
ENV PATH /app/.heroku/python/bin/:$PATH

# Create some needed directories
RUN mkdir -p /app/.heroku/python /app/.profile.d
WORKDIR /app/user

# `init` is kept out of /app so it won't be duplicated on Heroku
# Heroku already has a mechanism for running .profile.d scripts,
# so this is just for local parity
COPY ./init /usr/bin/init

# Install Python
RUN curl -s https://lang-python.s3.amazonaws.com/cedar-14/runtimes/$PYTHON_VERSION.tar.gz | tar zx -C /app/.heroku/python

# Install Pip & Setuptools
RUN curl -s https://bootstrap.pypa.io/get-pip.py | /app/.heroku/python/bin/python

# Export the Python environment variables in .profile.d
RUN echo 'export PATH=/app/usr/local/include:/app/usr/local/bin:$HOME/.heroku/python/bin:$PATH PYTHONUNBUFFERED=true PYTHONHOME=/app/.heroku/python LIBRARY_PATH=/app/.heroku/vendor/lib:/app/.heroku/python/lib:$LIBRARY_PATH LD_LIBRARY_PATH=/app/.heroku/vendor/lib:/app/.heroku/python/lib:$LD_LIBRARY_PATH LANG=${LANG:-en_US.UTF-8} PYTHONHASHSEED=${PYTHONHASHSEED:-random} PYTHONPATH=/app/user/airflow_login:$PYTHONPATH:/app/user' > /app/.profile.d/python.sh
RUN chmod +x /app/.profile.d/python.sh

# Need to install libsasl
#
RUN curl -s ftp://ftp.cyrusimap.org/cyrus-sasl/cyrus-sasl-2.1.26.tar.gz | tar xz -C /tmp
WORKDIR /tmp/cyrus-sasl-2.1.26
RUN ./configure --enable-silent-rules
RUN make DESTDIR=/app install

# Need to install libffi-dev
#
RUN curl -s ftp://sourceware.org/pub/libffi/libffi-3.2.1.tar.gz | tar xz -C /tmp
WORKDIR /tmp/libffi-3.2.1
RUN ./configure
RUN make DESTDIR=/app install
RUN ln -s /app/usr/local/lib/libffi-3.2.1/include/ffi.h /app/usr/local/include/ffi.h
RUN ln -s /app/usr/local/lib/libffi-3.2.1/include/ffitarget.h /app/usr/local/include/ffitarget.h

WORKDIR /app/user

RUN echo 'export PATH=/app/usr/local/include:/app/usr/local/bin:$HOME/.heroku/python/bin:$PATH'
COPY requirements.txt /app/user/
COPY . /app/user
RUN CFLAGS=-I/app/usr/local/include LDFLAGS=-L/app/usr/local/lib /app/.heroku/python/bin/pip install -r requirements.txt

ENTRYPOINT ["/usr/bin/init"]
