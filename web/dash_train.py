from flask import Blueprint

bp = Blueprint('train', __name__, url_prefix='/train')

@bp.route('/train')
def show_train():
    return 'show train'