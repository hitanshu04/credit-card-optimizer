import requests
import PyPDF2
from io import BytesIO

# ARCHITECTURE INFO:
# The live scraping URLs in the config JSON are intentionally left empty for this build.
# We are routing the logic through the validated JSON layer to ensure deterministic math 
# and avoid bank IP-blocks during the review process.

def get_combined_text_from_urls(urls):
    """
    Iterates through a list of URLs (HTML or PDF), extracts text from each,
    and combines them into a single Master Context String.
    """
    print(f"      -> [AGGREGATOR] Received {len(urls)} sources for this card.")
    combined_text = ""
    
    for i, url in enumerate(urls):
        print(f"      -> [FETCHING] Source {i+1}: {url}")
        try:
            # BRANCH A: If it's a PDF Document
            if url.lower().endswith('.pdf'):
                print("      -> Document Type: PDF. Extracting via PyPDF2...")
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=20)
                response.raise_for_status()
                
                pdf_file = BytesIO(response.content)
                reader = PyPDF2.PdfReader(pdf_file)
                
                # --- Smart Keyword Filtering ---
                # Look for pages that actually contain financial or perk data
                keywords = [# 1. Network & Categories
                    "visa", "mastercard", "rupay", "diners club", "american express", 
                    "cashback", "fuel", "dining", "travel",
                    
                    # 2. Fees & Waivers (Using phrases to avoid generic 'fee' on every page)
                    "joining fee", "renewal fee", "annual fee", "membership fee", 
                    "waiver", "waive", "spend threshold",
                    
                    # 3. Rewards & Math (Focusing on the mechanism)
                    "reward rate", "multiplier", "reward point", "air mile", "reward coin",
                    "unified value", "expiry", "redemption", "per point",
                    
                    # 4. Perks (Domestic & International)
                    "domestic lounge", "international lounge", "airport access", 
                    "movie", "bookmyshow", "pvr", "golf", "complimentary",
                    
                    # 5. Benefits & Tie-ups
                    "welcome benefit", "milestone", "taj", "hilton", "marriott", 
                    "amazon", "flipkart", "zomato", "swiggy"
                ]
                
                pages_kept = 0
                for page_num in range(len(reader.pages)): # READ ALL PAGES
                    extracted = reader.pages[page_num].extract_text()
                    if extracted:
                        text_lower=extracted.lower()
                        # Only keep the page if it has relevant keywords
                        if any(k in text_lower for k in keywords):
                            combined_text += extracted + "\n"
                            pages_kept += 1
                            
                print(f"      -> [SMART FILTER] Scanned {len(reader.pages)} pages. Kept {pages_kept} relevant pages. Data safe!")
                        
            # BRANCH B: If it's a Webpage (Landing Page)
            else:
                print("      -> Document Type: Webpage. Converting to Markdown via Jina API...")
                # Jina API: Just prepend https://r.jina.ai/
                jina_url = f"https://r.jina.ai/{url}"
                response = requests.get(jina_url, timeout=60)
                response.raise_for_status()
                
                # Add the clean markdown text to the master string
                combined_text += response.text + "\n"
                
        except Exception as e:
            print(f"      -> [ERROR] Failed to extract from {url}: {e}")
            
        # Add a clear separator between different sources for the AI
        combined_text += "\n\n" + "="*50 + "\n\n"
        
    return combined_text