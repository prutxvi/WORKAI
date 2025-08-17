import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class WorkAIResearcher:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Free Llama model on Groq

    def break_down_query(self, user_query: str) -> Dict[str, List[str]]:
        """Break query into multiple research layers for deep search"""
        prompt = f'''
Analyze this user query and create a comprehensive research plan:
User Query: "{user_query}"

Create different types of search terms:
1. PRIMARY: 3-4 main search terms for direct answers
2. SECONDARY: 2-3 related/context terms for deeper understanding  
3. VERIFICATION: 2-3 terms to cross-check facts and find contradictions
4. RECENT: 1-2 terms for latest information (add "2024" or "latest")

Format exactly as:
PRIMARY: term1, term2, term3
SECONDARY: term1, term2  
VERIFICATION: term1, term2
RECENT: term1 2024, term2 latest
'''
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.3,
                max_tokens=300
            )
            
            lines = response.choices[0].message.content.strip().split('\n')
            
            search_plan = {
                'primary': [],
                'secondary': [],
                'verification': [],
                'recent': []
            }
            
            for line in lines:
                if line.startswith('PRIMARY:'):
                    search_plan['primary'] = [term.strip() for term in line.replace('PRIMARY:', '').split(',')]
                elif line.startswith('SECONDARY:'):
                    search_plan['secondary'] = [term.strip() for term in line.replace('SECONDARY:', '').split(',')]
                elif line.startswith('VERIFICATION:'):
                    search_plan['verification'] = [term.strip() for term in line.replace('VERIFICATION:', '').split(',')]
                elif line.startswith('RECENT:'):
                    search_plan['recent'] = [term.strip() for term in line.replace('RECENT:', '').split(',')]
            
            print(f"✅ Generated deep search plan:")
            print(f"   📍 Primary: {search_plan['primary']}")
            print(f"   🔍 Secondary: {search_plan['secondary']}")
            print(f"   ✓ Verification: {search_plan['verification']}")
            print(f"   🕐 Recent: {search_plan['recent']}")
            return search_plan
        except Exception as e:
            print(f"❌ Failed to break down query: {e}")
            return {'primary': [user_query], 'secondary': [], 'verification': [], 'recent': []}

    def extract_answer_from_content(self, content: str, search_term: str, search_type: str) -> str:
        """Enhanced extraction based on search type"""
        if search_type == 'verification':
            prompt = f'''
Analyze this content to verify or contradict information about: "{search_term}"
Content: {content[:3000]}

Look for:
- Facts that support or contradict the topic
- Different perspectives or conflicting information
- Evidence quality (statistics, studies, expert opinions)

Response format:
SUPPORTS: [what supports the topic]
CONTRADICTS: [what contradicts it]
NEUTRAL: [neutral/unclear information]
'''
        else:
            prompt = f'''
From this content, extract comprehensive information about: "{search_term}"
Content: {content[:3000]}

Rules:
- Extract specific facts, numbers, dates, names
- Include key details and context
- If no clear answer, say "No clear answer found"
- Keep under 150 words
- Focus on factual accuracy

Answer:
'''
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0,
                max_tokens=200
            )
            answer = response.choices[0].message.content.strip()
            print(f"✅ Extracted {search_type} answer for '{search_term}': {answer[:100]}...")
            return answer
        except Exception as e:
            print(f"❌ Failed to extract {search_type} answer: {e}")
            return "Could not extract answer"

    def analyze_contradictions(self, verification_results: List[Dict]) -> str:
        """Analyze verification results for contradictions"""
        if not verification_results:
            return "No verification data available"
            
        prompt = f'''
Analyze these verification results for contradictions or conflicting information:

{verification_results}

Provide:
1. CONSENSUS: What most sources agree on
2. CONTRADICTIONS: What sources disagree about  
3. RELIABILITY: Overall reliability assessment
4. GAPS: What information is missing

Keep it concise and factual.
'''
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.2,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Failed to analyze contradictions: {e}")
            return "Could not analyze verification data"

    def calculate_research_confidence(self, all_results: Dict) -> str:
        """Enhanced confidence calculation for deep search"""
        total_searches = sum(len(results) for results in all_results.values())
        if total_searches == 0:
            return "Research Confidence: 0%"
            
        successful_extractions = 0
        verification_quality = 0
        
        for search_type, results in all_results.items():
            for result in results:
                if "No clear answer found" not in result['answer'] and "Could not extract answer" not in result['answer']:
                    successful_extractions += 1
                    
                # Bonus for verification data
                if search_type == 'verification' and len(result['answer']) > 50:
                    verification_quality += 1
        
        base_confidence = (successful_extractions / total_searches) * 100
        verification_bonus = (verification_quality / max(1, len(all_results.get('verification', [])))) * 15
        final_confidence = min(100, base_confidence + verification_bonus)
        
        return f"Research Confidence: {final_confidence:.0f}% (Deep Search)"

    def synthesize_comprehensive_answer(self, user_query: str, all_results: Dict, contradiction_analysis: str) -> str:
        """Synthesize all research layers into comprehensive answer"""
        
        findings_by_type = {}
        all_sources = set()
        
        for search_type, results in all_results.items():
            findings_by_type[search_type] = []
            for result in results:
                findings_by_type[search_type].append(f"- {result['search_term']}: {result['answer']}")
                if result.get('source'):
                    all_sources.add(result['source'])
        
        sources_list = "\n".join([f"  {src}" for src in all_sources]) if all_sources else "  [No sources recorded]"
        confidence_score = self.calculate_research_confidence(all_results)
        
        prompt = f'''
You are WORKAI conducting DEEP RESEARCH. Synthesize this comprehensive analysis:

Query: "{user_query}"

PRIMARY FINDINGS:
{chr(10).join(findings_by_type.get('primary', []))}

SECONDARY CONTEXT:
{chr(10).join(findings_by_type.get('secondary', []))}

RECENT DEVELOPMENTS:
{chr(10).join(findings_by_type.get('recent', []))}

VERIFICATION ANALYSIS:
{contradiction_analysis}

Instructions:
1. Start with "🔍 WORKAI DEEP RESEARCH COMPLETE"
2. Executive Summary (3-4 lines)
3. Comprehensive Findings (detailed analysis)
4. Recent Developments (if any)
5. Verification & Cross-Check Results
6. Research Limitations (if any)

Make this MORE thorough and accurate than ChatGPT, Claude, or any standard AI tool.
Show the depth of research conducted.
'''
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.3,
                max_tokens=800
            )
            final_answer = response.choices[0].message.content.strip()
            print("✅ Generated comprehensive deep research answer")
            
            return (
                "╔══════════════════════════════════════════════════════╗\n"
                "║         🤖 WORKAI DEEP RESEARCH COMPLETE            ║\n"
                "╚══════════════════════════════════════════════════════╝\n"
                f"{final_answer}\n\n"
                f"📊 {confidence_score}\n"
                f"🔍 Sources Analyzed: {len(all_sources)}\n"
                f"📋 Search Layers: {len([k for k, v in all_results.items() if v])}\n"
                "─────────────────────────────────────────────────────\n"
                "SOURCES CONSULTED:\n"
                f"{sources_list}\n"
            )
        except Exception as e:
            print(f"❌ Failed to synthesize comprehensive answer: {e}")
            return (
                "╔══════════════════════════════════════════════════════╗\n"
                "║   ❌ Unable to generate deep research answer        ║\n"
                "╚══════════════════════════════════════════════════════╝\n"
            )
