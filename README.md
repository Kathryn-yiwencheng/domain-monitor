# Domain Monitor

## API limitation 

The primary limitation of the API is that only 50 records returned in a given query. The documentation indicates there are page and limit attributes; however, these attributes seem to be ignored.

To attempt to overcome this limitation and retrieve more domains, we can try adding various countires and zone parameters to our queries.

We begin by querying by each country that is present in our database, but in some cases, country is not present. For this we also query with `country` omitted. For each country, as well as the omitted country query, we identify if the results are truncated, and in the event they are, we query again with each zone that is present in our databases specified.

## Data collection strategy

We will make queries for search terms found in the `search` table.

For each query, we will query, both `isDead=false` and `isDead=true`, and we will begin with searching for each known country, as well as with country omitted. After finding each country result, if the result is truncated, we will search again with zones specified. If in this case we still find truncated results, we will log a warning with the search parameters as well as the length of the truncated result set.

## Domain removal detection

There are three distinct ways in which removed domains may be identified.
    - Dead: The domain is found in the `isDead=true` query. 
    - Old: A new registration with a new `create_date` is found. 
    - Stale: The domain no longer appears in search results. 

## Setup and execution

Step 1: Load python requirements to the desired environment. 
```
pip install -r requirements.txt
```

Step 2: Configure database and load initial database migration

Update database configuration in `domain_monitor/config.py`.

```
python manage.py db upgrade
```

Alternatively, the schema may be loaded from the file `domain_monitor.sql` using the `psql` command.

Step 3: Populate search queries
```
python manage.py load_search_string lava
```

Step 4: Load data
```
python manage.py run_merge_task
```
Logs can be viewed in the `task.log` file which is appended to during every `merge_task` run.

