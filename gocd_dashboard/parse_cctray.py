from collections import defaultdict
from xml.etree import ElementTree as Et


class Projects(object):
    def __init__(self, fn):
        self.tree = Et.parse(fn)
        self.activities = defaultdict(list)
        self.pipelines = {}
        self.stages = defaultdict(list)
        self.jobs = defaultdict(list)
        self.stages = defaultdict(list)
        self.parse()

    def parse(self):
        for project in self.tree.findall('Project'):
            self.activities[project.attrib['activity']].append(project)
            name_parts = [n.strip() for n in project.attrib['name'].split('::')]
            pipeline_name = name_parts[0]
            stage_name = name_parts[1]
            if len(name_parts) > 2:
                job_name = name_parts[2]
            else:
                job_name = None
            if pipeline_name not in self.pipelines:
                self.pipelines[pipeline_name] = Pipeline()
            self.pipelines[pipeline_name].add_facts(project)
            if len(name_parts) == 2:
                self.stages[pipeline_name].append(stage_name)
            if len(name_parts) == 3:
                self.jobs[(pipeline_name, stage_name)].append(job_name)


class Pipeline(object):
    def __init__(self):
        self.activity_set = set()
        self.last_build_set = set()
        self.status = None

    def add_facts(self, project):
        self.activity_set.add(project.attrib['activity'])
        self.last_build_set.add(project.attrib['lastBuildStatus'])
        prefix = "Building after " if "Building" in self.activity_set else ""
        suffix = "Failure" if "Failure" in self.last_build_set else "Success"
        self.status = prefix + suffix