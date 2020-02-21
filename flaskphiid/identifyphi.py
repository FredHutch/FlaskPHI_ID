import json
import logging

from flaskphiid.annotation import AnnotationFactory, unionize_annotations
from flask import Blueprint, render_template, request, session, abort, jsonify, Response, current_app, g
import flaskphiid.hutchner as hutchner
from flaskphiid import compmedInterface, hutchNERInterface


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = Blueprint('identifyphi', __name__, url_prefix='/identifyphi')


@bp.route("/", methods=['POST'])
def annotate(**kwargs):
    if not request.json or 'extract_text' not in request.json:
        abort(400)

    note_text = request.json['extract_text']

    if note_text:
        return identify_phi(note_text, detailed=request.json.get('annotation_by_source', False), **kwargs)
    else:
        msg = "No Entity Text was found"
        logger.info("No entities returned")
        return Response(msg, status=400)


def identify_phi(note_text, detailed=False, **kwargs):
    annotations = []
    try:
        annotations += [AnnotationFactory.from_compmed(phi) for phi in compmedInterface.get_phi(note_text)]
    except ValueError as e:
        msg = "An error occurred while calling MedLP"
        logger.warning("{}: {}".format(msg, e))
        return Response(msg, status=400)
    try:
        annotations += [AnnotationFactory.from_hutchner(phi) for phi in
                        hutchNERInterface.predict(note_text, **kwargs).NER_token_labels
                        if phi.get('label') != "O"]
    except ValueError as e:
        msg = "An error occurred while calling HutchNER"
        logger.warning("{}: {}".format(msg, e))
        return Response(msg, status=400)
    merged_results = unionize_annotations(annotations)
    return Response(json.dumps([res.to_dict(detailed=detailed) for res in merged_results]),
                    mimetype=u'application/json')
