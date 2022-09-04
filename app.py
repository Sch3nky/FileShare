from flask import Flask, render_template, request, jsonify, send_from_directory, make_response, abort, redirect, url_for
from threading import Thread
from werkzeug.utils import secure_filename
import os
import Main
import json

cEnding = ["jpg", "jpeg", "jpe", "jif", "jfif", "jfi", "png", "gif", "webp", "svg", "svgz", "ai", "eps", "pdf", "mp4", "mp3", "mkv", "avi", "zip", "rar"]

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 * 1024

loop = Thread(target=Main.mainLoop)
loop.start()

@app.before_request
def before_request():
    with open(os.path.dirname(__file__) + f"/Data/adminData.json", "r+") as file:
        data = json.load(file)
        active = data["active"]
        file.close()
        if not active:
            return render_template("Admin/notAvalible.html")

@app.route("/set_cookies/<name>_<value>")
def set_cookies(name, value):
    response = make_response(redirect("/"))
    response.set_cookie(name, value)
    return response

@app.route('/')
@app.route('/<data>')
def main(data=""):  # put application's code here
    if data == "":
        cookieConcest = request.cookies.get('cookieConcest')
        return render_template("index.html", name="FileShare", notcookieconsent=False)#(cookieConcest!="1"))
    elif data.lower() == "contactus" or data.lower() == "contact":
        return redirect("https://soffapps.dev/contact")

    elif data.lower() == "termsofuse":
        return render_template("TermsOfUse.html")

    elif data.lower() == "cookies":
        return render_template("cookies.html")

    elif data.lower() == "privacypolicy":
        return render_template("PrivacyPolicy.html")

    elif data.lower() == "aboutus":
        return render_template("aboutus.html")

    elif data.find(".") != -1:
        return send_from_directory("serverFiles", data.lower())
    else:
        abort(404)

@app.route("/contact<type>", methods=["POST"])
@app.route("/contact-<messageP>-<name>-<email>-<fullscreen>", methods=["GET"])
def contact(messageP="Enter your message", name="Contact Us", email="1", fullscreen="1", type="message"):
    if request.method == "GET":
        print(fullscreen)
        return render_template("ContactUs.html", messageplaceholder=messageP.replace("_", " "), contactPageName=name.replace("_", " "), emailR=(email=="1"), fscreen=(fullscreen=="1"))
    elif request.method == "POST":
        text = request.form["text"]
        try:
            email = request.form["email"]
            text = request.form["text"]
        except:
            email = ""

        with open(os.path.dirname(__file__) + f"/Data/adminData.json", "r+") as file:
            data = json.load(file)
            data["messages"].append({"type": type, "email": email, "message": text})
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
            file.close()
        return redirect(url_for("main"))
    abort(404)

@app.route("/newsletter")
def newsletter():
    pass

@app.route("/help")
def help():
    try:
        with open(os.path.dirname(__file__) + f"/Data/FAQ.json", "r") as fqa:
            data = json.load(fqa)
            fqa.close()
            return render_template("Help.html", questions=data["faq"])
    except:
        abort(404)

@app.route("/pinUI")
def get_pin():
    return render_template("Pin.html")

@app.route("/upload", methods=['POST'])
def upload():
    if (request.method == "POST" and request.files.get('file', None)):
        file = request.files["file"]

        pin = Main.pin_generator()
        filename = file.filename.split(".")

        if filename[1] in cEnding:
            os.mkdir(os.path.dirname(__file__) + f"/Files/{pin}")
            file.save(os.path.dirname(__file__) + f"/Files/{pin}/" + secure_filename(file.filename))
            pin, timeOf = Main.safe_file(file, pin, False)
        else:
            os.mkdir(os.path.dirname(__file__) + f"/{pin}")
            file.save(os.path.dirname(__file__) + f"/{pin}/" + secure_filename(file.filename))
            pin, timeOf = Main.safe_file(file, pin, True)

        return jsonify({"pin": int(pin)})
    else:
        abort(404)

@app.route("/download/<pin>")
def download(pin):
    dir, name = Main.get_file(pin, cEnding)
    if dir != None:
        response = make_response(send_from_directory(dir, name, as_attachment=True))
        try:
            response.headers['File-Name'] = str(name).split("/")[1]
        except:
            response.headers['File-Name'] = str(name)
        return response
    else:
        abort(404)

@app.route("/<file>")
def returnFile(file):
    return send_from_directory("static", file)

"""@app.route("/admin")
def Admin():
    if request.method == "GET":
        return "Admin Page"
    if request.method == "POST":
        return "AdminControl" """

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
