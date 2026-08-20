from flask import Blueprint
bp = Blueprint('stock', __name__)
from . import routes
