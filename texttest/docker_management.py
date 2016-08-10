
import sys, os

import docker # if this import fails, run 'sudo pip install docker-py'

class ContainerManager:

    def __init__(self, docker_registry):
        self.docker_client = docker.Client(base_url = os.environ.get("DOCKER_HOST", "tcp://localhost:2375"))
        self.docker_registry = docker_registry

    def start_db_container(self, db_image, db_image_tag, db_port):
        db_image_name = "{}/{}:{}".format(self.docker_registry, db_image, db_image_tag)
        print("starting docker container from image {}".format(db_image_name))
        if not self.image_available(db_image_name):
            self.pull_image(db_image, db_image_tag)

        container = self.docker_client.create_container(image=db_image_name, ports=[5432])
        self.docker_client.start(container=container.get("Id"), port_bindings={5432:db_port})
        print("started docker container with id={}".format(container.get("Id")))
        return container

    def stop_container(self, container):
        print("stopping docker container")
        self.docker_client.stop(container=container.get("Id"))
        self.docker_client.remove_container(container=container.get("Id"))
        print("docker container stopped and removed")


    def pull_image(self, image_name, tag):
        image = "{}/{}".format(self.docker_registry, image_name)
        print("pulling image for {}".format(image))
        for line in self.docker_client.pull(image, tag=tag, stream=True, insecure_registry=self.docker_registry):
            print(line)
        print("image pulled")

    def image_available(self, image_name):
        available_images = [image['RepoTags'] for image in self.docker_client.images()]
        return image_name in available_images
