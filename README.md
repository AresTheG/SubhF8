## About SubhF8

SubhF8 is a powerful Python tool designed for analyzing subdomains of websites. This tool can be useful for both penetration testers and web server administrators. SubhF8 is based on open-source intelligence (OSINT) and provides the capability to discover subdomains of a website using various methods.

##  Features
* Search for subdomains of a specified domain.
* Multithreaded processing for improved scanning efficiency.
* Logging with the option to save results.
* Support for two different subdomain databases for scanning.

#### The code automatically creates a folder in the script directory to store the scan results. The folder name is generated based on the domain and the current date and time.

#### Inside the created folder, a log file named 'history_log.log' is created and used to record logs and debugging messages.

#### The code uses two predefined databases for the list of subdomains:
*  'base.txt': This is the default database that contains the default list of subdomains. (114,665 subdomains).
*  'base_large.txt': This is a larger list of subdomains that can be used when the -l or --large flag is specified when running the script. (4,351,335 subdomains).

## Installation

```
git clone https://github.com/AresTheG/subhf8.git
```
Install the required dependencies by running the following commands:

* Installation on Windows:

```
c:\python27\python.exe -m pip install -r requirements.txt
```
* Installation on Linux:
```
sudo pip install -r requirements.txt
```
### If you need to use a large base (more than 4M subdomains), you need to unpack txt from the archive (part 1, part2) into the directory with the script.


## Recommended Python Version:

SubhF8 currently supports  **Python 3**.

## Dependencies:

### This code relies on the following libraries:
* argparse: Command-line argument processing.
* requests: Making HTTP requests.
* re: Regular expressions.
* socket: Socket operations.
* threading: Multithreading.
* time, datetime: Working with time and dates.
* os: Filesystem operations.
* logging: Logging.
* concurrent.futures.ThreadPoolExecutor: Managing threads.
* urllib3: Disabling insecure request warnings.
* urllib.parse.urlparse, urllib.parse.urlunparse: Handling URLs.

## Usage

The SubhF8 script supports the following command-line arguments:

* -d or --domain: A required parameter to specify the domain for which you want to find subdomains.
* -n or --name: An optional parameter to specify the filename for saving results (default: subdomains_list.txt).
* -w or --workers: An optional parameter to specify the number of maximum worker threads (default: 4).
* -l or --large: An optional parameter to use a large subdomain database (default: base.txt, -l uses base_large.txt).

### Example usage:

```
python SubhF8.py -d example.com
```
or
```
python SubhF8.py -d example.com -n results.txt -w 8 -l
```

## Development Instructions
* To make changes to the code, ensure that you have installed the necessary libraries and environment.
* Changes may require updating the list of subdomains (files 'base.txt' and 'base_large.txt').
* After development, submit a pull request with a description of the changes made.

## License

SubhF8 is licensed under the GNU GPL license. take a look at the [LICENSE](https://github.com/aboul3la/Sublist3r/blob/master/LICENSE) for more information.

## Credits

The code is developed by Ares

## Version

**Current version is 1.0.0**
