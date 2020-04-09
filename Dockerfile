FROM registry.redhat.io/rhel7/rhel:7.6-362

ENV JAVA_HOME /usr/lib/jvm/jdk-11/
ENV PATH $JAVA_HOME/bin:$PATH
ENV CATALINA_HOME /opt/tomcat
ENV PATH $CATALINA_HOME/bin:$PATH

RUN mkdir /usr/lib/jvm

# RUN subscription-manager unregister
RUN subscription-manager register --username ksummersill --password "zxasqw12ZXASQW!@" --auto-attach
RUN yum update -y
RUN yum repolist all
RUN yum -y update; yum clean all
RUN yum -y install nano;
RUN yum -y install wget;
RUN curl -O https://download.java.net/openjdk/jdk11/ri/openjdk-11+28_linux-x64_bin.tar.gz
RUN tar xvf openjdk-11+28_linux-x64_bin.tar.gz -C /usr/lib/jvm
RUN java --version
RUN useradd tomcat
RUN mkdir /opt/tomcat
RUN wget http://apache.spinellicreations.com/tomcat/tomcat-9/v9.0.34/bin/apache-tomcat-9.0.34.tar.gz
RUN tar -zxvf apache-tomcat-9.0.34.tar.gz -C /opt/tomcat --strip-components=1
RUN cd /opt && chown -R tomcat tomcat/
RUN chmod 777 /etc/systemd/system
RUN echo $"[Unit] Description=Apache Tomcat Web Application\Container After=syslog.target network.target\[Service]\Type=forking\Environment=JAVA_HOME=/usr/lib/jvm/jre\Environment=CATALINA_PID=/opt/tomcat/temp/tomcat.pid\Environment=CATALINA_HOME=/opt/tomcat\Environment=CATALINA_BASE=/opt/tomcat\Environment='CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC'\Environment='JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom'\ExecStart=/opt/tomcat/bin/startup.sh\ExecStop=/bin/kill -15 $MAINPID\User=tomcat\Group=tomcat\[Install]\WantedBy=multi-user.target" > /etc/systemd/system/tomcat.service
RUN chmod 777 -R /opt/tomcat/webapps/manager/META-INF
RUN cd /opt/tomcat/webapps/manager/META-INF/
RUN echo $"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Context antiResourceLocking=\"false\" privileged=\"true\"><Manager sessionAttributeValueClassNameFilter=\"java\.lang\.(?:Boolean|Integer|Long|Number|String)|org\.apache\.catalina\.filters\.CsrfPreventionFilter\$LruCache(?:\$1)?|java\.util\.(?:Linked)?HashMap\"/></Context>" > /opt/tomcat/webapps/manager/META-INF/context.xml
RUN cd /opt/tomcat/conf
RUN echo $"<?xml version=\"1.0\" encoding=\"UTF-8\"?><tomcat-users xmlns=\"http://tomcat.apache.org/xml\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://tomcat.apache.org/xml tomcat-users.xsd\" version=\"1.0\"><role rolename=\"manager-script\"/><role rolename=\"admin-gui\"/><role rolename=\"manager-gui\"/><user username=\"tomcat\" password=\"World2k!\" roles=\"admin-gui,manager-gui,manager-script\"/></tomcat-users>" > /opt/tomcat/conf/tomcat-users.xml
COPY server.xml /opt/tomcat/conf/server.xml
#COPY context.xml /opt/tomcat/conf/context.xml
#COPY manager.xml /opt/tomcat/webapps/host-manager/manager.xml
COPY web.xml /opt/tomcat/conf/web.xml 
COPY setenv.sh /opt/tomcat/bin
RUN chmod +x /opt/tomcat/bin/setenv.sh

RUN mkdir /opt/certs
COPY gdig2_bundle.crt /opt/certs/gdig2_bundle.crt
COPY b8e15ee5a0fa8e89.crt /opt/certs/b8e15ee5a0fa8e89.crt

RUN keytool -genkey  -keyalg RSA  -dname "CN=jsvede.bea.com,OU=DRE,O=BEA,L=Denver,S=Colorado,C=US" -keypass zx#asqw_TST456$  -storepass zx#asqw_TST456$ -keystore /opt/certs/tomcat.keystore
RUN yum -y install mod_ssl

VOLUME /opt/tomcat
WORKDIR /opt/tomcat

EXPOSE 8443
CMD ["catalina.sh", "run"]

