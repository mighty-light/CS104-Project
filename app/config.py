uploaded_files = []
TIME_LADDER = ['year', 'month', 'date', 'hour', 'minute', 'second']
FROM_TIME_LADDER = [f"from_{TIME}" for TIME in TIME_LADDER]
TO_TIME_LADDER = [f"to_{TIME}" for TIME in TIME_LADDER]
STRUCTURED_CSV_FOLDER = 'csv'
VALIDATOR_FOLDER = 'Validator'
PARSER_FOLDER = 'Parser'
FILTER_SCRIPT_FOLDER = 'Filter'
IMAGE_FOLDER = 'img'
SUPPORTED_LOG_FORMATS = ['apache', 'android', 'syslog']
