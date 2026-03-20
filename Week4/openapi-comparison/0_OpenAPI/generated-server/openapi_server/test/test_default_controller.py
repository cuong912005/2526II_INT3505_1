import unittest

from flask import json

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.books_get200_response import BooksGet200Response  # noqa: E501
from openapi_server.models.create_book import CreateBook  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_books_get(self):
        """Test case for books_get

        Get all books
        """
        query_string = [('category', 'category_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_id_delete(self):
        """Test case for books_id_delete

        Delete a book
        """
        headers = { 
        }
        response = self.client.open(
            '/books/{id}'.format(id='id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_id_get(self):
        """Test case for books_id_get

        Get book by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books/{id}'.format(id='id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_id_put(self):
        """Test case for books_id_put

        Update a book
        """
        create_book = {"publishYear":0,"author":"author","price":6.027456183070403,"isbn":"isbn","title":"title","category":"category"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/books/{id}'.format(id='id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(create_book),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_post(self):
        """Test case for books_post

        Create a book
        """
        create_book = {"publishYear":0,"author":"author","price":6.027456183070403,"isbn":"isbn","title":"title","category":"category"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/books',
            method='POST',
            headers=headers,
            data=json.dumps(create_book),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
