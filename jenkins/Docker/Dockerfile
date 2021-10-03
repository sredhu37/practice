FROM jenkins/jenkins:2.309-alpine

# Disable Setup Wizard
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false -Dhudson.footerURL=http://richa.abcdpractice.com
# Configuration as Code file path
ENV CASC_JENKINS_CONFIG /var/jenkins_home/casc.yaml

# Pre-Install plugins
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

# Configuration as Code
COPY casc.yaml /tmp/jenkins_home/casc.yaml

USER root
# Install something here
USER jenkins

# This is just informational
EXPOSE 8080
EXPOSE 50000
