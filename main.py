from array import array
import math
import json
import requests
import currency_symbols

api_root = "https://api.apilayer.com/exchangerates_data/"

#exchange class used for all requests to the exchange
class exchange:
    #Class member variable/s
    session: requests.Session
    valid_tickers: array
    _base_currency: str

    #Get list of valid currency tickers from the exchange API
    def get_tickers(self) -> dict:
        #Send request to exchange API to retrieve ticker data
        response: requests.Response = self.session.get(api_root + "symbols")
        #Request success
        if response:
            json_response = json.loads(response.text)
            #Return array of all tickers
            return json_response["symbols"]
        #Request failed
        else:
            print("Requests failed. Status", response.status_code)
            #Return an empty array
            return []

    #Class constructor
    def __init__(self, base_currency: str):
        self.session = requests.Session()
        #Default headers for every request
        self.session.headers = {
            "apikey":"8HBhCE5tl7OlugU6vRaxHmEZhnUZui2M"
        }
        self.valid_tickers = self.get_tickers()
        self._base_currency = base_currency

    #Get conversion rates for the given currency to another currency
    def get_rate(self, from_cur: str, to_cur: str) -> float:
        #Send a request to the exchange api to retrieve exchange rates
        response: requests.Response = self.session.get(api_root + f"latest?symbols={to_cur}&base={from_cur}")
        #Check if the request was successful
        if response:
            #Parse plaintext into json object
            json_response = json.loads(response.text)
            return json_response["rates"][to_cur]
        else:
            return 0.0

    #Check if a provided ticker is valid
    def is_valid_ticker(self, ticker: str) -> bool:
        #Iterate through each entry in valid ticker array
        for entry in self.valid_tickers:
            #Test whether the current entry is the same as our ticker or not
            if entry == ticker:
                return True
        #Return false after fully iterating the array and finding no entries
        return False

    #Get value of base currency in foreign currency
    def to_currency(self, amount: float, to_cur: str) -> float:
        #Check if provided ticker is convertable
        if not self.is_valid_ticker(to_cur):
            print("Invalid Ticker supplied!")
            return 0.0
        #Get exchange rate
        rate: float = self.get_rate(self._base_currency, to_cur)
        return rate * amount

    #Get value of foreign currency in base currency
    def from_currency(self, amount: float, from_cur: str) -> float:
        #Check if provided ticker is valid
        if not self.is_valid_ticker(from_cur):
            print("Invalid Ticker supplied!")
            return 0.0
        #Get exchange rate
        rate: float = self.get_rate(from_cur, self._base_currency)
        return rate * amount

class time_zone:
    code: str
    description: str
    gmt_offset_hours: int

    def __init__(self, _code, hours, _description):
        self.code = _code
        self.gmt_offset_hours = hours
        self.description = _description

time_zones = [
    time_zone("GMT", 0, "Greenwich Meridian Time - London, Lisbon, Dublin, Reykjavik"),
    time_zone("CET", 1, "Central European Time - Oslo, Stockholm, Copenhagen, Amsterdam, Paris, Madrid, Zurich, Vienna, Warsaw"),
    time_zone("EET", 2, "Eastern European Time - Helsinki, Kyiv, Cairo, Johannesburg, Cape Town, Tel-Aviv, Athens"),
    time_zone("MSK", 3, "Moscow Time - Moscow, St. Petersberg, Istanbul, Doha, Manama"),
    time_zone("AMT", 4, "Armenia Time - Yerevan, Dubai, "),
    time_zone("PKT", 5, "Pakistan Standard Time - Karachi, New Delhi, Mumbai"),
    time_zone("OMSK", 6, "Omsk Time - Bishkek, Omsk, Dhaka"),
    time_zone("KRAT", 7, "Kranoyask Time - Bangkok, Ho Chi Minh City, Hano, Vientiane, Jakarta, Phnom Penh"),
    time_zone("AWST", 8, "Western Australian Standard Time - Beijing, Shanghai, Guangzhou, Hong Kong, Macau, Taipei, Manila, Kuala Lumpur, Singapore, Perth"),
    time_zone("JST", 9, "Japan Standard Time - Tokyo, Osaka, Okinawa, Darwin, Alice Springs, Adelaide"),
    time_zone("AEST", 10, "Eastern Australian Standard Time - Melbourne, Sydney, Brisbane, Townsville, Hobart, Port Moresby"),
    time_zone("SAKT", 11, "Sakhalin Standard Time - New Caledonia, Solomon Islands"),
    time_zone("NZST", 12, "New Zealand Standard Time - Auckland, Christchurch, Queenstown, Nauru, Marshall Islands, Fiji, Tuvalu"),
    time_zone("WAT", -1, "West Africa Time "),
    time_zone("AT", -2, "Azores Time"),
    time_zone("ART", -3, "Argentina Time - Brasilia, Rio De Janeiro, Sao Paulo, Buenos Aires, Cordoba, Monte Video"),
    time_zone("AST", -4, "Atlantic Standard Time - Caribean, La Paz, Santiago, Caracas"),
    time_zone("EST", -5, "Eastern Standard Time - New York, Washington D.C, Toronto, Quebec, Havana, Kingston, Panama"),
    time_zone("CST", -6, "Central Standard Time - Winnepeg, Chicago, Dallas, Mexico City"),
    time_zone("MST", -7, "Mountain Standard Time - Edmonton, Salt Lake City, Alberqueque, Denver"),
    time_zone("PST", -8, "Pacific Standard Time - Vancouver, Seattle, Los Angeles, Tijuana, San Francisco"),
    time_zone("AKST", -9, "Alaska Standard Time - Anchorage, "),
    time_zone("HST", -10, "Hawaii Standard Time - Honolulu, Maui, French Polynesia"),
    time_zone("NT", -11, "Nome Time"),
    time_zone("IDLW", -12, "International Date Line West - Tonga, Samoa"),
]

#Check if supplied timezone is supported
def is_valid_timezone(zone_code: str) -> bool:
    #Iterate each time zone
    for zone in time_zones:
        #Test if the zone codes are the same
        if zone.code == zone_code:
            #Return true as timezone was found
            return True

    #Return false as iteration was complete without returning.
    return False

#Get timezone's gmt offset
def get_gmt_offset(zone_code: str):
    #Iterate each time zone
    for zone in time_zones:
        #Test if the zone codes are the same
        if zone.code == zone_code:
            #Return gmt offset
            return zone.gmt_offset_hours
    #Return zero as zone wasn't found
    return 0
    
#Function used to extract hour and minutes from a given string
def parse_time(time_str: str) -> dict:
    #Dictionary to be returned
    time_dict: dict = {
        "hours":0,
        "minutes":0
    }

    #Check length of string. If it's not 5 then return nothing.
    if len(time_str) != 5:
        print("Bad string passed!")
        return time_dict

    #Can safely cast into integers now
    time_dict["hours"] = int(time_str[0:2])
    time_dict["minutes"] = int(time_str[3:5])

    return time_dict

#Check if given timestring is valid
def is_valid_time(time_str: str) -> bool:
    hours: str = time_str[0:2]
    minutes: str = time_str[3:5]

    #If time string isn't 5 characters in length
    if len(time_str) != 5:
        print("Time too long or short!")
        return False

    #Doesn't contain colon
    if time_str[2] != ':':
        print("Add separating colon!")
        return False

    #Check if entered time are actually numbers
    if not hours.isnumeric() or not minutes.isnumeric():
        print("Please Enter Numbers!")
        return False
    #Otherwise return true
    else:
         return True

#Convert time from one zone to another
def convert_time(to_code: str, from_code: str, from_time: dict) -> dict:
    return_time = {
        "hours": 0,
        "minutes": from_time["minutes"]
    }

    #Check if provided timezones are not valid
    if not is_valid_timezone(to_code) or not is_valid_timezone(from_code):
        #Return an empty array
        return {}

    #Retrieve GMT offsets for both timezones
    to_gmt_offset: int = get_gmt_offset(to_code)
    from_gmt_offset: int = get_gmt_offset(from_code)

    #Calculate current gmt time
    gmt_hour = from_time["hours"] - from_gmt_offset
    #Funky stuff
    if to_gmt_offset < 0:
        #Add gmt offset to gmt time
        return_time["hours"] = gmt_hour + to_gmt_offset + 1
    elif from_gmt_offset < 0:
        4#Add gmt offset to gmt time
        return_time["hours"] = gmt_hour + to_gmt_offset - 1
    else:
        #Add gmt offset to gmt time
        return_time["hours"] = gmt_hour + to_gmt_offset

    return return_time

def input_float(prompt: str) -> float:
    string: str = input(prompt)
    try:
        return float(string)
    except ValueError:
        print("Please enter a number!")
        return 0.0

def input_int(prompt: str) -> int:
    string: str = input(prompt)
    if string.isnumeric():
        return int(string)
    else:
        print("Please enter a whole number!")
        return 0

#Format time all pretty
def format_time(time: dict) -> str:
    minutes_length = 0
    if time["minutes"] != 0:
        minutes_length = math.floor(math.log10(time['minutes'])) + 1
    time_str = f"{time['hours']}:{time['minutes'] if minutes_length == 2 else '0' + str(time['minutes'])}"  
    return time_str

#Code Entry
def main():
    #Create an instance of the exchange class
    ex: exchange = exchange("AUD")

    #Main loop
    while True:
        print("""1. Convert Currency(FROM AUD)
2. Convert Currency(TO AUD)
3. Convert Time(TO FOREIGN)
4. Convert Time(FROM FOREIGN)
5. List all currencies
6. List all timezones
7. Exit Program.""")

        #Cast string to an integer
        current_function: int = input_int("> ")

        #Test given function index
        #Convert AUD to foreign currency
        if current_function == 1:
            #Ask user for ticker
            foreign_ticker: str = input("Foreign Currency: ").upper()
            #Allow user to re-enter ticker
            while not ex.is_valid_ticker(foreign_ticker):
                print("Invalid ticker entered")
                foreign_ticker = input("Foreign Currency: ").upper()
            #Ask user for amount of AUD
            amount: str = input_float("AUD amount: $")
            #Allow user to re-enter amount
            while not amount:
                amount = input_float("AUD amount: $")

            print(f"${amount} AUD = {currency_symbols.CurrencySymbols.get_symbol(foreign_ticker)}{ex.to_currency(amount, foreign_ticker)}") 

        #Convert foreign currency to AUD
        elif current_function == 2:
            #Ask user for ticker
            foreign_ticker: str = input("Foreign Currency: ").upper()
            #Allow user to re-enter ticker
            while not ex.is_valid_ticker(foreign_ticker):
                print("Invalid ticker entered")
                foreign_ticker = input("Foreign Currency: ").upper()
            #Ask user for amount of AUD
            amount: str = input_float(f"{foreign_ticker} amount: $")
            #Allow user to re-enter amount
            while not amount:
                amount = input_float(f"{foreign_ticker} amount: $")
            print(f"${amount} {currency_symbols.CurrencySymbols.get_symbol(foreign_ticker)} = ${ex.from_currency(amount, foreign_ticker)} AUD") 

        #Convert timezone to foreign from perth
        elif current_function == 3:
            #Retreive time in perth
            perth_time: str = input("Enter Perth time(HH:MM 24 hr): ")
            #Allow user to re-enter time if it's invalid
            while not is_valid_time(perth_time):
                perth_time = input("Enter Perth time(HH:MM 24 hr): ")
            #Parse given time
            parsed_time: dict = parse_time(perth_time)
            #Retrieve timezone to convert to
            code: str = input("Enter Timezone code: ").upper()
            #Allow user to re-enter timezone
            while not is_valid_timezone(code):
                code: str = input("Enter Timezone code: ").upper()
            #Convert time to new zone from AWST(GMT+8)
            converted_time: dict = convert_time(code, "AWST", parsed_time)
            #Correctly format string
            print(format_time(converted_time) + f" {code} 24 hr")
        
        #Convert timezone to perth from foreign
        elif current_function == 4:
            #Read foreign time
            foreign_time: str = input("Enter foreign time(HH:MM 24 hr): ")
            #Allow user to re-enter time if it's invalid
            while not is_valid_time(foreign_time):
                foreign_time = input("Enter foreign time(HH:MM 24 hr): ")
            #Foreign time zone
            foreign_code: str = input("Enter Timezone code: ").upper()
            #Allow user to re-enter timezone
            while not is_valid_timezone(foreign_code):
                foreign_code: str = input("Enter Timezone code: ").upper()
            #Parse the time
            parsed_time: dict = parse_time(foreign_time)
            #Convert the time to AWST(GMT+8)
            converted_time: dict = convert_time("AWST", foreign_code, parsed_time)
            #Output converted time
            print(format_time(converted_time) + " AWST 24 hr")

        #Print supported Currencies
        elif current_function == 5:
            #Retrieve a current list of tickers
            tickers = ex.get_tickers()
            #Iterate through each ticker
            for key in tickers:
                #Print each key and value
                print(key, " | ", tickers[key])
                
        #Print Timezones
        elif current_function == 6:
            #Iterate through each time zone
            for zone in time_zones:
                #Fix spacing
                code_len: int = len(zone.code)
                #Calculate number of spaces required
                spaces: int = 5 - code_len
                #Create formated string
                zone_string: str = zone.code + spaces * " " + "| " + zone.description
                print(zone_string)

        #Program exit
        elif current_function == 7:
            print("Exiting Program...")
            break

        #Unknown code
        else:
            print("Invalid function entered")

#Check if this code is running in the context of __main__
if __name__ == "__main__":
    main()