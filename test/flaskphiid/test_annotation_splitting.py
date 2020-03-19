from unittest import TestCase

from flaskphiid.annotation import Annotation, AnnotationFactory, MergedAnnotation
from flaskphiid.annotation import unionize_annotations
from flaskphiid.annotation import IncompatibleTypeException


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

    def make_sorted_annotation_list(self, compmed_annos, hutchner_annos):
        anns = [AnnotationFactory.from_compmed(ann) for ann in compmed_annos]
        anns += [AnnotationFactory.from_hutchner(ann) for ann in hutchner_annos]
        sorted_anns = sorted(anns, key=lambda x: x.start)

        return sorted_anns

    def test_split_annotations_single_subtype_no_split(self):
        sample_compound_type_text = (
            "123 Sesame Hospital"
            " Ward 3 Sick Burns Unit"
            " Seattle, WA 99999")
        sample_compound_compmed = [
            {
                "Id": 0,
                "BeginOffset": 0,
                "EndOffset": 60,
                "Score": 0.99,
                "Text": "123 Sesame Hospital Ward 3 Sick Burns Unit Seattle, WA 99999",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "ADDRESS",
                "Traits": []
            },
        ]
        sample_compound_hutchner = [
            {
                "start": 0,
                "stop": 19,
                "confidence": 0.01,
                "text": "123 Sesame Hospital",
                "label": "HOSPITAL_NAME"
            },
            {
                "start": 20,
                "stop": 26,
                "confidence": 0.01,
                "text": "Ward 3",
                "label": "HOSPITAL_NAME"
            },
            {
                "start": 27,
                "stop": 42,
                "confidence": 0.01,
                "text": "Sick Burns Unit",
                "label": "HOSPITAL_NAME"
            },
        ]
        anns = self.make_sorted_annotation_list(sample_compound_compmed, sample_compound_hutchner)

        merged = MergedAnnotation()
        for ann in anns:
            merged.add_annotation(ann)
        self.assertNotEqual(merged.type, "UNKNOWN")
        self.assertEqual(merged.type, "HOSPITAL_NAME")

        actual = merged.split_annotations_by_subtypes()
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].type, "HOSPITAL_NAME")



    def test_split_annotations_by_subtypes_multi_type_type_exception(self):
        anns = [AnnotationFactory.from_compmed(self.sample_compmed[5])]
        anns += [AnnotationFactory.from_hutchner(self.sample_hutchner[6])]
        sorted_anns = sorted(anns, key=lambda x: x.start)
        merged = MergedAnnotation()
        for ann in sorted_anns:
            merged.add_annotation(ann)
        self.assertEqual(merged.type, "UNKNOWN")
        with self.assertRaises(IncompatibleTypeException) as context:
            actual = merged.split_annotations_by_subtypes()
        self.assertTrue("URL_OR_IP" in context.exception.type_set)
        self.assertTrue("NAME" in context.exception.type_set)

    def test_split_annotations_by_subtypes_multitype_perfect_line_up(self):
        '''
        assert that when we attempt split a merged annotation that is all of multiple child types, same parent type,
        AND the offset of the first and last child tokens matches the first/last offset of the merged annotation,
        we return the child annotations (self.source_child_annotations) as a list
        :return:  [self]
        '''


        sample_compound_type_text = (
            "123 Sesame Hospital"
            " Ward 3 Sick Burns Unit")
        sample_compound_compmed = [
            {
                "Id": 0,
                "BeginOffset": 0,
                "EndOffset": 42,
                "Score": 0.99,
                "Text": "123 Sesame Hospital Ward 3 Sick Burns Unit",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "ADDRESS",
                "Traits": []
            },
        ]
        sample_compound_hutchner = [
            {
                "start": 0,
                "stop": 19,
                "confidence": 0.01,
                "text": "123 Sesame Hospital",
                "label": "HOSPITAL_NAME"
            },
            {
                "start": 20,
                "stop": 26,
                "confidence": 0.01,
                "text": "Ward 3",
                "label": "WARD"
            },
            {
                "start": 27,
                "stop": 42,
                "confidence": 0.01,
                "text": "Sick Burns Unit",
                "label": "SPECIALTY"
            },
        ]
        anns = self.make_sorted_annotation_list(sample_compound_compmed, sample_compound_hutchner)

        merged = MergedAnnotation()
        for ann in anns:
            merged.add_annotation(ann)
        self.assertNotEqual(merged.type, "UNKNOWN")
        self.assertEqual(merged.type, "ADDRESS")

        actual = merged.split_annotations_by_subtypes()
        self.assertEqual(len(actual), 3)
        self.assertEqual(actual[0].type, "HOSPITAL_NAME")
        self.assertEqual(actual[1].type, "WARD")
        self.assertEqual(actual[2].type, "SPECIALTY")


    def test_split_annotations_by_subtypes_multitype_underline_up(self):
        '''
        assert that when we attempt split a merged annotation that is all of multiple child types, same parent type,
        AND the offset of the first and last child tokens DO NOT matche the first/last offset of the merged annotation,
        we return the child annotations (self.source_child_annotations) as a list
        :return:  [self]
        '''
        sample_compound_type_text = (
            "123 Sesame Hospital"
            " Ward 3 Sick Burns Unit")
        sample_compound_compmed = [
            {
                "Id": 0,
                "BeginOffset": 0,
                "EndOffset": 54,
                "Score": 0.99,
                "Text": "123 Sesame Hospital Ward 3 Sick Burns Unit, Seattle WA",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "ADDRESS",
                "Traits": []
            },
        ]
        sample_compound_hutchner = [
            {
                "start": 0,
                "stop": 19,
                "confidence": 0.01,
                "text": "123 Sesame Hospital",
                "label": "HOSPITAL_NAME"
            },
            {
                "start": 20,
                "stop": 26,
                "confidence": 0.01,
                "text": "Ward 3",
                "label": "WARD"
            },
            {
                "start": 27,
                "stop": 42,
                "confidence": 0.01,
                "text": "Sick Burns Unit",
                "label": "SPECIALTY"
            },
        ]
        anns = self.make_sorted_annotation_list(sample_compound_compmed, sample_compound_hutchner)

        merged = MergedAnnotation()
        for ann in anns:
            merged.add_annotation(ann)
        self.assertNotEqual(merged.type, "UNKNOWN")
        self.assertEqual(merged.type, "ADDRESS")

        actual = merged.split_annotations_by_subtypes()
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0], merged)




