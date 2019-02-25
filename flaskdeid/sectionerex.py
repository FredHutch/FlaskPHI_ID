import json
import logging
import sectionerex

from flask import Blueprint, render_template, request, session, abort, jsonify, Response, current_app, g

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bp = Blueprint('sectionerex', __name__, url_prefix='/sectionerex')


@bp.route("/", methods=['POST'])
@bp.route("/<string:sectioning_category>", methods=['POST'])
def section(sectioning_category=None):
    if not request.json or 'extract_text' not in request.json:
        msg = "No extract text was specified for sectioning."
        return Response(msg, 400)

    note_text = request.json['extract_text']
    if note_text:
        return _get_sectioned_text(note_text, sectioning_category)
    else:
        msg = "No Entity Text was found"
        logger.info("No text was preprocessed")
        return Response(msg, status=400)

def get_rules():
    if 'sectioner_rules' not in g:
        logger.info("rules loading from: {}".format(current_app.config['SECTIONER_MODEL_LOC']))
        g.sectioner_rules = sectionerex.load_rules(current_app.config['SECTIONER_MODEL_LOC'])

    return g.sectioner_rules

def _get_sectioned_text(note_text, category=None):
    section_rules = get_rules()
    if category and category.lower() not in section_rules.keys():
        msg = "A category was specified that is not in the sectioner's ruleset: {}\nCurrently allowed categories are: {}".format(category, section_rules.keys())
        return Response(msg, status=400)

    logger.info("specified category: {}".format(category))
    logger.info("sectioner categories in use: {}".format(section_rules))
    tags = sectionerex.label_text(note_text, section_rules, category=category)

    return Response(json.dumps(tags), mimetype=u'application/json')



