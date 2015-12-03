# gocd-dashboard
Status dashboard for Go.CD Continuous Delivery Server

Gocd-dashboard provides an overview of the builds in your
Thoughtworks Go Continuous Delivery server.

You select which pipeline groups you want to monitor,
and whether you only want to see failing builds,
failing builds plus currently building, or all builds.
The builds you selected will be shown in descending
chronological order.

By default, you just see the pipeline name, the current
status, the pipeline label and the latest build time, 
but you can expand the view to see the status of its
stages and jobs, as well as the list of breakers.
There are also links to the current versions of pipelines,
stages and jobs at the go-server.

Gocd-dashboard uses the cctray.xml file from the go-server.

Since gocd-dashboard uses bootstrap, you can easily pimp
it to your liking.
