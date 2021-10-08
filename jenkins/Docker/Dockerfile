FROM jenkins/jenkins:2.309-alpine

# Disable Setup Wizard
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false

# Pre-Install plugins
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt

# This is just informational
EXPOSE 8080
EXPOSE 50000
