
import sys, os, time

import docker # if this import fails, run 'sudo pip install docker-py'

class ContainerManager:

    def __init__(self, docker_registry=""):
        self.docker_client = docker.Client(
            base_url=os.environ.get("DOCKER_HOST", "tcp://localhost:2375"),
            version="auto"
        )
        self.docker_registry = docker_registry

    def start_db_container(self, db_image, db_image_tag, db_port, environment=None):
        db_image_name = "{}:{}".format(self._full_image_name(db_image), db_image_tag)
        print("starting docker container from image {}".format(db_image_name))
        if not self.image_available(db_image_name):
            self.pull_image(db_image, db_image_tag)

        container = self.docker_client.create_container(image=db_image_name, ports=[5432], environment=environment)
        self.docker_client.start(container=container.get("Id"), port_bindings={5432:db_port})
        self._wait_for_db_container_to_start(container)
        print("started docker container with id={}".format(container.get("Id")))
        return container

    def _wait_for_db_container_to_start(self, container):
        logs = self.docker_client.logs(container=container.get("Id"), stdout=True, stderr=True, timestamps=False, stream=False)
        i = 0
        while i < 10 and not "database system is ready to accept connections" in logs.decode("UTF-8"):
            time.sleep(0.5)
            logs = self.docker_client.logs(container=container.get("Id"), stdout=True, stderr=True, timestamps=False, stream=False)
            i += 1
        #print(logs.decode("UTF-8"))
        #time.sleep(0.5)
        print("docker container ready to accept connections")
        sys.stdout.flush()

    def stop_container(self, container):
        print("stopping docker container")
        self.docker_client.stop(container=container.get("Id"))
        self.docker_client.remove_container(container=container.get("Id"))
        print("docker container stopped and removed")


    def pull_image(self, image_name, tag):
        image = self._full_image_name(image_name)
        print("pulling image for {}".format(image))
        for line in self.docker_client.pull(image, tag=tag, stream=True, insecure_registry=self.docker_registry):
            print(line)
        print("image pulled")

    def image_available(self, image_name):
        available_images = [image['RepoTags'] for image in self.docker_client.images()]
        return image_name in available_images

    def _full_image_name(self, image_name):
        if self.docker_registry:
            return "{}/{}".format(self.docker_registry, image_name)
        else:
            return image_name
