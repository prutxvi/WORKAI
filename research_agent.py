import google.generativeai as genai
import os
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class WorkAIResearcher:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def break_down_query(self, user_query: str) -> List[str]:
        """Break complex queries into simple search terms"""
        prompt = f"""
        Break down this user query into 2-3 simple Google search terms:
        
        User Query: "{user_query}"
        
        Return only the search terms, one per line, without numbers or extra text.
        Make them specific and searchable.
        
        Example:
        User Query: "Who founded Instagram and Facebook"
        Output:
        Instagram founder
        Facebook founder
        """
        
        try:
            response = self.model.generate_content(prompt)
            search_terms = [term.strip() for term in response.text.strip().split('\n') if term.strip()]
            print(f"✅ Generated search terms: {search_terms}")
            return search_terms
        except Exception as e:
            print(f"❌ Failed to break down query: {e}")
            return [user_query]  # Fallback to original query
    
    def extract_answer_from_content(self, content: str, search_term: str) -> str:
        """Extract specific answer from webpage content"""
        prompt = f"""
        From this webpage content, extract the specific answer for: "{search_term}"
        
        Content: {content[:3000]}
        
        Rules:
        - Give only the direct answer
        - Be specific (names, dates, facts)
        - If no clear answer, say "No clear answer found"
        - Keep it under 100 words
        
        Answer:
        """
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            print(f"✅ Extracted answer for '{search_term}': {answer[:100]}...")
            return answer
        except Exception as e:
            print(f"❌ Failed to extract answer: {e}")
            return "Could not extract answer"
    
    def synthesize_final_answer(self, user_query: str, research_results: List[Dict]) -> str:
        """Combine all research into final comprehensive answer"""
        results_text = ""
        for i, result in enumerate(research_results, 1):
            results_text += f"\nSearch {i}: {result['search_term']}\n"
            results_text += f"Answer: {result['answer']}\n"
        
        prompt = f"""
        User asked: "{user_query}"
        
        Here's what I found through research:
        {results_text}
        
        Provide a clear, comprehensive final answer that directly answers the user's question.
        
        Rules:
        - Be direct and factual
        - Combine information logically
        - Use proper names and specific details
        - Keep it concise but complete
        - Start with "Based on my research:"
        
        Final Answer:
        """
        
        try:
            response = self.model.generate_content(prompt)
            final_answer = response.text.strip()
            print("✅ Generated final answer")
            return final_answer
        except Exception as e:
            print(f"❌ Failed to synthesize answer: {e}")
            return "Sorry, I couldn't generate a complete answer from the research."

# Test the research agent
def test_researcher():
    researcher = WorkAIResearcher()
    
    # Test query breakdown
    query = "Who founded Instagram and Facebook and when"
    search_terms = researcher.break_down_query(query)
    print(f"Search terms: {search_terms}")
    
    # Test answer synthesis
    mock_results = [
        {"search_term": "Instagram founder", "answer": "Kevin Systrom and Mike Krieger founded Instagram in 2010"},
        {"search_term": "Facebook founder", "answer": "Mark Zuckerberg founded Facebook in 2004"}
    ]
    
    final_answer = researcher.synthesize_final_answer(query, mock_results)
    print(f"\nFinal Answer: {final_answer}")

if __name__ == "__main__":
    test_researcher()
