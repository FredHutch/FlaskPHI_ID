import json
import logging

from flask import Blueprint, render_template, request, session, abort, jsonify, Response, current_app, g
from flaskdeid import medlpInterface
import medlp
import merge
import hutchner


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = Blueprint('deid', __name__, url_prefix='/deid')

@bp.route("/annotate", methods=['POST'])
def identify_phi(**kwargs):
    medlp_phi = medlp.annotate_phi(**kwargs)
    hutchner_phi = hutchner.annotate_phi(**kwargs)
    merged_results = _merge_phi(medlp_phi, hutchner_phi)

    return Response(json.dumps(merged_results), mimetype=u'application/json')

@bp.route("/resynthesize", methods=['POST'])
def resynthesize_text(**kwargs):
    if not request.json or not 'deid_text' in request.json:
        abort(400)

    deid_text = request.json['deid_text']
    resynth_results = _resynthesize(deid_text, **kwargs)

    return Response(json.dumps(resynth_results), mimetype=u'application/json')

def _merge_phi(blob_one, blob_two):
    typed_blob_one = merge._match_types(blob_one, "medlp")
    typed_blob_two = merge._match_types(blob_two, "hutchner")

    merged_blobs = merge._merge_offsets([typed_blob_one, typed_blob_two])

    return Response("Merging PHI results is not yet implemented.", status=501)

def _resynthesize(annotated_text, **kwargs):
    return Response("To be Implemented!", status=501)

