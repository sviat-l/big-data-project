
CASSANDRA_TABLES ={
  "domain_pages": {
    "columns": ["domain", "page_id"],
  },
  "user_pages": {
    "columns": ["user_id", "page_id", "page_title"],
  },
  "pages": {
    "columns": ["page_id", "page_title", "domain"],
  },
  "pages_by_date": {
    "columns": ["created_at", "page_id", "page_title", "user_id", "user_text"],
  },
  "domain_stats": {
    "columns": ["domain", "page_id", "created_at", "user_is_bot"],
  },
}
