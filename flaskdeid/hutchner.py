import json
import logging

from flask import Blueprint, render_template, request, session, abort, jsonify, Response, current_app, g


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = Blueprint('hutchner', __name__, url_prefix='/hutchner')



@bp.route("/annotate/", methods=['POST'])
def annotate(**kwargs):
    if not request.json or not 'extract_text' in request.json:
        abort(400)

    note_text = request.json['extract_text']
    if note_text:
        return _get_entities(note_text, **kwargs)
    else:
        msg = "No Entity Text was found"
        logger.info("No entities returned")
        return Response(msg, status=400)

@bp.route("/annotate/phi", methods=['POST'])
def annotate_phi():
    return annotate(entityTypes=["PROTECTED_HEALTH_INFORMATION"])

def _get_entities(note_text, **kwargs):
    return Response("To be Implemented!", status=501)