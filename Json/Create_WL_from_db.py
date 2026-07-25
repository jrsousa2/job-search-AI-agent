# READS DATABASE AND CREATES WATCHLIST JSON FILE
# BELOW ARE THE FILES I NEED

import json
import re
import sqlite3

# ADD SUBOLDER scripts
from pathlib import Path
import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# IMPORT
from Repo_root import ATS_DB, WATCHLIST
from Exp_db_to_Excel import Exp_db_to_Excel
from print_to_log import print_to_log

INDUSTRY_KEYWORDS = {
    "insurance": ["insurance", "assurance", "casualty", "property", "mutual", "life",
                  "reinsurance", "underwriter", "claim", "indemnity", "accident" ],

    "banking": ["bank", "financial", "finance", "capital", "credit", "lending",
                        "mortgage", "trust", "fund", "investment", "wealth", "securities"],

    "HC": ["health", "hospital", "medical", "clinic", "cross", "pharma",
                   "biotech", "care", "healthcare" ],
    
    "other": ["market", "analytics"]               
}

insurance = ["USAA", "Allstate", "Amerisure", "Travelers", "Nationwide", "Hartford", "Humana",
            "CVS", "Brown & Brown", "Prudential", "Elevance", "Kemper", "Sun Life",
            "Radian", "CNA", "Markel", "Arch Capital", "AIG", "Relation Insurance",
            "SWBC", "GEICO", "State Farm", "Liberty Mutual", "Erie", "Chubb", "Assurant",
            "Sedgwick", "First American", "ICW Group", "American Family", "Auto-Owners",
            "Everest", "EverQuote", "Ethos Life", "MetLife", "New York Life", "Guardian Life", "Lincoln",
            "MassMutual", "Principal Financial", "Voya", "Unum",
            "Aflac", "Globe Life", "Reinsurance Group of America", "Genworth",
            "Protective Life", "Pacific Life", "Thrivent", "TIAA", "Renaissance",
            "Berkshire", "Bristol West", "Amica Insurance", "Hanover Insurance",
            "Selective", "W.R. Berkley", "AXA XL", "QBE", "Ryan", "Guidewire",
            "Tokio Marine", "Sompo International", "Zurich", "Argo",
            "Swiss Re", "Munich Re", "Hannover Re", "SCOR", "Hiscox",
            "Transamerica", "Penn Mutual", "Securian",
            "Northwestern Mutual", "Horace Mann", "Unum",
            "OneAmerica", "Ameritas", "Vanguard",
            "CareFirst", "PURE Insurance", "Lemonade", "Root Insurance",
            "Hippo Insurance", "Kin Insurance", "Clearcover",
            "Pie Insurance", "Next Insurance", "Coalition"]

banking = ["Citi", "Wells Fargo", "Regions Bank", "Fifth Third", "53RD", "Barclays",
         "Bank of America", "JPMorgan", "Capital One", "PNC Financial Services",
         "U.S. Bank", "American Express", "Discover Financial", "FNB", "Sumitomo",
         "Morgan Stanley", "Truist", "Chime", "SoFi", "Betterment",
         "Affirm", "Brex", "Ramp", "Marqeta", "Robinhood", "Trade Republic",
         "N26", "SumUp", "Qonto", "Mercury", "Plaid", "Block Inc", "Adyen",
         "Goldman Sachs", "Deutsche", "HSBC", "UBS", "Credit Suisse",
         "Lazard", "Jefferies", "Raymond James", "Stifel", "William Blair",
         "RBC Capital Markets", "TD Bank", "BMO", "Fifth Third", "Huntington",
         "KeyBank", "M&T", "Citizens Bank", "First Citizens",
         "First Horizon", "Webster Bank", "Zions Bank", "Comerica",
         "Cullen/Frost", "East West Bank", "Silicon Valley",
         "BankUnited", "Synovus", "Old National", "Wintrust",
         "Popular Bank", "Santander", "ING Bank", "ING Group", "BNP", "Societe Generale",
         "NatWest", "Lloyds", "Standard Chartered",
         "Macquarie Group", "Nomura", "Mizuho", "SMBC",
         "Interactive", "Fidelity", "Schwab",
         "T. Rowe Price", "BlackRock", "Blackstone", "Invesco", "Franklin Templeton",
         "Nuveen", "Janus Henderson", "AllianceBernstein",
         "Acorns", "Current", "Varo Bank", "Dave", "SoFi Bank",
         "Klarna", "Wise", "Revolut", "Checkout", "Toast",
         "Fiserv", "FIS", "Global Payments", "ACI Worldwide"]

#HC = []

HC = ["Centene", "Trinity", "Humana", "CVS", "Elevance",
      "UHG", "UnitedHealth", "Cigna", "Molina",
      "Cardinal", "Doximity","One Medical", "Highmark Health", 
      "Oscar Health", "Blue Cross", "Blue Shield"]

other = ["LexisNexis", "Equifax", "Nielsen", "Bradstreet"]

F500 = [
"Walmart", "Amazon", "UnitedHealth", "Apple", "CVS Health", "Berkshire", "Alphabet", "Exxon", 
"McKesson", "Cencora", "Microsoft", "JPMorgan", "Costco", "Cardinal Health", "Chevron", "Ford", 
"Bank of America", "General Motors", "Elevance Health", "Citigroup", "Centene", "Home Depot", "Fannie Mae", "Kroger", 
"Verizon", "Walgreens", "Phillips 66", "Valero Energy", "Target", "Meta Platforms", 
"State Farm", "Comcast", "Marathon Petroleum", "PepsiCo", "UPS", "Johnson & Johnson", 
"Archer Daniels", "FedEx", "Wells Fargo", "Lockheed", "Tesla", "Procter", 
"Albertsons", "General Electric", "Lowe's", "HCA Healthcare", "Goldman Sachs", "Morgan Stanley", 
"Raytheon", "Progressive", "Caterpillar", "IBM", "MetLife", "Nationwide", "AIG", "Deere", 
"Merck", "Pfizer", "ConocoPhillips", "Intel", "HP", "Cisco", "Oracle", "Coca-Cola", "Disney", "TIAA", 
"American Express", "Publix", "Delta Air Lines", "United Airlines", "Charter Communications", 
"AbbVie", "Boeing", "New York Life", "Liberty Mutual", "TJX Companies", "Best Buy", "Nike", 
"Thermo Fisher", "Honeywell", "Nationwide Mutual", "Deutsche", "Capital One", 
"PNC Financial Services", "Truist", "Bancorp", "Morgan Stanley", "Schwab", 
"PayPal", "Mastercard", "Visa", "T-Mobile", "AT&T", "Broadcom", "Nvidia", "Qualcomm", "Adobe", 
"Salesforce", "ServiceNow", "Booking Holdings", "Uber", "Starbucks", "Marriott", 
"Hilton Worldwide", "American Airlines", "Southwest Airlines", "Lumen", 
"Kraft Heinz", "Mondelez", "General Dynamics", "Northrop", 
"L3Harris", "RTX", "Eaton", "3M", "Dow", "DuPont", "Sherwin-Williams", 
"PPG Industries", "Nucor", "Steel Dynamics", "Freeport-McMoRan", "Cleveland-Cliffs", 
"United States Steel", "Alcoa", "Parker-Hannifin", "Emerson Electric", "Illinois Tool Works", 
"Black & Decker", "Whirlpool", "Carrier Global", "Johnson Controls", "Trane Technologies", 
"Cummins", "PACCAR", "Tesla", "AutoZone", "O'Reilly", "Advance Auto Parts", "CarMax", 
"Genuine Parts", "LKQ", "AutoNation", "Lithia Motors", "Penske Automotive", "Carvana", "D.R. Horton", 
"Lennar", "PulteGroup", "NVR", "Toll Brothers", "CBRE Group", "JLL", "Cushman & Wakefield", "Realogy", 
"Waste Management", "Republic Services", "Clean Harbors", "Verisk", "S&P Global", 
"Moody's", "FactSet", "ICE (Intercontinental Exchange)", "CME Group", "Nasdaq", "Northern Trust", 
"State Street", "BlackRock", "Vanguard", "Invesco", "Franklin Templeton", "T. Rowe Price", 
"Fidelity Investments", "Discover Financial", "Synchrony Financial", "Ally Financial", 
"American National", "Hartford Financial", "Travelers", "Chubb", "CNA", "Aflac", 
"Prudential Financial", "Lincoln Financial", "Principal Financial", "Unum Group", "Genworth", 
"Cigna Group", "Molina Healthcare", "Oscar Health", "HUMANA", "DaVita", "Quest Diagnostics", 
"Labcorp", "Baxter International", "Becton Dickinson", "Stryker", "Boston Scientific", 
"Zimmer Biomet", "Danaher", "GE HealthCare", "ResMed", "Amgen", "Gilead Sciences", 
"Bristol Myers", "Eli Lilly", "Regeneron", "Vertex Pharmaceuticals", "Biogen", 
"Moderna", "Viatris", "Organon", "Zoetis", "Elanco Animal", "Patterson Companies", 
"Henry Schein", "McCormick", "Campbell Soup", "Kellogg", "Conagra Brands", "J.M. Smucker", 
"Hormel Foods", "Tyson Foods", "Pilgrim's Pride", "Smithfield Foods", "JBS USA", "Sysco", 
"Performance Food", "US Foods", "Restaurant Brands", "Yum Brands", 
"Darden Restaurants", "Chipotle", "Domino's Pizza", "Wendy's", "Macy's", 
"Kohl's", "Nordstrom", "Gap", "Ross Stores", "TJX Companies", "Williams-Sonoma", "Bath & Body", 
"Ralph Lauren", "Levi Strauss", "VF Corporation", "Lululemon", "Under Armour", "Yeti Holdings", 
"Wayfair", "eBay", "Etsy", "Expedia", "Tripadvisor", "Caesars", "MGM Resorts", 
"Las Vegas Sands", "Wynn Resorts", "Carnival", "Royal Caribbean", "Norwegian Cruise Line", 
"Vail Resorts", "Live Nation", "Warner Bros.", "Paramount Global", "Fox Corporation", 
"News Corp", "Spotify", "Zoom Video", "Dropbox", "Dell", "Super Micro Computer", 
"Western Digital", "Seagate Technology", "Micron Technology", "Applied Materials", "Lam Research", 
"KLA Corporation", "Marvell Technology", "Analog Devices", "Texas Instruments", "Microchip Technology", 
"NXP Semiconductors", "ON Semiconductor", "Skyworks Solutions", "Jabil", "Flex", "Corning", "TE Connectivity", 
"Ametek", "Rockwell Automation", "Autodesk", "Intuit", "Paychex", "ADP", "FIS", "Fiserv", "Block", "Coinbase", 
"Robinhood", "Toast", "Datadog", "Palantir Technologies", "Leidos", "SAIC", "CACI International", 
"Booz Allen Hamilton", "Parsons", "AECOM", "Jacobs Solutions", "Fluor", "KBR", "Dover", "Fortive", "Xylem", 
"Pentair", "Westinghouse", "Constellation Energy", "NextEra Energy", "Duke Energy", "Southern Company", 
"Dominion Energy", "American Electric", "Exelon", "Edison International", "PG&E", "Sempra", "Entergy", 
"FirstEnergy", "NRG Energy", "AES", "Vistra", "PPL Corporation", "CenterPoint Energy", "Atmos Energy", 
"NiSource", "ONE Gas", "Williams Companies", "Kinder Morgan", "Enterprise Products", "Energy Transfer", 
"Plains All American", "Occidental Petroleum", "Devon Energy", "EOG Resources", "Hess", "Marathon Oil", 
"APA Corporation", "Halliburton", "Baker Hughes", "Schlumberger", "NOV", "Weatherford", "Cummins", 
"Westinghouse Air Brake Technologies", "Textron", "Huntington Ingalls Industries", "Oshkosh", "Allegiant Travel", 
"JetBlue Airways", "Alaska Air", "Spirit Airlines", "Avis Budget", "Hertz", "Ryder System", "XPO", 
"Old Dominion Freight Line", "J.B. Hunt", "Knight-Swift", "Expeditors International", 
"CH Robinson", "GXO Logistics", "C.H. Robinson", "Toll Group", "Ingram Micro", "CDW", "Arrow Electronics", 
"Avnet", "Insight Enterprises", "TD SYNNEX", "Core & Main", "Fastenal", "W.W. Grainger", 
"MSC Industrial Supply", "HD Supply", "Builders FirstSource", "Masco", "Mohawk Industries", 
"Mosaic", "CF Industries", "FMC Corporation", "International Paper", "WestRock", "Packaging Corporation of America", 
"Ball Corporation", "Crown Holdings", "Avery Dennison", "Kimberly-Clark", "Colgate-Palmolive", "Church & Dwight", 
"Clorox", "Estee Lauder", "Kenvue", "Verizon", "Tegna", "Gannett", "Gray Television", "Sinclair Broadcast", 
"Cox Enterprises", "Hearst", "Thomson Reuters", "News Corp", "Walt Disney", "Comcast", "Charter Communications", 
"Dish Network", "EchoStar", "T-Mobile", "AT&T", "Ciena", "Juniper Networks", "Arista Networks", "NetApp", 
"Pure Storage", "Snowflake", "Cloudflare", "CrowdStrike", "Fortinet", "Palo Alto Networks", "Zscaler", "Okta", 
"MongoDB", "Elastic", "Splunk", "Workday", "ServiceNow", "Atlassian", "Twilio", "HubSpot", "Paycom", "Paylocity", 
"Ceridian", "Gartner", "Cognizant", "Accenture", "DXC Technology", "EPAM Systems", "Globant", "Wipro", "Infosys", 
"HCLTech", "NTT Data", "Kyndryl", "Rackspace", "Science Applications International", 
"CACI", "Maximus", "Peraton", "ICF", "ManTech", "Amentum", "SAIC", "Concentrix", "Teleperformance", "TTEC", 
"Kelly Services", "ManpowerGroup", "Robert Half", "Adecco", "Korn Ferry", "Randstad", "FedEx", "UPS", "USPS", 
"Penske", "Roper Technologies", "Trimble", "Keysight Technologies", "Agilent Technologies", "Hewlett Packard Enterprise", 
"Western Union", "Principal Financial", "Lincoln National", "Raymond James Financial", "Ameriprise Financial", 
"Jefferies Financial", "Regions Financial", "Fifth Third", "KeyCorp", "Huntington Bancshares", "M&T", 
"Citizens Financial", "Comerica", "Zions Bancorporation", "Synovus Financial", "First Citizens", 
"Webster Financial", "Bancorp", "Bank of", "Popular Inc.", "F.N.B." 
]

# INCREASES LIKELIHOOD TO MATCH
def normalize(s):
    return re.sub(r"[^a-z0-9]", "", s.lower().strip())


# REMOVES BLANK SPACE TOO
def matches_industry(company):
    name = normalize(company)

    # Check known company lists first
    industry_companies = {
        "insurance": insurance,
        "banking": banking,
        "HC": HC,
        "F500": F500,
        "other": other}

    for category, companies in industry_companies.items():
        for comp in companies:
            if normalize(comp) in name:
                return category

    for category, keywords in INDUSTRY_KEYWORDS.items():
        for kw in keywords:
            if normalize(kw) in name:
               return category

    return None

def prettify_company(slug: str) -> str:
    """
    Convert tenant slug to a readable placeholder company name.
    Examples:
        citi -> Citi
        3m -> 3M
        7eleven -> 7Eleven
        bank-of-america -> Bank Of America
    """
    parts = re.split(r"[-_]", slug)
    return " ".join(p.capitalize() for p in parts)

def create_watchlist(input_db, output_file, log_file):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            company,
            platform,
            slug,
            last_probed_at
        FROM ATS
    """)

    rows = cursor.fetchall()

    output = []

    for company, platform, slug, last_probed_at in rows:
        # ATS-discovered records
        # create readable name from slug
        if last_probed_at is not None:
            # take first slug component
            company = prettify_company(slug.split("/")[0])

        # keep chosen industry matches
        industry = matches_industry(company)

        # if "guidewire" in company.lower():
        # if industry in ["insurance", "banking", "other"]:   
        if platform=="icims" and industry in ["banking"]:     
            # print(company, "->", industry)
            print_to_log(log_file,"Company: {} -> Industry: {}\n",company, industry)
            output.append({
            "company": company,
            "platform": platform,
            "slug": slug })

    conn.close()

    # alphabetical order
    output.sort(key=lambda x: x["company"].lower())
    with open(output_file, "w", encoding="utf-8") as f:
        #json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("[\n")
        for i, item in enumerate(output):
            comma = "," if i < len(output) - 1 else ""
            f.write("  " + json.dumps(item, ensure_ascii=False) + comma + "\n")
        f.write("]\n")

    # THE END
    print(f"Wrote {len(output):,} entries to {output_file}")


if __name__ == "__main__":
    # CALLS FUNCTIONS
    create_watchlist(ATS_DB, WATCHLIST, r"D:\Agent\Logs\Check_industry.txt")