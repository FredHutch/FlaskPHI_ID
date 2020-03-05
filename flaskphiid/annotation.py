"""Module for standardizing and combining annotations"""
from operator import attrgetter

# map hutchner labels to appriate comp med labels
HUTCHNER_TYPE_MAP = {
    "WARD": "ADDRESS",
    "SPECIALTY":"ADDRESS",
    "HOSPITAL_NAME": "ADDRESS",
    "MEDICAL_RECORD_NUMBER": "ID",
    "PATIENT_OR_FAMILY_NAME": "NAME",
    "PROVIDER_NAME": "NAME",
    "EMPLOYER": "PROFESSION"
}
TYPE_THRESHOLD = 0.5

class IncompatibleTypeException(Exception):
    def __init__(self, message, type_set):
        additional_info = "previous types: {type_set}".format(type_set=type_set)
        full_message = ":\n ".join([message, additional_info])
        super(IncompatibleTypeException, self).__init__(full_message)
        self.type_set = type_set


class AnnotationFactory:

    def __init__(self):
        pass

    @staticmethod
    def from_compmed(compmed):
        ann = Annotation('compmed')
        ann.start = compmed.get('BeginOffset')
        ann.end = compmed.get('EndOffset')
        ann.score = compmed.get('Score')
        ann.type = compmed.get('Type')
        ann.text = compmed.get('Text')
        return ann

    @staticmethod
    def from_hutchner(hutchner):
        ann = Annotation('hutchner')
        ann.start = hutchner.get('start')
        ann.end = hutchner.get('stop')
        ann.score = hutchner.get('confidence')
        ann.type = hutchner.get('label')
        ann.text = hutchner.get('text')
        ann.type_map = HUTCHNER_TYPE_MAP
        return ann

    @staticmethod
    def from_annotations(anns):
        if not anns:
            raise ValueError("annotation list cannot be empty")
        merged = MergedAnnotation()
        for ann in anns:
            merged.add_annotation(ann)
        if merged.has_compatible_family_typelist:
            return merged.split_annotations_by_subtypes()

        return [merged]

    @staticmethod
    def from_unsplittable_annotations(anns):
        if not anns:
            raise ValueError("annotation list cannot be empty")
        merged = MergedAnnotation()
        for ann in anns:
            merged.add_annotation(ann)

        return [merged]


class Annotation(object):

    def __init__(self, origin):
        self.origin = origin
        self.start = None
        self.end = None
        self.score = None
        self.text = None
        self._type = None
        self.type_map = {}

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        self._type = t.upper() if t else None

    @property
    def parent_type(self):
        return self.type_map.get(self.type, self.type)

    def empty(self):
        return not (self.start is not None and self.end is not None and self.text and self.type)

    def to_dict(self):
        data = {}
        data['origin'] = self.origin
        data['start'] = self.start
        data['end'] = self.end
        data['score'] = self.score
        data['type'] = self.type
        data['text'] = self.text
        return data


class MergedAnnotation(Annotation):

    def __init__(self):
        super().__init__('merged')
        self.source_annotations = []

    @property
    def source_types(self):
        return set([ann.type for ann in self.source_annotations])

    @property
    def source_parent_types(self):
        return set([ann.parent_type for ann in self.source_annotations])

    @property
    def source_scores(self):
        return [ann.score for ann in self.source_annotations]

    @property
    def source_origins(self):
        return set([ann.origin for ann in self.source_annotations])

    @property
    def type(self):
        if len(self.source_types) == 1:
            return self.source_annotations[0].type
        elif len(self.source_parent_types) == 1:
            subtypes = [x for x in self.source_annotations if (x.type != x.parent_type)]
            top = max(subtypes, key=attrgetter('score'))
            if top.score >= TYPE_THRESHOLD:
                return top.type
            return self.source_annotations[0].parent_type
        return "UNKNOWN"

    @type.setter
    def type(self, t):
        pass

    @property
    def has_compatible_family_typelist(self):
        return self.type != 'UNKNOWN'

    @property
    def score(self):
        if len(self.source_types) == 1:
            return max([x.score for x in self.source_annotations])
        elif len(self.source_parent_types) == 1:
            subtypes = [x for x in self.source_annotations if (x.type != x.parent_type)]
            top_score = max([x.score for x in subtypes])
            if top_score >= TYPE_THRESHOLD:
                return top_score
            return max([x.score for x in self.source_annotations])
        return TYPE_THRESHOLD

    @score.setter
    def score(self, t):
        pass

    def add_annotation(self, ann):
        if ann.empty():
            raise ValueError("new annotation cannot be empty")
        elif self.empty():
            self.text = ann.text
            self.start = ann.start
            self.end = ann.end
            self.type_map = ann.type_map
        elif (self.end < ann.start) or (self.start > ann.end):
            raise ValueError("annotation text must overlap")
        else:
            if (self.start <= ann.start):
                self.text = self.text + ann.text[(self.end-ann.start):]
            else:
                self.text = ann.text + self.text[(ann.end-self.start):]
            self.start = min([self.start, ann.start])
            self.end = max([self.end, ann.end])
            self.type_map = self.type_map or ann.type_map
        self.source_annotations.append(ann)

    def split_annotations_by_subtypes(self):
        if len(self.source_types) == 1:
            return self.source_annotations

        if len(self.source_parent_types) == 1:
            subtypes = [x for x in self.source_annotations if (x.type != x.parent_type)]
            subtyped_annotations = []
            running_annos = []
            for anno in self.source_annotations:
                if not running_annos or anno.type == running_annos[-1].type:
                    running_annos.append(anno)
                    continue
                subtyped_annotations.extend(AnnotationFactory.from_unsplittable_annotations(running_annos))
                running_annos = [anno]
            subtyped_annotations.extend(AnnotationFactory.from_unsplittable_annotations(running_annos))

            return subtyped_annotations

        raise IncompatibleTypeException("Cannot split by subtype for multiple parent types", self.source_parent_types)

    def to_dict(self, detailed=False):
        data = super().to_dict()
        data['source_types'] = list(self.source_types)
        data['source_scores'] = self.source_scores
        data['source_origins'] = list(self.source_origins)
        if detailed:
            data['source_annotations'] = [ann.to_dict() for ann in self.source_annotations]
        return data


def unionize_annotations(annotations):
    if not annotations:
        return []
    sorted_anns = sorted(annotations, key=lambda x: x.start)
    final_anns = []
    current_anns = []
    for idx in range(0, max([ann.end for ann in annotations])):
        # check if current annotations end at idx
        if current_anns and all((ann.end <= idx) for ann in current_anns):
            final_anns.extend(AnnotationFactory.from_annotations(current_anns))
            current_anns = []
        # get all new annotations at idx
        while sorted_anns and (sorted_anns[0].start == idx):
            current_anns.append(sorted_anns.pop(0))
    if current_anns:
        final_anns.extend(AnnotationFactory.from_annotations(current_anns))
    return final_anns
