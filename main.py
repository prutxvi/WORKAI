import asyncio
import os
from typing import List, Dict
from browser_controller import WorkAIBrowser
from research_agent import WorkAIResearcher
from dotenv import load_dotenv

load_dotenv()

class WorkAI:
    def __init__(self):
        self.browser = WorkAIBrowser()
        self.researcher = WorkAIResearcher()

    async def conduct_deep_research(self, search_terms: List[str], search_type: str) -> List[Dict]:
        """Conduct research for a specific search type"""
        results = []
        
        for search_term in search_terms:
            print(f"   🔎 [{search_type.upper()}] Researching: {search_term}")
            
            search_results = await self.browser.duckduckgo_search(search_term)
            if not search_results:
                results.append({
                    "search_term": search_term,
                    "answer": "No search results found",
                    "search_type": search_type
                })
                continue
            
            # Try multiple sources for better coverage
            answer_found = False
            for i, result in enumerate(search_results[:4]):  # Check top 4 results
                try:
                    content = await self.browser.extract_page_content(result['url'])
                    if content:
                        answer = self.researcher.extract_answer_from_content(content, search_term, search_type)
                        if "No clear answer found" not in answer:
                            results.append({
                                "search_term": search_term,
                                "answer": answer,
                                "source": result['url'],
                                "search_type": search_type
                            })
                            answer_found = True
                            break
                except Exception as e:
                    print(f"   ⚠️ Skipping {result['url']}: {e}")
                    continue
            
            if not answer_found:
                results.append({
                    "search_term": search_term,
                    "answer": "Could not find reliable answer",
                    "search_type": search_type
                })
        
        return results

    async def research_query(self, user_query: str) -> str:
        print(f"🔍 WORKAI Deep Research Starting...")
        print(f"📝 Query: {user_query}")
        print("=" * 60)
        
        try:
            print("1️⃣ Starting browser...")
            browser_started = await self.browser.start_browser()
            if not browser_started:
                return "❌ Failed to start browser. Please try again."
            
            print("2️⃣ Creating deep research plan...")
            search_plan = self.researcher.break_down_query(user_query)
            
            print("3️⃣ Conducting multi-layer research...")
            all_results = {}
            
            # Research each layer
            for search_type, terms in search_plan.items():
                if terms:
                    print(f"\n🔍 Layer: {search_type.upper()}")
                    results = await self.conduct_deep_research(terms, search_type)
                    all_results[search_type] = results
            
            print("\n4️⃣ Analyzing contradictions and verifying facts...")
            verification_results = all_results.get('verification', [])
            contradiction_analysis = self.researcher.analyze_contradictions(verification_results)
            
            print("5️⃣ Synthesizing comprehensive answer...")
            final_answer = self.researcher.synthesize_comprehensive_answer(
                user_query, all_results, contradiction_analysis
            )
            
            return final_answer
            
        except Exception as e:
            print(f"❌ Deep research failed: {e}")
            return f"Sorry, deep research failed due to: {str(e)}"
        
        finally:
            await self.browser.close_browser()

    async def interactive_mode(self):
        print("🤖 WORKAI - Advanced AI Research Assistant")
        print("Conducting deeper research than standard AI tools...")
        print("Type your questions and I'll perform comprehensive analysis!")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\n" + "="*60)
                answer = await self.research_query(user_input)
                print("="*60)
                print(f"{answer}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    workai = WorkAI()
    
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        answer = await workai.research_query(query)
        print(f"\n🤖 WORKAI Deep Research:\n{answer}")
    else:
        await workai.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())
