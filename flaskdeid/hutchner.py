import json
import logging

from flask import Blueprint, render_template, request, session, abort, jsonify, Response, current_app, g
from flaskdeid import hutchNERInterface

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
    try:
        if 'entityTypes' in kwargs and kwargs['entityTypes'] == ["PROTECTED_HEALTH_INFORMATION"]:
            entities = hutchNERInterface.predict(note_text).to_json()
    except ValueError as e:
        msg = "An error occurred while calling HutchNER"
        logger.warning("An error occurred while calling HutchNER: {}".format(e))
        return Response(msg, status=400)

    logger.info("{} entities returned for entity types".format(len(entities)))
    logger.info("entities: {}".format(entities))
    return Response(entities, mimetype=u'application/json')
