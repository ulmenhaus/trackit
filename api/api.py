"""
Flask API for trackit service
"""

import collections
import json

from flask import Flask, request


class API(object):
    """
    Wrapper for the flask API object
    """

    def __init__(self, db_connection, db_name):
        """
        Initialize
        """
        self.r = db_connection
        self.db = self.r.db(db_name)
        self.app = Flask(__name__)
        self.app.route('/schemata/<username>/')(self.get_schemata)
        self.app.route(
            '/schemata/<username>/<name>/', methods=["PUT"])(self.set_schema)
        self.app.route('/data/<username>/<schema>/')(self.get_data)
        self.app.route(
            '/data/<username>/<schema>/<key>/',
            methods=["PUT"])(self.set_datum)
        self.app.route('/data/<username>/<schema>/<key>/')(self.get_datum)
        self.app.route('/archive/', methods=["GET"])(self.get_archive)
        self.app.route('/archive/', methods=["PUT"])(self.restore_archive)
        self.app.route('/purge/', methods=["POST"])(self.purge)

    def get_schemata(self, username):
        """
        Get all schemata in a namespace
        """
        return json.dumps(
            {
                entry["name"][len(username) + 1:]: entry["body"]
                for entry in self.db.table("schemata").filter(self.r.row[
                    "username"] == username).run()
            },
            indent=4)

    def set_schema(self, username, name):
        """
        Get a schema given its name and namespace
        """
        body = request.get_json()
        # TODO validate body
        key = "{}/{}".format(username, name)
        schema = {
            "name": key,
            "body": body,
            "username": username,
        }
        self.db.table("schemata").insert([schema], conflict='update').run()
        return json.dumps({name: body}, indent=4)

    def get_data(self, username, schema):
        """
        Get all data for a schema given its name and a namespace
        """
        query = self.db.table("data").filter(
            (self.r.row["username"] == username) & \
            (self.r.row["schema"] == schema))

        return json.dumps(
            {
                entry["key"][len(username) + len(schema) + 2:]: entry["datum"]
                for entry in query.run()
            },
            indent=4)

    def set_datum(self, username, schema, key):
        """
        Set a datum given its key, schema name, and namespace
        """
        # TODO validate against schema
        body = request.get_json()
        fullkey = "{}/{}/{}".format(username, schema, key)
        entry = {
            "key": fullkey,
            "username": username,
            "schema": schema,
            "datum": body
        }
        self.db.table("data").insert([entry], conflict='update').run()
        return json.dumps({key: body}, indent=4)

    def get_datum(self, username, schema, key):
        """
        Get a datum given its key, schema name, and namespace
        """
        # TODO validate against schema
        fullkey = "{}/{}/{}".format(username, schema, key)
        entry, = self.db.table("data").filter(
            self.r.row["key"] == fullkey).run()
        return json.dumps(entry["datum"], indent=4)

    def get_archive(self):
        """
        Get an archive of all schemata and data for all namespaces
        """
        all_schemata = collections.defaultdict(dict)
        for entry in self.db.table("schemata").run():
            namespace, schema_name = entry["name"].split("/")
            all_schemata[namespace][schema_name] = {
                "schema": entry["body"],
                "data": {}
            }
        for entry in self.db.table("data").run():
            datum_key = entry["key"].split("/")[-1]
            all_schemata[entry["username"]][entry["schema"]]["data"][
                datum_key] = entry["datum"]
        return json.dumps(dict(all_schemata), indent=4)

    def restore_archive(self):
        """
        Restore an archive
        """
        archive = request.get_json()
        schemata = [{
            "name": "{}/{}".format(namespace, schema_name),
            "body": schema_spec["schema"],
            "username": namespace
        }
                    for namespace, space_items in archive.items()
                    for schema_name, schema_spec in space_items.items()]
        self.db.table("schemata").insert(schemata, conflict='update').run()

        data = [{
            "key": "{}/{}/{}".format(namespace, schema_name, datum_name),
            "datum": datum,
            "username": namespace,
            "schema": schema_name,
        }
                for namespace, space_items in archive.items()
                for schema_name, schema_spec in space_items.items()
                for datum_name, datum in schema_spec["data"].items()]
        self.db.table("data").insert(data, conflict='update').run()
        return json.dumps(archive, indent=4)

    def purge(self):
        """
        Destroy all schemata and data
        """
        self.db.table("data").delete().run()
        self.db.table("schemata").delete().run()
        return json.dumps({})
