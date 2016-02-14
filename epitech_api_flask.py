from flask import Flask, request, render_template
from api_parser import *
from api_checkers import log_and_check_params
from api_conf import server_url, listen_port, listen_host, debug, ssl_verify
from time import strftime
from datetime import timedelta, date
import json
import logging

app = Flask(__name__)
logging.basicConfig(filename=".api.log", level=logging.INFO)


@app.route('/', methods=['POST', 'GET'])
def doc():
    return render_template("api_epitech.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    error, session, params = log_and_check_params(["login", "password"], request)
    return (json.dumps(error), error['error']['code']) if error != {} else json.dumps(
            {"token": session.cookies['PHPSESSID']})


@app.route('/infos', methods=['POST', 'GET'])
def infos():
    """/login   (POST,GET) login, password"""
    error, session, params = log_and_check_params(["token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.post(server_url + "/?format=json", verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return r.text
    except:
        return json.dumps({"error": {"message": "Server was unable to connect through Epitech API", "code": 500}}), 500


@app.route('/planning', methods=['POST', 'GET'])
def planning():
    """/planning    (POST,GET) login, password, start, end, [get] (all, registered, free)"""
    error, session, params = log_and_check_params(["start", "end", "token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    get = params['get'] if "get" in params.keys() else "all"
    start = params['start']
    end = params['end']
    try:
        r = session.post(server_url + "/intra/planning/load?format=json&start=%s&end=%s" % (start, end),
                         verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        if debug:
            log_file("Intra replied in %s seconds" % r.elapsed)
        if len(r.text) < 2:
            return (json.dumps({"error": {"message": "Epitech API returned an empty response", "code": 500}})), 500
        planning = json.loads(r.text)
        filtered_planning = get_classes_by_status(planning, get)
        return json.dumps(filtered_planning)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/susies', methods=['POST', 'GET'])
def susies():
    error, session, params = log_and_check_params(["start", "end", "token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    get = params['get'] if "get" in params.keys() else "all"
    start = params['start']
    end = params['end']
    try:
        r = session.post(server_url + "/intra/planning/load?format=json&start=%s&end=%s" % (start, end),
                         verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        if len(r.text) < 2:
            return json.dumps({"error": {"message": "Intra replied an empty string. Please check your date format"}})
        planning = json.loads(clean_json(r.text))
        susies = get_classes_by_calendar_type(planning, 'susie')
        susies = get_classes_by_status(susies, get)
        return json.dumps(susies)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/susie', methods=['POST', 'GET', 'DELETE'])
def susie(action=""):
    method = request.method
    error, session, params = log_and_check_params(["id", "token", "calendar_id"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    _id = params['id']
    try:
        action = {"POST": "subscribe",
                  "DELETE": "unsubscribe",
                  "GET": ""}
        route = server_url + "/planning/%s/%s/%s?format=json" % (params['calendar_id'], _id, action[method])
        r = session.post(route, verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps(
                    {"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/projects', methods=['POST', 'GET'])
def projects():
    """/projects  (POST,GET) login, password, [get]"""
    error, session, params = log_and_check_params(["token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    get = params['get'] if "get" in params.keys() else "all"
    d = date.today()
    start = strftime("%Y-%m-%d", d.timetuple())
    d = date.today() + timedelta(days=365);
    end = params["key"] if "end" in params.keys() else strftime("%Y-%m-%d", d.timetuple())
    try:
        r = session.post(server_url + "/module/board/?format=json&start=%s&end=%s" % (start, end), verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return json.dumps(filter_projects(json.loads(r.text), get))
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/project', methods=['GET', 'POST', 'DELETE'])
def project():
    method = request.method
    error, session, params = log_and_check_params(["token", "scolaryear", "codemodule", "codeinstance", "codeacti"],
                                                  request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        action = {"GET": "",
                  "POST": "register",
                  "DELETE": "destroygroup"}
        route = server_url + "/module/%s/%s/%s/%s/project/%s?format=json" % (params['scolaryear'], params['codemodule'],
                                                                             params['codeinstance'], params['codeacti'],
                                                                             action[method])
        r = session.post(route, verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps(
                    {"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/project/files', methods=['GET'])
def get_file():
    error, session, params = log_and_check_params(["token", "scolaryear", "codemodule", "codeinstance", "codeacti"],
                                                  request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.post(server_url + "/module/%s/%s/%s/%s/project/file/?format=json" % (
            params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti']), verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps(
                    {"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/project/marks', methods=['GET'])
def project_marks():
    error, session, params = log_and_check_params(["token", "scolaryear", "codemodule", "codeinstance", "codeacti"],
                                                  request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        url = server_url + "/module/%s/%s/%s/%s/note/?format=json" % (
            params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'])
        r = session.get(url, verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return r.text
    except:
        return json.dumps({"error": {"message": "Server was unable to connect through Epitech API", "code": 500}}), 500


@app.route('/user/files', methods=['GET'])
def get_user_files():
    error, session, params = log_and_check_params(["token", "login"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.post(server_url + "/user/%s/document/?format=json" % params['login'], verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps(
                    {"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/user/flags', methods=['GET'])
def get_user_flags():
    error, session, params = log_and_check_params(["token", "login"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.post(server_url + "/user/%s/flags/?format=json" % params['login'], verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps(
                    {"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/allmodules', methods=['GET'])
def allmodules():
    error, session, params = log_and_check_params(["token", "scolaryear", "location", "course"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.get(
                server_url + "/course/filter?format=json&preload=1&location=FR&location=%s&course=%s&scolaryear=%s" % (
                    params['location'], params['course'], params['scolaryear']), verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps({"error": {"message": "Server was unable to connect through Epitech API", "code": 500}}), 500


@app.route('/modules', methods=['POST', 'GET'])
def modules():
    """/modules (POST,GET) login, password"""
    error, session, params = log_and_check_params(["token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        route = server_url + "/user/" + ("%s/notes" % params['login'] if 'login' in params else "#!/netsoul")
        r = session.get(route, verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return get_modules(r.text)
    except:
        return json.dumps({"error": {"message": "Server was unable to connect through Epitech API", "code": 500}}), 500


@app.route('/module', methods=['GET', 'POST', 'DELETE'])
def module():
    method = request.method
    error, session, params = log_and_check_params(["token", "scolaryear", "codemodule", "codeinstance"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        action = {"GET": "",
                  "POST": "register",
                  "DELETE": "unregister"}
        url = server_url + "/module/%s/%s/%s/%s?format=json" % (
            params['scolaryear'], params['codemodule'], params['codeinstance'], action[method])
        r = session.post(url, verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/module/registered', methods=['GET'])
def module_registered():
    error, session, params = log_and_check_params(["token", "scolaryear", "codemodule", "codeinstance"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        url = server_url + "/module/%s/%s/%s/registered?format=json" % (
        params['scolaryear'], params['codemodule'], params['codeinstance'])
        r = session.post(url, verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/marks', methods=['POST', 'GET'])
def marks():
    """/marks (POST,GET) login, password"""
    error, session, params = log_and_check_params(["token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        if 'login' in params:
            r = session.post(server_url + "/user/%s/#!/notes" % params['login'], verify=ssl_verify)
        else:
            r = session.post(server_url + "/user/#!/netsoul", verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return get_marks(r.text)
    except:
        return {"error": {"message": "Server was unable to connect through Epitech API", "code": 500}}


@app.route('/messages', methods=['POST', 'GET'])
def messages():
    """/messages (POST,GET) login, password"""
    error, session, params = log_and_check_params(["token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.post(server_url + "/intra/user/notification/message?format=json", verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/alerts', methods=['POST', 'GET'])
def alerts():
    """/alerts (POST,GET) login, password"""
    error, session, params = log_and_check_params(["token"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.post(server_url + "/intra/user/notification/alert?format=json", verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except Exception as e:
        return json.dumps({"error": {"message": str(e), "code": 500}}), 500


@app.route('/photo', methods=['POST', 'GET'])
def photo():
    """/photo (POST,GET) login, password"""
    error, session, params = log_and_check_params(["token", "login"], request)
    if error != {}:
        return json.dumps(error)
    return json.dumps({"url": "https://cdn.local.epitech.eu/userprofil/profilview/%s.jpg" % params['login']})


@app.route('/token', methods=['POST', 'GET'])
def token():
    """/token (POST,GET) login, password, scolaryear, codemodule, codeinstance, codeacti, token"""
    error, session, params = log_and_check_params(
            ["tokenvalidationcode", "scolaryear", "codemodule", "codeinstance", "codeacti", "token", "codeevent"],
            request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        payload = {'token': params['tokenvalidationcode'], 'rate': 1, 'comment': ''}
        url = server_url + "/module/%s/%s/%s/%s/%s/token?format=json" % (
            params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'], params['codeevent'])
        r = session.post(url, data=payload, verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/user', methods=['GET'])
def user():
    error, session, params = log_and_check_params(["token", "user"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        r = session.post(server_url + "/user/%s?format=json" % params['user'], verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/event', methods=['GET', 'POST', 'DELETE'])
def event():
    method = request.method
    error, session, params = log_and_check_params(
            ["token", "scolaryear", "codemodule", "codeinstance", "codeacti", "codeevent"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        action = {"GET": "",
                  "POST": "register",
                  "DELETE": "unregister"}
        url = server_url + "/module/%s/%s/%s/%s/%s/%s?format=json" % (
            params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'],
            params['codeevent'], action[method])
        r = session.post(url, verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/event/registered', methods=['GET'])
def event_registered():
    error, session, params = log_and_check_params(
            ["token", "scolaryear", "codemodule", "codeinstance", "codeacti", "codeevent"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        url = server_url + "/module/%s/%s/%s/%s/%s/registered?format=json" % (
        params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'], params['codeevent'])
        r = session.get(url, verify=ssl_verify)

        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/event/rdv', methods=['GET'])
def appoointment_registered():
    error, session, params = log_and_check_params(["token", "scolaryear", "codemodule", "codeinstance", "codeacti"],
                                                  request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        url = server_url + "/module/%s/%s/%s/%s/rdv?format=json" % (
        params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'])
        r = session.get(url, verify=ssl_verify)

        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/event/rdv', methods=['POST'])
def appoointment_register():
    error, session, params = log_and_check_params(
            ["token", "scolaryear", "codemodule", "codeinstance", "codeacti", "idcreneau"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        if 'idteam' in params:
            url = server_url + "/module/%s/%s/%s/%s/rdv/register?id_creneau=%s&id_team=%s&format=json" % (
                params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'], params['idcreneau'],
                params['idteam'])
        else:
            url = server_url + "/module/%s/%s/%s/%s/rdv/register?id_creneau=%s&login=%s&format=json" % (
                params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'], params['idcreneau'],
                params['login'])
        r = session.post(url, verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps({"error": {"message": r.text, 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/event/rdv', methods=['DELETE'])
def appoointment_unregister():
    error, session, params = log_and_check_params(
            ["token", "scolaryear", "codemodule", "codeinstance", "codeacti", "idcreneau"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        if 'idteam' in params:
            url = server_url + "/module/%s/%s/%s/%s/rdv/unregister?id_creneau=%s&id_team=%s&format=json" % (
                params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'], params['idcreneau'],
                params['idteam'])
        else:
            url = server_url + "/module/%s/%s/%s/%s/rdv/unregister?id_creneau=%s&login=%s&format=json" % (
                params['scolaryear'], params['codemodule'], params['codeinstance'], params['codeacti'], params['idcreneau'],
                params['login'])
        r = session.post(url, verify=ssl_verify)
        if r.status_code == 403:
            if "// Epitech JSON webservice" in r.text:
                return clean_json(r.text), 403
            return json.dumps({"error": {"message": r.text, 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/trombi', methods=['GET'])
def trombi():
    filters = ""
    error, session, params = log_and_check_params(["token", "location", "year"], request)
    if error != {}:
        return json.dumps(error), error['error']['code']
    try:
        for param in params:
            if param not in ["login", "password"]:
                filters += "&%s=%s" % (param, params[param])
        r = session.post(server_url + "/user/filter/user?format=json" + filters, verify=ssl_verify)
        if r.status_code == 403:
            return json.dumps({"error": {"message": "Connection token is invalid or has expired", 'code': 403}}), 403
        return clean_json(r.text)
    except:
        return json.dumps(
                {"error": {"message": "Server was unable to connect to Epitech's intra API", "code": 500}}), 500


@app.route('/rank', methods=['GET'])
def rank():
    return json.dumps({"message": "Available soon"})


@app.route('/ping', methods=['POST', 'GET'])
def wake_up():
    return ("pong"), 200


if __name__ == '__main__':
    try:
        app.debug = debug
        app.run(port=listen_port, host=listen_host, threaded=True)
    except Exception as e:
        if debug:
            log_file(e)
