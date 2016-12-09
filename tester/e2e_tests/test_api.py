"""
Test trackit API e2e
"""

import json
import random
import string
import unittest

import requests


class APITestCase(unittest.TestCase):
    """
    Abstract base class for API test cases
    """
    root_url = "http://proxy"

    def get_schemata(self, username):
        """
        Return all schemata for a given namespace
        """
        result = requests.get("{}/schemata/{}/".format(self.root_url,
                                                       username))
        self.assertEqual(result.status_code, 200)
        return result.json()

    def put_schema(self, username, name, obj):
        """
        Set the schema for a name in a namespace
        """
        result = requests.put("{}/schemata/{}/{}/".format(self.root_url,
                                                          username, name),
                              headers={'Content-type': 'application/json'},
                              data=json.dumps(obj))
        self.assertEqual(result.status_code, 200)
        return result.json()

    def get_data(self, username, schema):
        """
        Return all data for a named schema in a namespace
        """
        result = requests.get("{}/data/{}/{}/".format(self.root_url, username,
                                                      schema))
        self.assertEqual(result.status_code, 200)
        return result.json()

    def put_datum(self, username, schema, key, obj):
        """
        Set a datum for a key, name, and namespace
        """
        result = requests.put("{}/data/{}/{}/{}/".format(
            self.root_url, username, schema, key),
                              headers={'Content-type': 'application/json'},
                              data=json.dumps(obj))
        self.assertEqual(result.status_code, 200)
        return result.json()

    def get_datum(self, username, schema, key):
        """
        Return a datum for a named schema in a namespace given a key
        """
        result = requests.get("{}/data/{}/{}/{}/".format(
            self.root_url, username, schema, key))
        self.assertEqual(result.status_code, 200)
        return result.json()

    def purge(self):
        """
        Delete all schemata and data
        """
        result = requests.post(
            "{}/purge/".format(self.root_url),
            headers={'Content-type': 'application/json'}, )
        self.assertEqual(result.status_code, 200)
        return result.json()

    def put_archive(self, archive):
        """
        Restore an archive
        """
        result = requests.put("{}/archive/".format(self.root_url),
                              headers={'Content-type': 'application/json'},
                              data=json.dumps(archive))
        self.assertEqual(result.status_code, 200)
        return result.json()

    def get_archive(self):
        """
        Return an archive of all schemata and data
        """
        result = requests.get("{}/archive/".format(self.root_url),
                              headers={'Content-type': 'application/json'})
        self.assertEqual(result.status_code, 200)
        return result.json()

    @staticmethod
    def make_username(length=5):
        """
        Return a random valid namespace
        """
        return "".join(
            random.choice(string.ascii_letters) for _ in range(length))


class APITests(APITestCase):
    """
    Basic e2e tests of the API
    """

    def test_put_and_get_schema(self):
        """
        Test PUTting and GETting a schema
        """
        username = self.make_username()
        schemata = self.get_schemata(username)
        self.assertEqual(schemata, {})
        self.put_schema(username, "test", {"message": {"type": "string"}})
        schemata = self.get_schemata(username)
        self.assertEqual(schemata, {"test": {"message": {"type": "string"}}})

    def test_put_and_get_datum(self):
        """
        Test PUTting and GETting a datum
        """
        username = self.make_username()
        schemata = self.get_schemata(username)
        self.assertEqual(schemata, {})
        schema = "test"
        self.put_schema(username, schema, {"message": {"type": "string"}})
        schemata = self.get_schemata(username)
        self.assertEqual(schemata, {schema: {"message": {"type": "string"}}})
        data = self.get_data(username, schema)
        self.assertEqual(data, {})
        self.put_datum(username, schema, "Hello", {"message": "Hello World!"})
        data = self.get_data(username, schema)
        self.assertEqual(data, {"Hello": {"message": "Hello World!"}})
        datum = self.get_datum(username, schema, "Hello")
        self.assertEqual(datum, {"message": "Hello World!"})

    def test_purge_put_and_get_archive(self):
        """
        Test purging, restoring, and GETting an archive
        """
        archive = {
            "user1": {
                "schema1": {
                    "schema": {
                        "field1": {
                            "type": "string"
                        }
                    },
                    "data": {
                        "datum1": {
                            "field1": "foo"
                        },
                    },
                },
                "schema2": {
                    "schema": {
                        "field2": {
                            "type": "string"
                        }
                    },
                    "data": {
                        "datum2": {
                            "field2": "bar"
                        },
                    },
                },
            },
            "user2": {
                "schema3": {
                    "schema": {
                        "field3": {
                            "type": "string"
                        }
                    },
                    "data": {
                        "datum3": {
                            "field3": "baz"
                        },
                    },
                },
                "schema4": {
                    "schema": {
                        "field4": {
                            "type": "string"
                        }
                    },
                    "data": {
                        "datum4": {
                            "field4": "garpley"
                        },
                    },
                },
            },
        }
        self.purge()
        self.put_archive(archive)
        self.assertEqual(archive, self.get_archive())
