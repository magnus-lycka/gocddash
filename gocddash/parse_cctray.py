from collections import defaultdict
from xml.etree import ElementTree as Et


class Projects(object):
    def __init__(self, source):
        try:
            self.tree = Et.fromstring(source)
        except TypeError:
            self.tree = Et.parse(source)
        self.pipelines = {}
        self.stages = defaultdict(list)
        self.jobs = defaultdict(list)
        self.parse()

    def parse(self):
        for project in self.tree.findall('Project'):
            name_parts = [n.strip() for n in project.attrib['name'].split('::')]
            project.pipeline_name = name_parts[0]
            project.stage_name = name_parts[1]
            if len(name_parts) > 2:
                project.job_name = name_parts[2]
            else:
                project.job_name = None
            if project.pipeline_name not in self.pipelines:
                self.pipelines[project.pipeline_name] = Pipeline()
            self.pipelines[project.pipeline_name].add_facts(project)

    @staticmethod
    def all_which(entity):
        return True

    @staticmethod
    def progress_which(entity):
        return entity.status != 'Success'

    @staticmethod
    def failing_which(entity):
        return 'Failure' in entity.status

    @staticmethod
    def time_key(enity):
        return enity.changed

    def select(self, which, groups=None, group_map=None):
        selection = {
            'all': self.all_which,
            'progress': self.progress_which,
            'failing': self.failing_which,
        }[which]
        pipelines = [p for p in self.pipelines.values() if selection(p)]
        pipelines.sort(key=self.time_key)
        pipelines.reverse()
        if groups:
            pipelines = [pl for pl in pipelines if group_map[pl.name] in groups]
        return pipelines


class Pipeline(object):
    def __init__(self):
        self.activity_set = set()
        self.last_build_set = set()
        self.status = None
        self.changed = None
        self.url = None
        self.name = None
        self.label = None
        self.stages = []
        self.messages = defaultdict(set)

    def add_facts(self, project):
        self.changed = max(self.changed, project.attrib['lastBuildTime'])
        if not self.name:
            self.name = project.pipeline_name
            self.url = project.attrib['webUrl'].rsplit('/', 2)[0].replace('pipelines/', 'pipelines/value_stream_map/')
            self.label = self.url.split('/')[-1]
        if project.stage_name not in [stage.name for stage in self.stages]:
            self.stages.append(Stage(project))
        if project.job_name:
            self.stages[-1].add_job(project)
        self.activity_set.add(project.attrib['activity'])
        self.last_build_set.add(project.attrib['lastBuildStatus'])
        prefix = "Building after " if "Building" in self.activity_set else ""
        suffix = "Failure" if "Failure" in self.last_build_set else "Success"
        self.status = prefix + suffix
        self.add_messages(project)

    def add_messages(self, project):
        for message in project.findall('messages/message'):
            self.messages[message.attrib['kind']].add(message.attrib['text'])


class Entity(object):
    def __init__(self, project):
        prefix = "Building after " if project.attrib['activity'] == "Building" else ""
        self.status = prefix + project.attrib['lastBuildStatus']
        self.url = project.attrib['webUrl']


class Stage(Entity):
    def __init__(self, project):
        super(Stage, self).__init__(project)
        self.jobs = []
        self.name = project.stage_name
        self.counter = self.url.split('/')[-1]

    def add_job(self, project):
        self.jobs.append(Job(project))


class Job(Entity):
    def __init__(self, project):
        super(Job, self).__init__(project)
        self.name = project.job_name
