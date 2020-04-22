- Patty Jula pattyjula@gmail.com

# LA City COVID19 data by neighborhood webscraping 
LA County Public Health has been providing daily counts of the number of cases and 
rates Los Angeles County from COVID-19. This script provides a way to download the day's counts, 
load to a database, in this case a CSV, and join to a Los Angeles neighborhood shapefile. 

## Data ource: <http://publichealth.lacounty.gov/media/Coronavirus/locations.htm>
### Note:
This type of webscraping is only available from sites that reveal their source code. 
The best practice is to ask permission before scraping so an organization's servers 
are not overloaded.

# Content	

The output of this script loads to ./data and the shapefile is found there as well. Also 
found there is the neighborhood_storage.csv which contains the daily pulls.