from nose.tools import assert_true, assert_false, assert_equals, assert_raises

from .metadata import semantic_search

class TestMetadata(object):

  def test_semantic_search(self):
    table_names = ["vendors", "products", "inventory", "offices", "employees"]
    query = "people"

    results = semantic_search(table_names, query, 1)
    assert_equals(len(results), 1)
    assert_equals(results[0], "employees")

    results = semantic_search(table_names, query, 2)
    assert_equals(len(results), 2)

  def test_semantic_search_large_corpus(self):
    table_names = ["orders", "products", "employees", "suppliers", "categories", "claims",
              "policies", "shipments", "payments", "sales", "contacts", "addresses", "accounts",
              "transactions", "users", "messages", "reviews", "comments", "events", "tickets",
              "reservations", "projects", "tasks", "departments", "roles", "permissions", "books",
              "authors", "genres", "students", "courses", "enrollments", "grades",
              "inventory", "locations", "vendors", "partners", "assets", "expenses", "budgets",
              "donations", "hospitals", "patients", "doctors", "appointments", "vehicles",
              "drivers"]

    query = "people"

    results = semantic_search(table_names, query)
    assert_equals(len(results), 10)
    assert_equals(results[0], "users")

    query = "names of people who bought the largest number of books"

    results = semantic_search(table_names, query)
    print("Results :", results)
    assert_true("users" in results, msg="users table must be returned as that contains the name column")
    assert_true("orders" in results)
    assert_true("books" in results)
