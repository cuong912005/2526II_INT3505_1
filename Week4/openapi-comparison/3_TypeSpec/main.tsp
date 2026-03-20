import "@typespec/rest";
import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Rest;
using TypeSpec.Http;

@service({
  title: "Book Management API",
  version: "1.0.0",
})
@server("http://localhost:3000/api/v1", "Development server")
@server("https://api.bookstore.com/v1", "Production server")
namespace BookAPI;

// Enums
enum Category {
  Classic,
  Fiction,
  Science,
  History,
  Biography,
  Technology,
}

// Models
@doc("Complete book information")
model Book {
  @doc("Book unique identifier")
  id: string;

  @minLength(1)
  @maxLength(200)
  @doc("Book title")
  title: string;

  @minLength(1)
  @maxLength(100)
  @doc("Author name")
  author: string;

  @pattern("^\\d{10}(\\d{3})?$")
  @doc("ISBN-10 or ISBN-13")
  isbn?: string;

  @minValue(1000)
  @maxValue(2100)
  @doc("Year of publication")
  publishYear?: integer;

  @minValue(0)
  @doc("Book price in USD")
  price?: float64;

  @doc("Book category")
  category?: Category;
}

@doc("Request to create a new book")
model CreateBookRequest {
  @minLength(1)
  @maxLength(200)
  @doc("Book title")
  title: string;

  @minLength(1)
  @maxLength(100)
  @doc("Author name")
  author: string;

  @pattern("^\\d{10}(\\d{3})?$")
  @doc("ISBN-10 or ISBN-13")
  isbn?: string;

  @minValue(1000)
  @maxValue(2100)
  @doc("Year of publication")
  publishYear?: integer;

  @minValue(0)
  @doc("Book price in USD")
  price?: float64;

  @doc("Book category")
  category?: Category;
}

@doc("Request to update a book (all fields optional)")
model UpdateBookRequest {
  @minLength(1)
  @maxLength(200)
  @doc("Book title")
  title?: string;

  @minLength(1)
  @maxLength(100)
  @doc("Author name")
  author?: string;

  @pattern("^\\d{10}(\\d{3})?$")
  @doc("ISBN-10 or ISBN-13")
  isbn?: string;

  @minValue(1000)
  @maxValue(2100)
  @doc("Year of publication")
  publishYear?: integer;

  @minValue(0)
  @doc("Book price in USD")
  price?: float64;

  @doc("Book category")
  category?: Category;
}

@doc("Response containing list of books")
model ListBooksResponse {
  @doc("Array of books")
  books: Book[];

  @doc("Total number of books")
  total: integer;
}

@doc("Error response")
model ErrorResponse {
  @doc("Error code")
  code: integer;

  @doc("Error message")
  message: string;

  @doc("Additional error details")
  details?: {};
}

// Service Interface
interface Books {
  @doc("Get all books")
  @get
  @route("/books")
  listBooks(
    @query
    @doc("Filter by category")
    category?: Category,

    @query
    @doc("Max number of results")
    limit?: integer = 10,

    @query
    @doc("Number of results to skip")
    offset?: integer = 0,
  ): ListBooksResponse;

  @doc("Create a new book")
  @post
  @route("/books")
  createBook(
    @body
    book: CreateBookRequest,
  ): Book | ErrorResponse;

  @doc("Get book by ID")
  @get
  @route("/books/{id}")
  getBook(
    @path
    @doc("Book ID")
    id: string,
  ): Book | ErrorResponse;

  @doc("Update book")
  @put
  @route("/books/{id}")
  updateBook(
    @path
    @doc("Book ID")
    id: string,

    @body
    @doc("Updated book data")
    book: UpdateBookRequest,
  ): Book | ErrorResponse;

  @doc("Delete book")
  @delete
  @route("/books/{id}")
  deleteBook(
    @path
    @doc("Book ID")
    id: string,
  ): void;
}
