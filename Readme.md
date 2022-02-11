# Adjust Home Task

## Requirements

1. Python 3.9
2. Please, use virtual environment
3. Update Python dependencies tooling:
    ```shell
    pip install -U pip pip-tools setuptools wheel
    ```
4. Install project requirements
    ```shell
    pip install -r requirements.txt
    ```

## Starting the project

1. Apply migrations
   ```shell
   python3 manage.py migrate
   ```
2. Create superuser
   ```shell
   python3 manage.py createsuperuser --email %email% --username %username%
   ```
3. Load test data from [this file](https://gist.github.com/kotik/3baa5f53997cce85cc0336cb1256ba8b/#file-dataset-csv)
   ```shell
   python manage.py load_test_data %path_to_file%
   ```
   You may check loaded data on [this page](http://127.0.0.1:8000/admin/metrics/metric/)
4. Start the Django application:
   ```shell
   python manage.py runserver
   ```
   
   If you want to check what SQL queries executed during the application work, you may run 
   ```shell
   python manage.py runserver_plus --print-sql
   ```

## API

### Common use-cases

1. [Link](http://127.0.0.1:8000/metrics/?group_by=channel&display_columns=impressions,clicks&order_by=-clicks&date_range_before=2017-05-31)
Show the number of impressions and clicks that occurred before the 1st of June 2017,
broken down by channel and country, sorted by clicks in descending order

2. [Link](http://127.0.0.1:8000/metrics/?group_by=date&display_columns=installs&order_by=date&date_range_before=2017-05-31&date_range_after=2017-05-01&os=ios)
Show the number of installs that occurred in May of 2017 on iOS,
broken down by date, sorted by date in ascending order.

3. [Link](http://127.0.0.1:8000/metrics/?group_by=os&display_columns=revenue&order_by=-revenue&date=2017-06-01) 
Show revenue, earned on June 1, 2017 in US,
broken down by operating system and sorted by revenue in descending order.

4. [Link](http://127.0.0.1:8000/metrics/?group_by=channel&display_columns=spend,cpi&order_by=-cpi&country=CA)
Show CPI and spend for Canada (CA)broken down by channel ordered by CPI in descending order.

### Metric List API

**URL**: `/metric/`

**Pagination**: The API supports pagination and uses two parameters:
  - `limit`
  - `offset`
    
Example: `metrics/?limit=100&offset=100`

```json
{
    "count": 1096,
    "next": "http://127.0.0.1:8000/metrics/?limit=100&offset=200&ordering=country%2C-date",
    "previous": "http://127.0.0.1:8000/metrics/?limit=100&ordering=country%2C-date",
    "results": [
        {
            "id": 273,
            "date": "2017-05-24",
            "channel": "facebook",
            "country": "CA",
            "os": "ios",
            "impressions": 3428,
            "clicks": 97,
            "installs": 25,
            "spend": 38.8,
            "revenue": 30.0
        },
        {
            "id": 281,
            "date": "2017-05-24",
            "channel": "google",
            "country": "CA",
            "os": "ios",
            "impressions": 3313,
            "clicks": 108,
            "installs": 29,
            "spend": 33.33,
            "revenue": 90.0
        }
    ]
}
```
    
**Ordering**: The API supports ordering by single or multiple fields and uses `ordering` parameter.
Ascending order is default. To use descending order, add a `-` symbol before column name.
    
Example: 

```json
{
  "count": 1096,
  "next": "http://127.0.0.1:8000/metrics/?limit=100&offset=100&ordering=country%2C-date",
  "previous": null,
  "results": [
      {
          "id": 1064,
          "date": "2017-06-15",
          "channel": "chartboost",
          "country": "CA",
          "os": "ios",
          "impressions": 3251,
          "clicks": 107,
          "installs": 27,
          "spend": 54.0,
          "revenue": 40.0
      },
      {
          "id": 1072,
          "date": "2017-06-14",
          "channel": "facebook",
          "country": "CA",
          "os": "android",
          "impressions": 3456,
          "clicks": 93,
          "installs": 18,
          "spend": 37.2,
          "revenue": 20.0
      },
      {
          "id": 1078,
          "date": "2017-06-15",
          "channel": "google",
          "country": "DE",
          "os": "android",
          "impressions": 3237,
          "clicks": 102,
          "installs": 28,
          "spend": 33.33,
          "revenue": 90.0
      },
      {
          "id": 1086,
          "date": "2017-06-11",
          "channel": "unityads",
          "country": "DE",
          "os": "android",
          "impressions": 3271,
          "clicks": 131,
          "installs": 24,
          "spend": 48.0,
          "revenue": 10.0
      }
  ]
}
```

**Filtering**: The API supports data filtering by the following fields:
   - `date` - by exact date in `YYYY-MM-DD` format;
   - `channel` - by exact channel name;
   - `os` - by exact os name;
   - `country` - by single (`country=CA`) or multiple (`country=CA&country=DE`) countries;
   - `date_range` - by date range including borders. 
   Use `date_range_after` to specify the beginning of the range, and `date_range_before` to specify the end.
   You may use only `_before` or `_after`

**Aggregation**: The API supports `SELECT ... GROUP BY` data aggregation by parameters:
   - `group_by` - one or more columns to group data by. You may group the data by any column except `date`
   and columns specified in `display_columns` parameter.
   - `display_columns` - one or more columns to aggregate. The default aggregation is `SUM`.
   You may specify another aggregation function using this syntax: `%column_name%__%aggregation_name%`.
   Supported aggregations:
     - `__sum` - uses `SUM` aggregation.
   
   **NOTE**: Aggregation performed only when both `group_by` and `display_columns` defined.

Example: `metrics/?group_by=channel&display_columns=spend,cpi&order_by=-cpi&country=CA`

```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "channel": "chartboost",
            "spend": 1274.0,
            "cpi": 2.0
        },
        {
            "channel": "facebook",
            "spend": 1164.0,
            "cpi": 2.0748663101604277
        },
        {
            "channel": "google",
            "spend": 999.9000000000004,
            "cpi": 1.7419860627177708
        },
        {
            "channel": "unityads",
            "spend": 2642.0,
            "cpi": 2.0
        }
    ]
}
```

## Found issues

During the work on the task found some issues:

1. Common API use-case proposes condition `where date < '2017-06-01'`.
However, the hint below contains the data that received with `where date <= '2017-06-01'` condition.
