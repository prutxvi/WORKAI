import asyncio
import os
from browser_controller import WorkAIBrowser
from research_agent import WorkAIResearcher
from dotenv import load_dotenv

load_dotenv()

class WorkAI:
    def __init__(self):
        self.browser = WorkAIBrowser()
        self.researcher = WorkAIResearcher()
        
    async def research_query(self, user_query: str) -> str:
        """Main research pipeline"""
        print(f"🔍 WORKAI Research Starting...")
        print(f"📝 Query: {user_query}")
        print("=" * 50)
        
        try:
            # Step 1: Start browser
            print("1️⃣ Starting browser...")
            browser_started = await self.browser.start_browser()
            if not browser_started:
                return "❌ Failed to start browser. Please try again."
            
            # Step 2: Break down the query
            print("2️⃣ Breaking down query...")
            search_terms = self.researcher.break_down_query(user_query)
            
            # Step 3: Research each search term
            print("3️⃣ Conducting research...")
            research_results = []
            
            for i, search_term in enumerate(search_terms, 1):
                print(f"   🔎 Researching: {search_term}")
                
                # USE DUCKDUCKGO SEARCH INSTEAD OF GOOGLE
                search_results = await self.browser.duckduckgo_search(search_term)
                
                if not search_results:
                    research_results.append({
                        "search_term": search_term,
                        "answer": "No search results found"
                    })
                    continue
                
                # Try to extract answer from top results
                answer_found = False
                for result in search_results[:3]:  # Check top 3 results
                    try:
                        content = await self.browser.extract_page_content(result['url'])
                        if content:
                            answer = self.researcher.extract_answer_from_content(content, search_term)
                            if "No clear answer found" not in answer:
                                research_results.append({
                                    "search_term": search_term,
                                    "answer": answer,
                                    "source": result['url']
                                })
                                answer_found = True
                                break
                    except Exception as e:
                        print(f"   ⚠️ Skipping {result['url']}: {e}")
                        continue
                
                if not answer_found:
                    research_results.append({
                        "search_term": search_term,
                        "answer": "Could not find reliable answer"
                    })
            
            # Step 4: Generate final answer
            print("4️⃣ Generating final answer...")
            final_answer = self.researcher.synthesize_final_answer(user_query, research_results)
            
            return final_answer
            
        except Exception as e:
            print(f"❌ Research failed: {e}")
            return f"Sorry, research failed due to: {str(e)}"
        
        finally:
            # Always close browser
            await self.browser.close_browser()
    
    async def interactive_mode(self):
        """Interactive chat mode"""
        print("🤖 WORKAI - Your AI Research Assistant")
        print("Type your questions and I'll research them for you!")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\n" + "="*50)
                answer = await self.research_query(user_input)
                print("="*50)
                print(f"🤖 WORKAI: {answer}")
                print("\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main application entry point"""
    workai = WorkAI()
    
    # Check if running in interactive mode or with command line argument
    import sys
    if len(sys.argv) > 1:
        # Command line mode
        query = " ".join(sys.argv[1:])
        answer = await workai.research_query(query)
        print(f"\n🤖 WORKAI Answer: {answer}")
    else:
        # Interactive mode
        await workai.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())
