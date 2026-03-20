import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.books_get200_response import BooksGet200Response  # noqa: E501
from openapi_server.models.create_book import CreateBook  # noqa: E501
from openapi_server import util


def books_get(category=None):  # noqa: E501
    """Get all books

     # noqa: E501

    :param category: 
    :type category: str

    :rtype: Union[BooksGet200Response, Tuple[BooksGet200Response, int], Tuple[BooksGet200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def books_id_delete(id):  # noqa: E501
    """Delete a book

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def books_id_get(id):  # noqa: E501
    """Get book by ID

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    return 'do some magic!'


def books_id_put(id, body):  # noqa: E501
    """Update a book

     # noqa: E501

    :param id: 
    :type id: str
    :param create_book: 
    :type create_book: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    create_book = body
    if connexion.request.is_json:
        create_book = CreateBook.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def books_post(body):  # noqa: E501
    """Create a book

     # noqa: E501

    :param create_book: 
    :type create_book: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    create_book = body
    if connexion.request.is_json:
        create_book = CreateBook.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
