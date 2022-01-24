0.5.0 (2022-01-25)
******************

- added tests
- code refactoring
- tox, linters, cicd tests


0.1.4.8 (2021-11-19)
********************

- added urljoin instead of concatenation
- updated except_shell decorator


0.1.4.7 (2021-08-19)
********************

- Added lazy object to remote user middleware


0.1.4.6 (2021-07-28)
********************

- Added error process function when error occur in microservice

0.1.4.5 (2021-06-25)
********************

- Changed data type to 'json' in put method

0.1.4.4 (2021-06-23)
********************

- Fix reverse_url in class method microservice_response

0.1.4.3 (2021-06-19)
********************

- Fix class method microservice_response

0.1.4.2 (2021-06-07)
********************

- Added class method microservice_response

0.1.4.1 (2021-05-18)
********************

- Fix bug whe remote user in custom headers has been rewritten by user_id

0.1.4.0 (2021-05-17)
********************

- Updated and renamed ConnectionService (Service) for opportunities to send requests throughout celery or signals, where request obj is not available

0.1.3.6 (2021-05-12)
********************

- Added opportunities to use single headers for request


0.1.3.5 (2021-04-26)
********************

- Added response obj to error handler


0.1.3.4 (2021-04-15)
********************

- Fixed remote user middleware when id is not integer


0.1.3.3 (2021-04-09)
********************
- Fixed and added Union typing in post method
- Added error handler method if request to microservice return None
- Added error_code variable
- Added different typing


0.1.3 (2021-04-06)
******************
- Added logger if connection refused
- Added cookies param setting for request to microservice

0.1.2 (2021-04-03)
******************

- Set getattr and renamed settings param CUSTOMER_HOST to GATEWAY_HOST for pagination response
- Add getattr for settings API_KEY_HEADER param
