from unittest import TestCase

from flaskphiid.annotation import Annotation, AnnotationFactory, MergedAnnotation
from flaskphiid.annotation import unionize_annotations


class AnnotationTest(TestCase):

    def setUp(self):
        # sample text
        self.sample_text = ("Patient is Mr. John Smith Jr., a 48-year-old "
            "teacher and chef. His phone number is (555) 867-5309, "
            "and his address is 123 Sesame St, Seattle, WA 99999. "
            "Test.")
        # sample MedLP results
        self.sample_compmed = [
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
                "label": "HOSPITAL_NAME"
            },
            {
                "start": 142,
                "stop": 150,
                "confidence": 0.06,
                "text": "WA 99999",
                "label": "HOSPITAL_NAME"
            },
            {
                "start": 152,
                "stop": 156,
                "confidence": 0.07,
                "text": "Test",
                "label": "URL_OR_IP"
            }
        ]
        #text to test compound annotations
        self.sample_compound_type_text = (
            "John Smith Jr. is being seen at"
            " 123 Sesame Hospital"
            " Ward 3 Sick Burns Unit"
            " Seattle, WA 99999")
        self.sample_compound_compmed = [
            {
                "Id": 0,
                "BeginOffset": 32,
                "EndOffset": 92,
                "Score": 0.99,
                "Text": "123 Sesame Hospital Ward 3 Sick Burns Unit Seattle, WA 99999",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "ADDRESS",
                "Traits": []
            },
        ]
        self.sample_compound_hutchner = [
            {
                "start": 32,
                "stop": 51,
                "confidence": 0.01,
                "text": "123 Sesame Hospital",
                "label": "HOSPITAL_NAME"
            },
            {
                "start": 51,
                "stop": 58,
                "confidence": 0.01,
                "text": "Ward 3",
                "label": "WARD"
            },
            {
                "start": 59,
                "stop": 74,
                "confidence": 0.01,
                "text": "Sick Burns Unit",
                "label": "SPECIALTY"
            },
        ]


    def tearDown(self):
        pass

    def test_annotation_empty(self):
        ann1 = Annotation('test')
        self.assertTrue(ann1.empty())
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        self.assertFalse(ann2.empty())

    def test_annotation_from_compmed(self):
        for sample in self.sample_compmed:
            ann = AnnotationFactory.from_compmed(sample)
            self.assertEqual(ann.origin, 'compmed')
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
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[0])
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
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        data = merged.to_dict()
        self.assertEqual(data['origin'], 'merged')
        self.assertEqual(data['text'], 'Patient is Mr. John Smith Jr.')
        self.assertTrue('compmed' in data['source_origins'])
        detailed = merged.to_dict(detailed=True)
        self.assertEqual(len(detailed['source_annotations']), 2)

    def test_mergedannotation_type_merge_matching(self):
        # matching type case
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[1])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[1])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

    def test_mergedannotation_type_matching_parent_low_score(self):
        # matching type/parent-type case; score < threshold
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

    def test_mergedannotation_type_matching_parent_high_score_scnd_anno(self):
        # matching type/parent-type case; score > threshold
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann2.score = 0.8
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann2.type)
        self.assertEqual(merged.score, ann2.score)

    def test_mergedannotation_type_matching_parent_high_score_first_anno(self):
        # matching parent-type/type case; score > threshold
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann2.score = 0.8
        merged = AnnotationFactory.from_annotations([ann2, ann1])
        self.assertEqual(merged.type, ann2.type)
        self.assertEqual(merged.score, ann2.score)

    def test_mergedannotation_type_matching_parent_low_score(self):
        # matching parent-type/type case; score < threshold
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann2.score = 0.4
        merged = AnnotationFactory.from_annotations([ann2, ann1])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

    def test_mergedannotation_type_matching_parent_diff_child_hi_score(self):
        # matching parent-type/parent-type case; score1 > score2
        ann1 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann1.score = 0.6
        ann2.type = "PROVIDER_NAME"
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

    def test_mergedannotation_type_matching_parent_diff_child_low_score(self):
        # matching parent-type/parent-type case; score1 < score2
        ann1 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[0])
        ann2.score = 0.8
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, ann2.type)
        self.assertEqual(merged.score, ann2.score)

    def test_mergedannotation_type_matching_parent_compound_child_maps(self):
        # matching parent-type/parent-type case; score1 > score2, 3, 4
        ann1 = AnnotationFactory.from_compmed(self.sample_compound_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_compound_hutchner[0])
        ann3 = AnnotationFactory.from_hutchner(self.sample_compound_hutchner[1])
        ann4 = AnnotationFactory.from_hutchner(self.sample_compound_hutchner[2])

        merged = AnnotationFactory.from_annotations([ann1, ann2, ann3, ann4])
        #Do we end up with the parent type after compound mapping?
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

    def test_mergedannotation_type_matching_parent_compound_child_maps(self):
        # matching parent-type/parent-type case; score1 > score2, 3, 4
        ann1 = AnnotationFactory.from_compmed(self.sample_compound_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_compound_hutchner[0])
        ann3 = AnnotationFactory.from_hutchner(self.sample_compound_hutchner[1])
        ann4 = AnnotationFactory.from_hutchner(self.sample_compound_hutchner[2])
        ann2.score = 0.8
        ann3.score = 0.8
        ann4.score = 0.8

        merged = AnnotationFactory.from_annotations([ann1, ann2, ann3, ann4])
        # Do we end up with the parent type after compound mapping?
        self.assertEqual(merged.type, ann1.type)
        self.assertEqual(merged.score, ann1.score)

    def test_mergedannotation_type_mismatched_parent_type(self):
        # mismatched parent-type/parent-type case
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[5])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[6])
        merged = AnnotationFactory.from_annotations([ann1, ann2])
        self.assertEqual(merged.type, "UNKNOWN")

    def test_mergedannotation_invalid_cases(self):
        self.assertRaises(ValueError, AnnotationFactory.from_annotations, [])
        self.assertRaises(ValueError, MergedAnnotation().add_annotation,
                          Annotation('test'))

        # attempt to combine non-overlapping annotations
        ann1 = AnnotationFactory.from_compmed(self.sample_compmed[0])
        ann2 = AnnotationFactory.from_hutchner(self.sample_hutchner[3])
        ma = AnnotationFactory.from_annotations([ann1])
        self.assertRaises(ValueError, ma.add_annotation, ann2)

    def test_unionize_annotations(self):
        anns = [AnnotationFactory.from_compmed(ann) for ann in self.sample_compmed]
        anns += [AnnotationFactory.from_hutchner(ann) for ann in self.sample_hutchner]
        union = unionize_annotations(anns)

        self.assertEqual(len(union), 7)
        for merged in union:
            self.assertEqual(merged.text,
                             self.sample_text[merged.start:merged.end])
        self.assertEqual(len(union[5].source_annotations), 3)
        self.assertEqual(len(union[5].source_origins), 2)
