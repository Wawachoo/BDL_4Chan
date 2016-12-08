# BDL_4Chan
**Engine API version**: `2.0.0`

A 4Chan engine for BDL. **This engine does not uses the 4Chan API**.


## Installation
```shell
$> git clone https://github.com/Wawachoo/BDL_4Chan
$> cd BDL_4Chan
$> python3.5 setup.py install
```


## Supported URLs
This engine supports URL of type
`http://boards.4chan.org/SECTION/thread/THREAD_ID/THREAD_NAME`. `THREAD_NAME`
is optional. `https://` URL are accepted.


## Repository name
The engine returns the thread name from the URL of from the thread page.


## Metadata
This engine export the following metadata:
* `{thread_section}`: thread section (ex: `g`);
* `{thread_name}`: thread name (ex: `the name of the thread`);
* `{thread_id}`: thread identifier (ex: `1234567`)
