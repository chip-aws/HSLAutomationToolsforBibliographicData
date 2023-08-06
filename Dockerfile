# Use the latest centOS image
# Note that here you can tag a specific version if you want by passing in FROM centos:7 for example
FROM centos
MAINTAINER ITS Middleware <middleware@unc.edu>
 
# These labels are used by OpenShift in order to display information inside the project
LABEL io.k8s.description="Middleware simple application test" \
 io.k8s.display-name="Simple Hello World App" \
 io.openshift.expose-services="8080:http"

USER 1001
EXPOSE 8080

ENTRYPOINT ["/bin/echo hello world"]
