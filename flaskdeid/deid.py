import json
import logging

from flaskdeid.annotation import AnnotationFactory, unionize_annotations
from flask import Blueprint, render_template, request, session, abort, jsonify, Response, current_app, g
import flaskdeid.hutchner as hutchner
from flaskdeid import medlpInterface, hutchNERInterface


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = Blueprint('deid', __name__, url_prefix='/deid')


@bp.route("/annotate", methods=['POST'])
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
        annotations += [AnnotationFactory.from_medlp(phi) for phi in medlpInterface.get_phi(note_text)]
    except ValueError as e:
        msg = "An error occurred while calling MedLP"
        logger.warning("{}: {}".format(msg, e))
        return Response(msg, status=400)
    try:
        annotations += [AnnotationFactory.from_hutchner(phi) for phi in
                        hutchNERInterface.predict(note_text, **kwargs).NER_token_labels]
    except ValueError as e:
        msg = "An error occurred while calling HutchNER"
        logger.warning("{}: {}".format(msg, e))
        return Response(msg, status=400)
    merged_results = unionize_annotations(annotations)
    return Response(json.dumps([res.to_dict(detailed=detailed) for res in merged_results]),
                    mimetype=u'application/json')


@bp.route("/resynthesize", methods=['POST'])
def resynthesize_text(**kwargs):
    if not request.json or 'deid_text' not in request.json:
        abort(400)

    deid_text = request.json['deid_text']
    resynth_results = _resynthesize(deid_text, **kwargs)

    return Response(json.dumps(resynth_results), mimetype=u'application/json')


def _resynthesize(annotated_text, **kwargs):
    return Response("To be Implemented!", status=501)
