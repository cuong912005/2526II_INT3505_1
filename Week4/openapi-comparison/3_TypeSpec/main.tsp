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
namespace BookAPI;

enum Category {
  Classic,
  Fiction,
  Science,
  History,
  Biography,
  Technology,
}

model Book {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  publishYear?: integer;
  price?: float64;
  category?: Category;
}

model CreateBookRequest {
  title: string;
  author: string;
  isbn?: string;
  publishYear?: integer;
  price?: float64;
  category?: Category;
}

model ListBooksResponse {
  books: Book[];
  total: integer;
}

interface Books {
  @get
  @route("/books")
  listBooks(
    @query category?: Category,
    @query limit?: integer,
    @query offset?: integer,
  ): ListBooksResponse;

  @post
  @route("/books")
  createBook(
    @body book: CreateBookRequest,
  ): Book;

  @get
  @route("/books/{id}")
  getBook(
    @path id: string,
  ): Book;

  @put
  @route("/books/{id}")
  updateBook(
    @path id: string,
    @body book: CreateBookRequest,
  ): Book;

  @delete
  @route("/books/{id}")
  deleteBook(
    @path id: string,
  ): void;
}
