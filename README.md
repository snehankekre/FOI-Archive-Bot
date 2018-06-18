# Freedom of Information Request Archive Bot

The goal of this simple python script is to permanently archive Freedom of Information Requests from [Right to Know](https://righttoknow.org.au) on the Internet Archive's [Wayback Machine](https://archive.org/web/)

### Installation

⚠ Python v2.7 is required

You will need the following python packages installed: archiveis, stem

```sh
pip install -r requirements.txt
```

### Usage

```
usage: FOI_Archive_Bot.py -s from_request -e to_request -r retries -l log_urls_to_file.txt

arguments:
  -h, --help            show this help message and exit
  -s from_request, --start from_request
                        FOI request number to start archiving from (default=1)
  -e to_request, --end to_request
                        FOI request number to stop archiving at (default=5000
  -r retries, --retries retries
                        set max number of retries when bot encounters a
                        connection error (default=3)
  -l log_urls_to_file, --log log_urls_to_file
                        log archived urls to a file
```

### Example output

![Archives FOI requests](https://i.imgur.com/qTtSbp0.png)

License
----
GNU GPLv3



