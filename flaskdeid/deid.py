import json
import logging

from annotation import Annotation, AnnotationFactory, unionize_annotations
from flask import Blueprint, render_template, request, session, abort, jsonify, Response, current_app, g
from flaskdeid import medlpInterface
import hutchner
import medlp


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = Blueprint('deid', __name__, url_prefix='/deid')

@bp.route("/annotate", methods=['POST'])
def identify_phi(**kwargs):
    annotations = []
    annotations += [AnnotationFactory.from_medlp(phi) for phi in medlp.annotate_phi(**kwargs)]
    annotations += [AnnotationFactory.from_hutchner(phi) for phi in hutchner.annotate_phi(**kwargs)]
    merged_results = unionize_annotations(annotations)
    return Response(json.dumps([res.to_dict() for res in merged_results]),
                    mimetype=u'application/json')

@bp.route("/resynthesize", methods=['POST'])
def resynthesize_text(**kwargs):
    if not request.json or not 'deid_text' in request.json:
        abort(400)

    deid_text = request.json['deid_text']
    resynth_results = _resynthesize(deid_text, **kwargs)

    return Response(json.dumps(resynth_results), mimetype=u'application/json')

def _resynthesize(annotated_text, **kwargs):
    return Response("To be Implemented!", status=501)

