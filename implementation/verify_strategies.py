import asyncio
import os
import time
import logging
import sys
import argparse
from typing import Callable, Any, List, Dict
from dotenv import load_dotenv
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("test_runner")

# Add implementation directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import strategies
try:
    from rag_agent_advanced import (
        initialize_db,
        close_db,
        search_knowledge_base,
        search_with_multi_query,
        search_with_reranking,
        search_with_self_reflection,
        search_with_hybrid_retrieval,
        retrieve_full_document,
        answer_with_fact_verification,
        answer_with_multi_hop,
        answer_with_uncertainty
    )
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you are running this from the implementation directory or have dependencies installed.")
    sys.exit(1)

# Load env vars
load_dotenv(".env")

@dataclass
class TestResult:
    name: str
    status: str  # PASS, FAIL, SKIP
    duration_ms: float
    output: str = ""
    error: str = ""

class StrategyTester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.db_initialized = False

    async def setup(self):
        print("🔌 Checking environment...")
        if not os.getenv("DATABASE_URL"):
            raise ValueError("DATABASE_URL is missing in .env")
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is missing in .env")
        
        print("🔌 Initializing database connection...")
        try:
            await initialize_db()
            self.db_initialized = True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

    async def teardown(self):
        if self.db_initialized:
            await close_db()

    async def run_test(self, name: str, func: Callable, *args, **kwargs) -> TestResult:
        print(f"🔄 Running test: {name}...", end="", flush=True)
        start_time = time.time()
        try:
            # Most functions in rag_agent_advanced take (ctx, query, limit)
            # We pass None for ctx
            result = await func(None, *args, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            # success criteria: result is a string and does not start with "Error" or "Search error"
            status = "PASS"
            if isinstance(result, str):
                if result.startswith("Error") or result.startswith("Search error") or "encountered an error" in result:
                    status = "FAIL"
            else:
                status = "FAIL"
                result = f"Unexpected return type: {type(result)}"

            print(f" {status} ({duration:.2f}ms)")
            return TestResult(name, status, duration, str(result)[:200] + "...")
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            print(f" FAIL ({duration:.2f}ms)")
            return TestResult(name, "FAIL", duration, error=str(e))

    async def run_all(self, test_query: str = "strategic overview"):
        await self.setup()
        
        print(f"\n🧪 Starting Tests with Query: '{test_query}'\n" + "="*50)

        # 1. Baseline Search
        self.results.append(await self.run_test(
            "Baseline: search_knowledge_base", 
            search_knowledge_base, 
            test_query
        ))

        # 2. Multi-Query
        self.results.append(await self.run_test(
            "Strategy: search_with_multi_query", 
            search_with_multi_query, 
            test_query
        ))

        # 3. Re-ranking
        self.results.append(await self.run_test(
            "Strategy: search_with_reranking", 
            search_with_reranking, 
            test_query
        ))

        # 4. Self-Reflection
        self.results.append(await self.run_test(
            "Strategy: search_with_self_reflection", 
            search_with_self_reflection, 
            test_query
        ))
        
        # 5. Hybrid Retrieval
        self.results.append(await self.run_test(
            "Strategy: search_with_hybrid_retrieval", 
            search_with_hybrid_retrieval, 
            test_query
        ))

        # 6. Full Document Retrieval
        self.results.append(await self.run_test(
            "Edge Case: retrieve_full_document (missing)", 
            retrieve_full_document, 
            "NON_EXISTENT_DOCUMENT_X123"
        ))
        
        # 7. Fact Verification
        self.results.append(await self.run_test(
            "Strategy: answer_with_fact_verification",
            answer_with_fact_verification,
            test_query
        ))
        
        # 8. Multi-hop
        self.results.append(await self.run_test(
            "Strategy: answer_with_multi_hop",
            answer_with_multi_hop,
            test_query
        ))
        
        # 9. Uncertainty
        self.results.append(await self.run_test(
            "Strategy: answer_with_uncertainty",
            answer_with_uncertainty,
            test_query
        ))

        # 10. Input Validation: Empty Query
        self.results.append(await self.run_test(
            "Input Validation: Empty Query", 
            search_knowledge_base, 
            ""
        ))

        await self.teardown()
        self.print_report()

    def print_report(self):
        print("\n" + "="*50)
        print("📊 TEST REPORT")
        print("="*50)
        print(f"{ 'TEST NAME':<40} | { 'STATUS':<6} | { 'TIME (ms)':<10} | {'OUTPUT/ERROR'}")
        print("-" * 80)
        
        passed = 0
        failed = 0
        
        for r in self.results:
            status_icon = "✅" if r.status == "PASS" else "❌"
            if r.status == "PASS": passed += 1
            else: failed += 1
            
            # Clean output for display
            display_output = r.output.replace('\n', ' ') if r.output else r.error
            if len(display_output) > 30:
                display_output = display_output[:27] + "..."
                
            print(f"{r.name:<40} | {status_icon} {r.status} | {r.duration_ms:>9.2f} | {display_output}")

        print("="*50)
        print(f"Total: {len(self.results)}, Passed: {passed}, Failed: {failed}")
        if failed > 0:
            print("\n⚠️  Some tests failed. Check the logs above.")
            sys.exit(1)
        else:
            print("\n✨ All systems operational.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify RAG Strategies")
    parser.add_argument("--query", type=str, default="What are the strategic goals?", help="Test query to run")
    args = parser.parse_args()

    tester = StrategyTester()
    try:
        asyncio.run(tester.run_all(args.query))
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted.")
    except Exception as e:
        print(f"\n❌ Critical failure: {e}")
