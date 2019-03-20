from unittest import TestCase

from flaskdeid.annotation import Annotation, AnnotationFactory, MergedAnnotation
from flaskdeid.annotation import unionize_annotations


class AnnotationTest(TestCase):

    def setUp(self):
        # sample text
        self.sample_text = ("Patient is Mr. John Smith Jr., a 48-year-old "
            "teacher and chef. His phone number is (555) 867-5309, "
            "and his address is 123 Sesame St, Seattle, WA 99999. "
            "Test.")
        # sample MedLP results
        self.sample_medlp = [
            {
                "Id": 0,
                "BeginOffset": 0,
                "EndOffset": 25,
                "Score": 0.99,
                "Text": "Patient is Mr. John Smith",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "NAME",
                "Traits": []
            },
            {
                "Id": 1,
                "BeginOffset": 33,
                "EndOffset": 35,
                "Score": 0.98,
                "Text": "48",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "AGE",
                "Traits": []
            },
            {
                "Id": 2,
                "BeginOffset": 45,
                "EndOffset": 52,
                "Score": 0.97,
                "Text": "teacher",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "PROFESSION",
                "Traits": []
            },
            {
                "Id": 3,
                "BeginOffset": 83,
                "EndOffset": 97,
                "Score": 0.96,
                "Text": "(555) 867-5309",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "PHONE_OR_FAX",
                "Traits": []
            },
            {
                "Id": 4,
                "BeginOffset": 122,
                "EndOffset": 144,
                "Score": 0.95,
                "Text": "Sesame St, Seattle, WA",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "ADDRESS",
                "Traits": []
            },
            {
                "Id": 5,
                "BeginOffset": 152,
                "EndOffset": 156,
                "Score": 0.94,
                "Text": "Test",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "NAME",
                "Traits": []
            }
        ]
        # sample HutchNER results
        self.sample_hutchner = [
            {
                "start": 15,
                "stop": 29,
                "confidence": 0.01,
                "text": "John Smith Jr.",
                "label": "PATIENT_OR_FAMILY_NAME"
            },
            {
                "start": 33,
                "stop": 44,
                "confidence": 0.02,
                "text": "48-year-old",
                "label": "AGE"
            },
            {
                "start": 57,
                "stop": 61,
                "confidence": 0.03,
                "text": "chef",
                "label": "PROFESSION"
            },
            {
                "start": 89,
                "stop": 97,
                "confidence": 0.04,
                "text": "867-5309",
                "label": "PHONE_NUMBER"
            },
            {
                "start": 118,
                "stop": 131,
                "confidence": 0.05,
                "text": "123 Sesame St",
                "label": "ADDRESS_AND_COMPONENTS"
            },
            {
                "start": 142,
                "stop": 150,
                "confidence": 0.06,
                "text": "WA 99999",
                "label": "ADDRESS_AND_COMPONENTS"
            },
            {
                "start": 152,
                "stop": 156,
                "confidence": 0.07,
                "text": "Test",
                "label": "URL_OR_IP"
            }
        ]


    def tearDown(self):
        pass

    def test_annotation_empty(self):
        ann1 = Annotation('test')
        self.assertTrue(ann1.empty())
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        self.assertFalse(ann2.empty())

    def test_annotation_from_medlp(self):
        for sample in self.sample_medlp:
            ann = AnnotationFactory.from_medlp(sample)
            self.assertEqual(ann.origin, 'medlp')
            self.assertEqual(ann.text, sample['Text'])
            self.assertEqual(ann.start, sample['BeginOffset'])

    def test_annotation_from_hutchner(self):
        for sample in self.sample_hutchner:
            ann = AnnotationFactory.from_hutchner(sample)
            self.assertEqual(ann.origin, 'hutchner')
            self.assertEqual(ann.type, sample['label'])
            self.assertEqual(ann.score, sample['confidence'])

    def test_annotation_to_dict(self):
        ann = Annotation('test')
        data = ann.to_dict()
        self.assertEqual(data['origin'], 'test')

    def test_mergedannotation_from_annotations(self):
        ann1 = AnnotationFactory.from_medlp(self.sample_medlp[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.origin, 'merged')
        self.assertEqual(merged.start, ann1.start)
        self.assertEqual(merged.end, ann2.end)
        self.assertEqual(merged.text, "Patient is Mr. John Smith Jr.")

        self.assertEqual(merged.source_origins,
                         set([ann1.origin, ann2.origin]))
        self.assertEqual(merged.source_scores, [ann1.score, ann2.score])
        self.assertTrue(ann1 in merged.source_annotations)

    def test_mergedannotation_to_dict(self):
        ann1 = AnnotationFactory.from_medlp(self.sample_medlp[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        data = merged.to_dict()
        self.assertEqual(data['origin'], 'merged')
        self.assertEqual(data['text'], 'Patient is Mr. John Smith Jr.')
        self.assertTrue('medlp' in data['source_origins'])
        detailed = merged.to_dict(detailed=True)
        self.assertEqual(len(detailed['source_annotations']), 2)

    def test_mergedannotation_type_merge(self):
        # matching type case
        ann1 = AnnotationFactory.from_medlp(self.sample_medlp[1])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[1])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

        # matching type/parent-type case; score < threshold
        ann1 = AnnotationFactory.from_medlp(self.sample_medlp[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

        # matching type/parent-type case; score > threshold
        ann2.score = 0.8
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann2.type)
        self.assertEqual(merged.score, ann2.score)

        # matching parent-type/type case; score > threshold
        merged = AnnotationFactory.from_annotations([ann2, ann1])
        self.assertEqual(merged.type, ann2.type)
        self.assertEqual(merged.score, ann2.score)

        # matching parent-type/type case; score < threshold
        ann2.score = 0.4
        merged = AnnotationFactory.from_annotations([ann2, ann1])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

        # matching parent-type/parent-type case; score1 > score2
        ann1 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann1.score = 0.6
        ann2.type = "PROVIDER_NAME"
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

        # matching parent-type/parent-type case; score1 < score2
        ann2.score = 0.8
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann2.type)
        self.assertEqual(merged.score, ann2.score)

        # mismatched parent-type/parent-type case
        ann1 = AnnotationFactory.from_medlp(self.sample_medlp[5])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[6])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, "UNKNOWN")

    def test_mergedannotation_invalid_cases(self):
        self.assertRaises(ValueError, AnnotationFactory.from_annotations, [])
        self.assertRaises(ValueError, MergedAnnotation().add_annotation,
                          Annotation('test'))

        # attempt to combine non-overlapping annotations
        ann1 = AnnotationFactory.from_medlp(self.sample_medlp[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[3])
        ma = AnnotationFactory.from_annotations([ann1])
        self.assertRaises(ValueError, ma.add_annotation, ann2)

    def test_unionize_annotations(self):
        anns = [AnnotationFactory.from_medlp(ann) for ann in self.sample_medlp]
        anns += [AnnotationFactory.from_hutchner(ann) for ann in self.sample_hutchner]
        union = unionize_annotations(anns)

        self.assertEqual(len(union), 7)
        for merged in union:
            self.assertEqual(merged.text,
                             self.sample_text[merged.start:merged.end])
        self.assertEqual(len(union[5].source_annotations), 3)
        self.assertEqual(len(union[5].source_origins), 2)
