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

## API documentation

Metric.objects.values("channel", "country").filter(date__lt='2017-06-01').order_by("channel").annotate(summ=Sum("impressions"))[:4]

## Found issues

During the work on the task found some issues:

1. Common API use-case proposes condition `where date < '2017-06-01'`.
However, the hint below contains the data that received with `where date <= '2017-06-01'` condition.
