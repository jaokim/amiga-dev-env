
FROM ubuntu:16.04
 
RUN apt-get update
RUN apt-get --assume-yes install python
RUN echo "deb http://dl.bintray.com/sba1/adtools-deb /" | tee -a /etc/apt/sources.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 379CE192D401AB61
RUN apt-get update
RUN apt-get update --fix-missing
ADD https://raw.githubusercontent.com/sba1/adtools/master/packaging/deb/adtools-sdk/update-adtools-sdk-nonfree /usr/sbin/update-adtools-sdk-nonfree
RUN chmod +x /usr/sbin/update-adtools-sdk-nonfree

RUN apt-get --assume-yes --allow-unauthenticated install adtools-binutils adtools-gcc adtools-sdk-53.30
RUN mkdir -p /usr/ppc-amigaos/SDK/local && chmod a+r /usr/ppc-amigaos/SDK/local

## Add links for pcc-amigaos tools (so Amiga bases makefiles should work
RUN ln /usr/bin/ppc-amigaos-addr2line /usr/bin/addr2line && ln /usr/bin/ppc-amigaos-ar /usr/bin/ar && ln /usr/bin/ppc-amigaos-as /usr/bin/as && ln /usr/bin/ppc-amigaos-c++ /usr/bin/c++ && ln /usr/bin/ppc-amigaos-c++filt /usr/bin/c++filt && ln /usr/bin/ppc-amigaos-cpp /usr/bin/cpp && ln /usr/bin/ppc-amigaos-elfedit /usr/bin/elfedit && ln /usr/bin/ppc-amigaos-g++ /usr/bin/g++ && ln /usr/bin/ppc-amigaos-gcc /usr/bin/gcc && ln /usr/bin/ppc-amigaos-gcc-8.2.0 /usr/bin/gcc-8.2.0 && ln /usr/bin/ppc-amigaos-gcc-ar /usr/bin/gcc-ar && ln /usr/bin/ppc-amigaos-gcc-nm /usr/bin/gcc-nm && ln /usr/bin/ppc-amigaos-gcc-ranlib /usr/bin/gcc-ranlib && ln /usr/bin/ppc-amigaos-gcov /usr/bin/gcov && ln /usr/bin/ppc-amigaos-gcov-dump /usr/bin/gcov-dump && ln /usr/bin/ppc-amigaos-gcov-tool /usr/bin/gcov-tool && ln /usr/bin/ppc-amigaos-gprof /usr/bin/gprof && ln /usr/bin/ppc-amigaos-ld /usr/bin/ld && ln /usr/bin/ppc-amigaos-ld.bfd /usr/bin/ld.bfd && ln /usr/bin/ppc-amigaos-nm /usr/bin/nm && ln /usr/bin/ppc-amigaos-objcopy /usr/bin/objcopy && ln /usr/bin/ppc-amigaos-objdump /usr/bin/objdump && ln /usr/bin/ppc-amigaos-ranlib /usr/bin/ranlib && ln /usr/bin/ppc-amigaos-readelf /usr/bin/readelf && ln /usr/bin/ppc-amigaos-size /usr/bin/size && ln /usr/bin/ppc-amigaos-strings /usr/bin/strings && ln /usr/bin/ppc-amigaos-strip /usr/bin/strip

RUN ln /usr/ppc-amigaos/SDK/ /SDK -s

COPY support-files/conf/dependencies.json /etc/amiga-dependencies.json
## ADD https://sourceforge.net/p/docker-ade/code/HEAD/tree/trunk/support-files/conf/dependencies.json?format=raw /etc/amiga-dependencies.json
RUN chmod +r /etc/amiga-dependencies.json

COPY support-files/sbin/dep-get.py /usr/sbin/dep-get.py
## ADD https://sourceforge.net/p/docker-ade/code/HEAD/tree/trunk/support-files/sbin/install-sdk-dependency.py?format=raw /usr/sbin/install-sdk-dependency.py
RUN chmod +x /usr/sbin/dep-get.py


# RUN apt-get --assume-yes install subversion git make
# COPY support-files/sbin/build.py /usr/sbin/ade-build.py
# ADD https://sourceforge.net/p/docker-ade/code/HEAD/tree/trunk/support-files/sbin/build.py /usr/sbin/ade-build.py
# RUN chmod +x /usr/sbin/ade-build.py

WORKDIR ./workdir
