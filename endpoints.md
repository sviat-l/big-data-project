### Data model (only necessary fields are shown)

```json
{
"data": {
    "meta": {
        "id": "00121f00-1443-44fa-ae26-ce85902d75ed",
        "domain": "zh.wikipedia.org",
    },
    "performer": {
        "user_text": "Interaccoonale",
        "user_is_bot": false,
        "user_id": 1256681,
    },
    "page_id": 8751616,
    "page_title": "Template_talk:Taxonomy/Psittaculidae",
    "dt": "2024-05-24T11:43:12Z",
    }
}
```

## Categorie B (ad-hoc queries)
1. `/domains/all`
```ddl
CREATE TABLE wiki.domain_pages (
    domain TEXT,
    page_id INT,
    PRIMARY KEY (domain, page_id),
);
```

2. `/users/{user_id}/pages`

```ddl
CREATE TABLE wiki.user_pages (
    user_id INT,
    page_id INT,
    page_title TEXT,
    PRIMARY KEY (user_id, page_id),
);
```

3. `/domains/{domain_id}/pages`

- use domain_pages

4. `/pages/{page_id}`

```ddl
CREATE TABLE wiki.pages (
    page_id INT,
    page_title TEXT,
    domain TEXT,
    PRIMARY KEY (page_id, domain),
);
```

5. `/pages-by_users/?from={from}&to={to}`
    
```ddl
CREATE TABLE wiki.pages_by_date (
    created_at TEXT, -- in the format 'YYYY-MM-DD:hh:mm:ss' with allowed filtering
    page_id INT,
    page_title TEXT,
    user_id INT,
    user_name TEXT,
    domain TEXT,
    PRIMARY KEY (created_at, page_id),
);
```

## Categorie A (pre-aggregated queries)

1. `/domains/stats`

```ddl
CREATE TABLE wiki.domain_stats (
    created_at TEXT, -- in the format 'YYYY-MM-DD:hh'
    domain TEXT,
    page_id INT,
    user_is_bot BOOLEAN,
    PRIMARY KEY ((created_at, user_is_bot), domain)
);
```

```sql
COUNT (*) FROM domain_stats WHERE created_at = '2024-05-24:hh' 
            AND user_is_bot IN (true, false)
            AND domain = 'zh.wikipedia.org';
```

2. `/domains/stats/by_bots`

```sql
COUNT (*) FROM domain_stats WHERE created_at = '2024-05-24:hh' 
            AND user_is_bot = true
            AND domain = 'zh.wikipedia.org';
```
3. `/users/most-productive`

- use pages_by_date


```python

prev_hour = None
current_hour = None

while True:
    current_hour = get_current_hour()
    if current_hour != prev_hour:
        prev_hour = current_hour
        recalculate_stats(current_hour)
        save_stats(current_hour)
    time.sleep(60)
```


