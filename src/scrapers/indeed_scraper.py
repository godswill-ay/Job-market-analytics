import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent

class IndeedScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = "https://uk.indeed.com/jobs"
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
    
    def search_jobs(self, keyword="software engineer", location="London", max_pages=5):
        jobs = []
        
        for page in range(max_pages):
            print(f"Scraping page {page + 1}...")
            
            params = {
                'q': keyword,
                'l': location,
                'start': page * 10
            }
            
            response = requests.get(self.base_url, params=params, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', {'data-jk': True})
            
            for card in job_cards:
                job = self.extract_job_info(card)
                if job:
                    jobs.append(job)
            
            # Be respectful - don't hammer the server
            time.sleep(random.uniform(2, 4))
        
        return jobs
    
    def extract_job_info(self, card):
        try:
            # Extract job title
            title_elem = card.find('h2', class_='jobTitle')
            title = title_elem.find('span').text.strip() if title_elem else "N/A"
            
            # Extract company
            company_elem = card.find('span', {'data-testid': 'company-name'})
            company = company_elem.text.strip() if company_elem else "N/A"
            
            # Extract location
            location_elem = card.find('div', {'data-testid': 'job-location'})
            location = location_elem.text.strip() if location_elem else "N/A"
            
            # Extract salary (if available)
            salary_elem = card.find('span', class_='salaryText')
            salary = salary_elem.text.strip() if salary_elem else "N/A"
            
            # Extract job link
            link_elem = title_elem.find('a') if title_elem else None
            job_link = f"https://uk.indeed.com{link_elem['href']}" if link_elem else "N/A"
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'link': job_link,
                'scraped_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Error extracting job info: {e}")
            return None

# Test the scraper
if __name__ == "__main__":
    scraper = IndeedScraper()
    jobs = scraper.search_jobs("Python Developer", "London", max_pages=3)
    
    df = pd.DataFrame(jobs)
    df.to_csv('data/raw/indeed_jobs_sample.csv', index=False)
    print(f"Scraped {len(jobs)} jobs and saved to CSV")
    print(df.head())