"""
Unit tests for the trackit API
"""

import json
import operator
import unittest

import mock

import api.api


class MockRowConstraint(object):
    """
    A Mock rethinkdb filter
    """

    def __init__(self, attribute, op, expression):
        """
        Initialize
        """
        self.attribute = attribute
        self.op = op
        self.expression = expression

    def matches(self, row):
        """
        return true iff the constraint matches a mock row (dict)
        """
        return self.op(row[self.attribute], self.expression)


class MockPartialRowConstraint(object):
    """
    Mock of the expression part of a rethinkdb filter (can be combined with other
    partials to make a MockRowConstraint)
    """

    def __init__(self, attribute):
        """
        Initialize
        """
        self.attribute = attribute

    def __eq__(self, expression):
        """
        Construct an exp1 == exp2 type MockRowConstraint
        """
        return MockRowConstraint(self.attribute, operator.eq, expression)


class MockRowConstraintFactory(object):
    """
    MockPartialRowConstraint generator that behaves like r.row
    """

    def __init__(self):
        """
        Initialize
        """
        pass

    def __getitem__(self, row_name):
        """
        Like r.row[item] creates a MockPartialRowConstraint
        """
        return MockPartialRowConstraint(row_name)


class MockTable(object):
    """
    A mock rethinkdb table
    """

    def __init__(self, rows):
        """
        Initialize
        """
        self.rows = rows

    def filter(self, constraint):
        """
        Return the rows that match a MockRowConstraint
        """
        toret = mock.Mock()
        toret.run.return_value = list(filter(constraint.matches, self.rows))
        return toret


class MockDB(object):
    """
    A mock rethink database
    """

    def __init__(self, data):
        """
        Initialize
        """
        self.data = data

    def table(self, name):
        """
        Get the table of a given name
        """
        return MockTable(self.data[name])


class APITestCase(unittest.TestCase):
    """
    Abstract base class for API test cases
    """
    dbs = {}

    def setUp(self):
        """
        Creates a mock database given the test case's mock data as
        a class attribute
        """
        self.mock_db_connection = mock.Mock()
        self.mock_db_connection.row = MockRowConstraintFactory()
        self.mock_db_connection.db.side_effect = self._db
        self.api = api.api.API(self.mock_db_connection, "trackit")

    def _db(self, name):
        return self.dbs[name]


class GetSchemaTests(APITestCase):
    """
    Test getting schemata using the API
    """
    dbs = {
        "trackit": MockDB({
            "schemata": [{
                "username": "rabrams",
                "name": "rabrams/schema-1",
                "body": {},
            }, ],
        })
    }

    def test_one_schema(self):
        """
        test getting a single scema
        """
        expected_response = json.dumps({"schema-1": {}}, indent=4)
        self.assertEqual(expected_response, self.api.get_schemata("rabrams"))


# TODO(rabrams) full test suite
