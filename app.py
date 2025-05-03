from flask import Flask, request, jsonify
from markupsafe import escape
from db import MongoDBConnection
from bson import ObjectId
from typing import Dict, List, Optional, Union

app = Flask(__name__)
mongo = MongoDBConnection(db_name="testdb")
mongo.connect()

@app.route("/about")
def about():
    return "<p>This is the about page.</p>"

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!\n"

# curl -X POST http://localhost:5000/upload -F "file=@data/billing/n_pain.md"
@app.route("/docs", methods=["POST"])
def upload_document(metadata: Optional[Dict] = None) -> None:
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # file_id = mongo.fs.put(file, filename=file.filename)
    file_id = mongo.create_document(file, metadata)
    return jsonify({"message": "File uploaded", "file_id": str(file_id)})

@app.route("/docs/<file_id>", methods=["GET"])
def get_document(file_id: ObjectId):
    try:
        grid_out = mongo.fs.get(ObjectId(file_id))
        return (
            # TODO FIX
            grid_out.read(), 200, {
                'Content-Type': 'application/pdf', 
                'Content-Disposition': f'attachment; filename={grid_out.filename}'
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/docs/<file_id>", methods=["DELETE"])
def delete_document(file_id: str) -> None:
    file_id = ObjectId(file_id)
    status = mongo.delete_document(file_id)
    if status:
        return jsonify({"message": f"document {file_id} deleted"}), 200
    return jsonify({"error": f"bad id {file_id}"}), 404


# curl.exe http://192.168.0.111:5000/docs/meta/6802d39198e1216ede642f3a -X POST -H "Content-Type: application/json" -d '{"test": "12345"}'
@app.route("/docs/meta/<file_id>", methods=["POST"])
def update_metadata(file_id: str):
    file_id = ObjectId(file_id)
    metadata = request.get_json()
    status = mongo.update_metadata(file_id, metadata)

    if status:
        return jsonify({"message": f"document {file_id} updated with new metadata"}), 200
    else:
        return jsonify({"error": f"couldn't update metadata for {file_id}"}), 400

@app.route("/docs/meta/<file_id>", methods=["GET"])
def get_metadata(file_id: str):
    metadata = mongo.get_metadata(ObjectId(file_id))
    if metadata:
        return jsonify(metadata), 200
    return jsonify({"error": f"couldn't update metadata for {file_id}"}), 400
    
@app.route("/docs/meta/all", methods=["GET"])
def get_all_metadata() -> str:
    file_ids = mongo.list_file_ids()
    file_ids = [str(id) for id in file_ids]
    if file_ids:
        return jsonify({"message": file_ids}), 200
    else:
        return jsonify({"message": "no files in the db"}), 200
    
# @app.teardown_appcontext # This is running when I don't want it to
# def close_connection(exception):
#     mongo.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)