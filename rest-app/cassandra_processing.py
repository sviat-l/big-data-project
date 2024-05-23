import cassandra_client
from datetime import date, timedelta
from collections import Counter

host, port, keyspace = 'cassandra', 9042, 'reviews'
connection = cassandra_client.CassandraClient(host, port, keyspace)
connection.connect()


def find_reviews_by_customer_id(customer_id):
    result = connection.get_customer_reviews(customer_id=customer_id)
    return result


def find_reviews_by_product_id(product_id, star_rating=None):
    result = connection.get_product_reviews(
        product_id=product_id, star_rating=star_rating)
    return result


def find_most_reviewed_products(from_date, to_date, limit):
    # collect all reviews for each date
    occurrences = Counter()
    curr_date = from_date
    while curr_date <= to_date:
        result = connection.get_products_reviwed_at_date(curr_date)
        result = [tuple([(col, getattr(r, col)) for col in
                        ["product_id", "product_title"]])
                  for r in result]
        occurrences.update(result)
        curr_date = curr_date + timedelta(days=1)
    # return in the requested format
    selected_products = []
    for product_info, num in occurrences.most_common(limit):
        product_result = dict(product_info)
        product_result["reviews_number"] = num
        selected_products.append(product_result)
    return selected_products

    # return [dict(product_info + (("reviews_number", num),)) for product_info, num in occurrences.most_common(limit)]


def map_review_type_with_rating_range(review_type):
    if review_type == "positive":
        return (4, 5)
    elif review_type == "negative":
        return (1, 2)
    return tuple(range(1, 6))


def find_most_productive_customers(from_date, to_date, limit=10, verified_only=False, review_type=None):
    star_rating_range = map_review_type_with_rating_range(review_type)
    occurrences = Counter()
    curr_date = from_date
    while curr_date <= to_date:
        result = connection.get_clients_reviewing_at_date(
            curr_date, star_rating_range=star_rating_range, verified_only=verified_only)
        result = [r.customer_id for r in result]
        occurrences.update(result)
        curr_date = curr_date + timedelta(days=1)
    selected_customers = [{"customer_id": customer_id, "reviews_number": num}
                          for customer_id, num in occurrences.most_common(limit)]
    return selected_customers

