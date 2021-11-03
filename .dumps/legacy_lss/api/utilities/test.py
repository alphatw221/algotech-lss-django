from api.fb_campaign_automation import *
from flask import jsonify, request, render_template, send_file

from config import connex_app, db, basedir
from api.utilities.fb_api_utilities import *


def hello():
    return 'Hello!'


def echo(echo_me):
    return echo_me


def user_id_and_product_id(user_id, product_id):
    return "user: " + user_id + " product: " + product_id


def show_data():
    data = request.get_json()

    return jsonify({"Server says:": "got it", "data": data})


@ connex_app.route('/demo', methods=['GET'])
def live_stream_testing_html():
    return render_template("demo.html")


@ connex_app.route('/first_data', methods=['GET'])
def first_data():
    return render_template("first_data.php")


@ connex_app.route('/test', methods=['GET'])
def test():
    ret = ""
    return jsonify(ret), 200


@ connex_app.route('/testing_sql', methods=['GET'])
def testing_sql():
    ret = ""

    with db.engine.connect() as connection:
        result = connection.execute(
            """
            SELECT * FROM 
            (SELECT * FROM lss_fb_campaign_order WHERE fb_campaign_id = 4) a 
            LEFT JOIN lss_product_description ON a.product_id = lss_product_description.product_id
            """)

        for row in result:
            ret += str(row)

    return jsonify(ret), 200


@ connex_app.route('/download', methods=['GET'])
def download_file():
    path = basedir + "/campaign_summary.csv"
    return send_file(path, as_attachment=True)


@ connex_app.route('/order_report/<campaign_id>', methods=['GET'])
def order_report(campaign_id):
    ret = create_fb_campaign_summary(campaign_id)
    return jsonify(ret), 200


@ connex_app.route('/sql', methods=['POST'])
def direct_sql():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Data needed."}), 400

    sql = data.get('sql', None)
    if not sql:
        return jsonify({"msg": "Bad input data. Need: sql"}), 400

    ret = []
    try:
        for row in db.engine.execute(sql):
            ret.append(dict(row.items()))
    except:
        return jsonify(traceback.format_exc()), 200

    return jsonify(ret), 200
