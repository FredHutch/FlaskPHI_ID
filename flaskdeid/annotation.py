"""Module for standardizing and combining annotations"""
class Annotation(object):
    def __init__(self, origin):
        self.origin = origin
        self.start = None
        self.end = None
        self.score = None
        self.type = None
        self.text = None

    def empty(self):
        return not (self.start and self.end and self.text)

    def from_medlp(medlp):
        ann = Annotation('medlp')
        ann.start = medlp.get('BeginOffset')
        ann.end = medlp.get('EndOffset')
        ann.score = medlp.get('Score')
        ann.type = medlp.get('Type')
        ann.text = medlp.get('Text')
        return ann

    def from_hutchner(hutchner):
        ann = Annotation('hutchner')
        ann.start = hutchner.get('start')
        ann.end = hutchner.get('stop')
        ann.score = hutchner.get('confidence')
        ann.type = hutchner.get('label')
        ann.text = hutchner.get('text')
        return ann

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
    def source_scores(self):
        return [ann.score for ann in self.source_annotations]

    @property
    def source_origins(self):
        return set([ann.origin for ann in self.source_annotations])

    def add_annotation(self, ann):
        if ann.empty():
            raise ValueError("new annotation cannot be empty")
        if self.empty():
            self.text = ann.text
            self.start = ann.start
            self.end = ann.end
            self.type = ann.type
        else:
            if (self.start <= ann.start):
                self.text = self.text + ann.text[(self.end-ann.start):]
            else:
                self.text = ann.text + self.text[(ann.end-self.start):]
            self.start = min([self.start, ann.start])
            self.end = max([self.end, ann.end])
            self.type = "Unknown" if (self.type != ann.type) else self.type
        self.source_annotations.append(ann)

    def from_annotations(anns):
        if not anns:
            raise ValueError("annotation list cannot be empty")
        merged = MergedAnnotation()
        for ann in anns:
            merged.add_annotation(ann)
        return merged

    def to_dict(self, detailed=False):
        data = super().to_dict()
        data['source_types'] = self.source_types
        data['source_scores'] = self.source_scores
        data['source_origins'] = self.source_origins
        if detailed:
            data['source_annotations'] = [ann.to_dict() for ann in self.source_annotations]
        return data


def unionize_annotations(annotations):
    sorted_anns = sorted(annotations, key=lambda x: x.start)
    final_anns = []
    current_anns = []
    for idx in range(0, max([ann.end for ann in annotations])):
        # check if current annotations end at idx
        if current_anns and all((ann.end <= idx) for ann in current_anns):
            final_anns.append(MergedAnnotation.from_annotations(current_anns))
            current_anns = []
        # get all new annotations at idx
        while sorted_anns and (sorted_anns[0].start == idx):
            current_anns.append(sorted_anns.pop(0))
    if current_anns:
        final_anns.append(MergedAnnotation.from_annotations(current_anns))
    return final_anns
