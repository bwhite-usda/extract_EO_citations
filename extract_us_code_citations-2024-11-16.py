import requests
import PyPDF2
import re
import os
import time
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(
    filename="script.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def download_pdf(url, filename, delay=5, max_retries=3):
    """Downloads a PDF file from the given URL and saves it locally."""
    headers = {'User-Agent': 'My Custom User Agent'}
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, stream=True, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if not chunk:
                            break
                        f.write(chunk)
                logging.info(f"Successfully downloaded: {url}")
                return True
            else:
                logging.error(f"Failed to download {url}: Status code {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {url} (attempt {attempt}): {e}")
            time.sleep(delay)
    return False

def extract_us_code_citations(pdf_path):
    """Extracts U.S. Code citations and surrounding context from the given PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)

            citations = []
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()

                # Regex to match U.S. Code citations
                citation_pattern = r"(\d+)\s*(U\.S\.C\.|USC|Code of Federal Regulations|CFR)\s*§?\s*(\d+(?:\.\d+)*)"
                matches = re.finditer(citation_pattern, text)

                for match in matches:
                    citation = match.group(0)
                    start, end = match.start(), match.end()
                    context = text[max(0, start-50):min(len(text), end+50)]  # Extract 50 chars before and after
                    citations.append((citation, context.strip()))

        logging.info(f"Extracted {len(citations)} citations from {pdf_path}")
        return citations

    except (FileNotFoundError, PyPDF2.errors.PdfReadError) as e:
        logging.error(f"Error reading PDF {pdf_path}: {e}")
        return []

def infer_title(filename):
    """Infers a human-readable title from a filename."""
    name_parts = filename.split('.')[:-1]
    title = ' '.join(name_parts).replace('_', ' ').title()
    return title

def save_to_excel(output_path, data):
    """Saves the extracted data to an Excel file."""
    df = pd.DataFrame(data, columns=["Filename", "Citation", "Context"])
    df.to_excel(output_path, index=False, engine='openpyxl')
    logging.info(f"Saved data to {output_path}")

def process_pdf(url):
    """Downloads a PDF, extracts citations, and returns results."""
    filename = url.split("/")[-1]
    if download_pdf(url, filename):
        citations = extract_us_code_citations(filename)
        title = infer_title(filename)
        # Cleanup downloaded PDF after processing
        os.remove(filename)
        return [(title, citation, context) for citation, context in citations]
    return []

def main():
    pdf_urls = [
    'https://rd.usda.gov/sites/default/files/00701.pdf',
    'https://rd.usda.gov/sites/default/files/04041.pdf',
    'https://rd.usda.gov/sites/default/files/04261.pdf',
    'https://rd.usda.gov/sites/default/files/04262.pdf',
    'https://rd.usda.gov/sites/default/files/04401_11.pdf',
    'https://rd.usda.gov/sites/default/files/04448.pdf',
    'https://rd.usda.gov/sites/default/files/04505.pdf',
    'https://rd.usda.gov/sites/default/files/1900a.pdf',
    'https://rd.usda.gov/sites/default/files/1900b.pdf',
    'https://rd.usda.gov/sites/default/files/1900c.pdf',
    'https://rd.usda.gov/sites/default/files/1900d.pdf',
    'https://rd.usda.gov/sites/default/files/1901a.pdf',
    'https://rd.usda.gov/sites/default/files/1901e.pdf',
    'https://rd.usda.gov/sites/default/files/1901f.pdf',
    'https://rd.usda.gov/sites/default/files/1901k.pdf',
    'https://rd.usda.gov/sites/default/files/1901p.pdf',
    'https://rd.usda.gov/sites/default/files/1902a.pdf',
    'https://rd.usda.gov/sites/default/files/1904b.pdf',
    'https://rd.usda.gov/sites/default/files/1904c.pdf',
    'https://rd.usda.gov/sites/default/files/1904d.pdf',
    'https://rd.usda.gov/sites/default/files/1910b.pdf',
    'https://rd.usda.gov/sites/default/files/1910c.pdf',
    'https://rd.usda.gov/sites/default/files/1922a.pdf',
    'https://rd.usda.gov/sites/default/files/1922b.pdf',
    'https://rd.usda.gov/sites/default/files/1924a.pdf',
    'https://rd.usda.gov/sites/default/files/1924c.pdf',
    'https://rd.usda.gov/sites/default/files/1924f.pdf',
    'https://rd.usda.gov/sites/default/files/1925a.pdf',
    'https://rd.usda.gov/sites/default/files/1927b.pdf',
    'https://rd.usda.gov/sites/default/files/1940c.pdf',
    'https://rd.usda.gov/sites/default/files/1940e.pdf',
    'https://rd.usda.gov/sites/default/files/1940j.pdf',
    'https://rd.usda.gov/sites/default/files/1940l.pdf',
    'https://rd.usda.gov/sites/default/files/1940m.pdf',
    'https://rd.usda.gov/sites/default/files/1940q.pdf',
    'https://rd.usda.gov/sites/default/files/1940t.pdf',
    'https://rd.usda.gov/sites/default/files/1942a.pdf',
    'https://rd.usda.gov/sites/default/files/1942c.pdf',
    'https://rd.usda.gov/sites/default/files/1944b.pdf',
    'https://rd.usda.gov/sites/default/files/1944i_0.pdf',
    'https://rd.usda.gov/sites/default/files/1944k.pdf',
    'https://rd.usda.gov/sites/default/files/1944n.pdf',
    'https://rd.usda.gov/sites/default/files/1948b.pdf',
    'https://rd.usda.gov/sites/default/files/1950c.pdf',
    'https://rd.usda.gov/sites/default/files/1951a.pdf',
    'https://rd.usda.gov/sites/default/files/1951b.pdf',
    'https://rd.usda.gov/sites/default/files/1951c.pdf',
    'https://rd.usda.gov/sites/default/files/1951d.pdf',
    'https://rd.usda.gov/sites/default/files/1951e.pdf',
    'https://rd.usda.gov/sites/default/files/1951f.pdf',
    'https://rd.usda.gov/sites/default/files/1951o_0.pdf',
    'https://rd.usda.gov/sites/default/files/1951r.pdf',
    'https://rd.usda.gov/sites/default/files/1955a.pdf',
    'https://rd.usda.gov/sites/default/files/1955b.pdf',
    'https://rd.usda.gov/sites/default/files/1955c.pdf',
    'https://rd.usda.gov/sites/default/files/1956b.pdf',
    'https://rd.usda.gov/sites/default/files/1956c.pdf',
    'https://rd.usda.gov/sites/default/files/1962a.pdf',
    'https://rd.usda.gov/sites/default/files/1980e.pdf',
    'https://rd.usda.gov/sites/default/files/1980k.pdf',
    'https://rd.usda.gov/sites/default/files/1992e.pdf',
    'https://rd.usda.gov/sites/default/files/2003a.pdf',
    'https://rd.usda.gov/sites/default/files/2006a.pdf',
    'https://rd.usda.gov/sites/default/files/2006b.pdf',
    'https://rd.usda.gov/sites/default/files/2006d.pdf',
    'https://rd.usda.gov/sites/default/files/2006ee.pdf',
    'https://rd.usda.gov/sites/default/files/2006f.pdf',
    'https://rd.usda.gov/sites/default/files/2006ff.pdf',
    'https://rd.usda.gov/sites/default/files/2006g.pdf',
    'https://rd.usda.gov/sites/default/files/2006h.pdf',
    'https://rd.usda.gov/sites/default/files/2006i.pdf',
    'https://rd.usda.gov/sites/default/files/2006k.pdf',
    'https://rd.usda.gov/sites/default/files/2006kk.pdf',
    'https://rd.usda.gov/sites/default/files/2006m.pdf',
    'https://rd.usda.gov/sites/default/files/2006nn.pdf',
    'https://rd.usda.gov/sites/default/files/2006oo.pdf',
    'https://rd.usda.gov/sites/default/files/2006pp.pdf',
    'https://rd.usda.gov/sites/default/files/2006qq.pdf',
    'https://rd.usda.gov/sites/default/files/2006t.pdf',
    'https://rd.usda.gov/sites/default/files/2006tt.pdf',
    'https://rd.usda.gov/sites/default/files/2006u.pdf',
    'https://rd.usda.gov/sites/default/files/2006v.pdf',
    'https://rd.usda.gov/sites/default/files/2006w.pdf',
    'https://rd.usda.gov/sites/default/files/2006x.pdf',
    'https://rd.usda.gov/sites/default/files/2006y.pdf',
    'https://rd.usda.gov/sites/default/files/2006z.pdf',
    'https://rd.usda.gov/sites/default/files/2009a.pdf',
    'https://rd.usda.gov/sites/default/files/2009b.pdf',
    'https://rd.usda.gov/sites/default/files/2009c.pdf',
    'https://rd.usda.gov/sites/default/files/2009d.pdf',
    'https://rd.usda.gov/sites/default/files/2012a.pdf',
    'https://rd.usda.gov/sites/default/files/2012b.pdf',
    'https://rd.usda.gov/sites/default/files/2012c.pdf',
    'https://rd.usda.gov/sites/default/files/2015b.pdf',
    'https://rd.usda.gov/sites/default/files/2015c.pdf',
    'https://rd.usda.gov/sites/default/files/2015d.pdf',
    'https://rd.usda.gov/sites/default/files/2015e.pdf',
    'https://rd.usda.gov/sites/default/files/2015g.pdf',
    'https://rd.usda.gov/sites/default/files/2018d.pdf',
    'https://rd.usda.gov/sites/default/files/2018e.pdf',
    'https://rd.usda.gov/sites/default/files/2018f.pdf',
    'https://rd.usda.gov/sites/default/files/2018g.pdf',
    'https://rd.usda.gov/sites/default/files/2018h.pdf',
    'https://rd.usda.gov/sites/default/files/2021a.pdf',
    'https://rd.usda.gov/sites/default/files/2021c.pdf',
    'https://rd.usda.gov/sites/default/files/2024a.pdf',
    'https://rd.usda.gov/sites/default/files/2024b.pdf',
    'https://rd.usda.gov/sites/default/files/2024c.pdf',
    'https://rd.usda.gov/sites/default/files/2024f.pdf',
    'https://rd.usda.gov/sites/default/files/2024g.pdf',
    'https://rd.usda.gov/sites/default/files/2024h.pdf',
    'https://rd.usda.gov/sites/default/files/2024o.pdf',
    'https://rd.usda.gov/sites/default/files/2024q.pdf',
    'https://rd.usda.gov/sites/default/files/2030a.pdf',
    'https://rd.usda.gov/sites/default/files/2030b.pdf',
    'https://rd.usda.gov/sites/default/files/2030c.pdf',
    'https://rd.usda.gov/sites/default/files/2030d.pdf',
    'https://rd.usda.gov/sites/default/files/2033a.pdf',
    'https://rd.usda.gov/sites/default/files/2033f.pdf',
    'https://rd.usda.gov/sites/default/files/2036a.pdf',
    'https://rd.usda.gov/sites/default/files/2039a.pdf',
    'https://rd.usda.gov/sites/default/files/2042a.pdf',
    'https://rd.usda.gov/sites/default/files/2042b.pdf',
    'https://rd.usda.gov/sites/default/files/2045e.pdf',
    'https://rd.usda.gov/sites/default/files/2045ee.pdf',
    'https://rd.usda.gov/sites/default/files/2045f.pdf',
    'https://rd.usda.gov/sites/default/files/2045gg.pdf',
    'https://rd.usda.gov/sites/default/files/2045jj.pdf',
    'https://rd.usda.gov/sites/default/files/2045kk.pdf',
    'https://rd.usda.gov/sites/default/files/2045ll.pdf',
    'https://rd.usda.gov/sites/default/files/2045m.pdf',
    'https://rd.usda.gov/sites/default/files/2045o.pdf',
    'https://rd.usda.gov/sites/default/files/2045y.pdf',
    'https://rd.usda.gov/sites/default/files/2048a.pdf',
    'https://rd.usda.gov/sites/default/files/2048b.pdf',
    'https://rd.usda.gov/sites/default/files/2051a.pdf',
    'https://rd.usda.gov/sites/default/files/2051b.pdf',
    'https://rd.usda.gov/sites/default/files/2051c.pdf',
    'https://rd.usda.gov/sites/default/files/2051f.pdf',
    'https://rd.usda.gov/sites/default/files/2051h.pdf',
    'https://rd.usda.gov/sites/default/files/2051i.pdf',
    'https://rd.usda.gov/sites/default/files/2051j.pdf',
    'https://rd.usda.gov/sites/default/files/2054a.pdf',
    'https://rd.usda.gov/sites/default/files/2054l.pdf',
    'https://rd.usda.gov/sites/default/files/2054m.pdf',
    'https://rd.usda.gov/sites/default/files/2054u.pdf',
    'https://rd.usda.gov/sites/default/files/2054v.pdf',
    'https://rd.usda.gov/sites/default/files/2057a.pdf',
    'https://rd.usda.gov/sites/default/files/2063a.pdf',
    'https://rd.usda.gov/sites/default/files/2063d.pdf',
    'https://rd.usda.gov/sites/default/files/2063f.pdf',
    'https://rd.usda.gov/sites/default/files/2063g.pdf',
    'https://rd.usda.gov/sites/default/files/2063i.pdf',
    'https://rd.usda.gov/sites/default/files/2066a.pdf',
    'https://rd.usda.gov/sites/default/files/2006ss.pdf',
    'https://rd.usda.gov/sites/default/files/2069a.pdf',
    'https://rd.usda.gov/sites/default/files/2069b.pdf',
    'https://rd.usda.gov/sites/default/files/3570b.pdf',
    'https://rd.usda.gov/sites/default/files/3570f.pdf',
    'https://rd.usda.gov/sites/default/files/3575a.pdf',
    'https://rd.usda.gov/sites/default/files/4274d.pdf',
    'https://rd.usda.gov/sites/default/files/4279a.pdf',
    'https://rd.usda.gov/sites/default/files/4279-b.pdf',
    'https://rd.usda.gov/sites/default/files/4279c.pdf',
    'https://rd.usda.gov/sites/default/files/4280a.pdf',
    'https://rd.usda.gov/sites/default/files/4280b.pdf',
    'https://rd.usda.gov/sites/default/files/4280d.pdf',
    'https://rd.usda.gov/sites/default/files/4284a.pdf',
    'https://rd.usda.gov/sites/default/files/4284f.pdf',
    'https://rd.usda.gov/sites/default/files/4284j.pdf',
    'https://rd.usda.gov/sites/default/files/4284k.pdf',
    'https://rd.usda.gov/sites/default/files/4284l.pdf',
    'https://rd.usda.gov/sites/default/files/4287b.pdf',
    'https://rd.usda.gov/sites/default/files/4287d.pdf',
    'https://rd.usda.gov/sites/default/files/4288a.pdf',
    'https://rd.usda.gov/sites/default/files/4288b.pdf',
    'https://rd.usda.gov/sites/default/files/4290a.pdf',
    'https://rd.usda.gov/sites/default/files/5001.pdf',
    'https://rd.usda.gov/sites/default/files/1992e.pdf',
    'https://rd.usda.gov/sites/default/files/RD-Inst-4280E-RBDG-Update-Final.pdf',
]
    
    output_file = "us_code_citations.xlsx"
    all_data = []

    # Process PDFs in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_pdf, pdf_urls)
        for result in results:
            all_data.extend(result)

    # Save results to Excel
    save_to_excel(output_file, all_data)
    logging.info("Processing complete.")

if __name__ == "__main__":
    main()


