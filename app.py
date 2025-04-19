from flask import Flask, request, jsonify
from markupsafe import escape
from db import MongoDBConnection
from bson import ObjectId

app = Flask(__name__)
mongo = MongoDBConnection(db_name="testdb")
mongo.connect()

@app.route("/about")
def about():
    return "<p>This is the about page.</p>"

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!\n"

@app.route("/upload_doc", methods=["POST"])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_id = mongo.fs.put(file, filename=file.filename)
    return jsonify({"message": "File uploaded", "file_id": str(file_id)})

@app.route("/download/<file_id>", methods=["GET"])
def download_document(file_id: ObjectId):
    try:
        grid_out = mongo.fs.get(ObjectId(file_id))
        return (grid_out.read(), 
                200, 
                {'Content-Type': 'application/pdf',
                 'Content-Disposition': f'attachment; filename={grid_out.filename}'})
    except Exception as e:
        return jsonify({"error": str(e)}), 404
    
# @app.teardown_appcontext # This is running when I don't want it to
# def close_connection(exception):
#     mongo.close()

if __name__ == "__main__":
    app.run(debug=True)