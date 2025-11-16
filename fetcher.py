import os
import json
import time
import logging
import requests
from typing import List, Callable, Optional, Dict
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from transcript import *
from program import * 

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskState(Enum):
    """Task states for better type safety"""
    ACTIVE = "active"
    RUNNING = "running"
    QUEUED = "queued"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FetchResult:
    program_title: str
    success: bool
    program: Optional[Block] = None
    error: Optional[str] = None
    attempts: int = 1
    duration_seconds: float = 0.0


@dataclass
class FetchConfig:
    """
    Configuration for fetching behavior.
    
    Attributes:
        max_retries: Maximum number of retry attempts per program (default: 1)
        max_workers: Maximum concurrent worker threads (default: 5)
        task_timeout: Maximum time in seconds to wait for task completion (default: 300)
        poll_interval: Time in seconds between polling attempts (default: 5)
        request_timeout: HTTP request timeout in seconds (default: 30)
        step_limit: Maximum steps for agent task execution (default: 2)
        debug_mode: If True, uses get_program function instead of API calls (default: False)
        debug_get_program: Function to use in debug mode: (title: str) -> Program
    """
    max_retries: int = 1
    max_workers: int = 5
    task_timeout: int = 300
    poll_interval: int = 5
    request_timeout: int = 30
    step_limit: int = 5
    debug_mode: bool = False
    debug_get_program: Optional[Callable[[str], Block]] = None


class ProgramFetchError(Exception):
    """exception for program fetching errors"""
    pass


class ProgramFetcher:
    """
    Fetches and parses academic program information from course catalogs
    using browser cash API agent.
    """
    
    PROGRAM_CATALOG: Dict[str, str] = {
        "Computer Science Major Concentration (B.A.)": 
            "https://coursecatalogue.mcgill.ca/en/undergraduate/arts/programs/computer-science/computer-science-major-concentration-ba/",
        "Economics Major Concentration (B.A.)":"https://coursecatalogue.mcgill.ca/en/undergraduate/arts/programs/economics/economics-major-concentration-ba/"
    }
    
    def __init__(self, config: Optional[FetchConfig] = None):
        """
        Initialize the fetcher.
        
        Args:
            config: Fetch configuration (defaults to FetchConfig())
        
        Raises:
            ValueError: If API credentials are missing (in non-debug mode) or
                       if debug_get_program is not provided in debug mode
        """
        self.config = config or FetchConfig()
        
        # Debug mode validation
        if self.config.debug_mode:
            if not self.config.debug_get_program:
                raise ValueError("debug_get_program function must be provided when debug_mode=True")
            logger.info("🐛 Debug mode enabled - using debug_get_program function")
            self.api_base = None
            self.api_key = None
        else:
            # API mode validation
            self.api_base = os.getenv('API_BASE')
            self.api_key = os.getenv('API_KEY')
            
            if not self.api_base or not self.api_key:
                raise ValueError("API_BASE and API_KEY must be provided")
        
        self._lock = Lock()
        self._results: List[FetchResult] = []
        self._failed: List[str] = []
    
    @property
    def results(self) -> List[FetchResult]:
        """Thread-safe access to results"""
        with self._lock:
            return self._results.copy()
    
    @property
    def failed(self) -> List[str]:
        """Thread-safe access to failed programs"""
        with self._lock:
            return self._failed.copy()
    
    def _prepare_prompt(self, program_title: str, program_link: str) -> str:
        return f"""
            You are part of a larger degree audit system. Your task is to go to 
            program page at {program_link} and fetch important information in 
            structured format that is necessary for the audit. Do not change the wording
            of the program. You are more like web-scrapper.

            Your output is JSON with the following schema:

            {json.dumps(Block.model_json_schema(), indent=2)}

            Please extract all relevant information and return ONLY valid JSON matching this schema.
            """
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None
    ) -> dict:
        """
        Make an HTTP request with proper error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: JSON payload for POST requests
        
        Returns:
            Response JSON
        
        Raises:
            ProgramFetchError: If request fails
        """
        url = f"{self.api_base}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise ProgramFetchError(f"Request timeout: {endpoint}")
        except requests.exceptions.RequestException as e:
            raise ProgramFetchError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise ProgramFetchError(f"Invalid JSON response: {e}")
    
    def create_task(self, program_title: str, program_link: str) -> str:
        """
        Create a task and return task ID.
        
        Args:
            program_title: Title of the program
            program_link: URL to program page
        
        Returns:
            Task ID
        
        Raises:
            ProgramFetchError: If task creation fails
        """
        prompt = self._prepare_prompt(program_title, program_link)
        
        try:
            data = self._make_request(
                method="POST",
                endpoint="/v1/task/create",
                json_data={
                    "agent": "glitter",
                    "prompt": prompt,
                    "mode": "text",
                    "stepLimit": self.config.step_limit
                }
            )
            
            task_id = data.get("taskId")
            if not task_id:
                raise ProgramFetchError("No taskId in response")
            
            logger.info(f"Created task {task_id} for '{program_title}'")
            return task_id
            
        except ProgramFetchError as e:
            logger.error(f"Failed to create task for '{program_title}': {e}")
            raise
    
    def verify_task_active(self, task_id: str) -> bool:
        """
        Verify that a task is in active status.
        
        Args:
            task_id: Task ID to verify
        
        Returns:
            True if task is active/running/queued/completed
        """
        try:
            data = self._make_request("GET", f"/v1/task/{task_id}")
            state = data.get("state", "")
            
            valid_states = {s.value for s in TaskState}
            if state not in valid_states:
                logger.warning(f"Unknown task state: {state}")
            
            return state in [
                TaskState.ACTIVE.value,
                TaskState.RUNNING.value,
                TaskState.QUEUED.value,
                TaskState.COMPLETED.value
            ]
        except ProgramFetchError as e:
            logger.error(f"Failed to verify task {task_id}: {e}")
            return False
    
    def poll_task(self, task_id: str) -> Optional[dict]:
        """
        Poll task until completion or timeout.
        
        Args:
            task_id: Task ID to poll
        
        Returns:
            Task data if completed, None if failed/timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < self.config.task_timeout:
            try:
                data = self._make_request("GET", f"/v1/task/{task_id}")
                state = data.get("state")
                
                if state == TaskState.COMPLETED.value:
                    logger.info(f"Task {task_id} completed")
                    return data
                elif state == TaskState.FAILED.value:
                    logger.error(f"Task {task_id} failed")
                    return None
                
                time.sleep(self.config.poll_interval)
                
            except ProgramFetchError as e:
                logger.error(f"Error polling task {task_id}: {e}")
                time.sleep(self.config.poll_interval)
        
        logger.error(f"Task {task_id} timed out after {self.config.task_timeout}s")
        return None
    
    def parse_result(self, result_data: dict) -> Optional[Block]:
        """
        Parse and validate result into Block object.
        
        Args:
            result_data: Raw task result data
        
        Returns:
            Program object if parsing succeeds, None otherwise
        """
        try:
            result = result_data.get("result", {})
            answer = result.get("answer", "")
            
            # Extract JSON from answer
            start = answer.find("{")
            end = answer.rfind("}")
            
            if start == -1 or end == -1:
                raise ValueError("No JSON found in answer")
            
            json_str = answer[start:end+1]
            parsed = json.loads(json_str)
            
            # Validate and create Program object
            program = Program(**parsed)
            return program
            
        except (ValueError, json.JSONDecodeError, TypeError) as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def _fetch_debug(self, program_title: str) -> FetchResult:
        """
        Fetch program using debug function (simulates fetching).
        
        Args:
            program_title: Title of program to fetch
        
        Returns:
            FetchResult with success/failure status
        """
        start_time = time.time()
        
        try:
            logger.info(f"🐛 Debug fetching '{program_title}'...")
            program = self.config.debug_get_program(program_title)
            
            # Simulate some processing time
            time.sleep(0.5)
            
            duration = time.time() - start_time
            logger.info(f"✓ Debug fetched '{program_title}' in {duration:.1f}s")
            
            return FetchResult(
                program_title=program_title,
                success=True,
                program=program,
                attempts=1,
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"✗ Debug fetch failed for '{program_title}': {e}")
            
            return FetchResult(
                program_title=program_title,
                success=False,
                error=str(e),
                attempts=1,
                duration_seconds=duration
            )
    
    def fetch_single_program(
        self,
        program_title: str,
        attempt: int = 1
    ) -> FetchResult:
        """
        Fetch and parse a single program with retry logic.
        
        Args:
            program_title: Title of program to fetch
            attempt: Current attempt number (for retry tracking)
        
        Returns:
            FetchResult with success/failure status
        """
        # Debug mode path
        if self.config.debug_mode:
            return self._fetch_debug(program_title)
        
        # Normal API path
        start_time = time.time()
        program_link = self.PROGRAM_CATALOG.get(program_title)
        
        if not program_link:
            return FetchResult(
                program_title=program_title,
                success=False,
                error="Program not in catalog",
                attempts=attempt
            )
        
        try:
            # Create and verify task
            task_id = self.create_task(program_title, program_link)
            
            if not self.verify_task_active(task_id):
                raise ProgramFetchError(f"Task {task_id} not active")
            
            # Poll for results
            result_data = self.poll_task(task_id)
            if not result_data:
                raise ProgramFetchError("Task failed or timed out")
            
            # Parse results
            program = self.parse_result(result_data)
            if not program:
                raise ProgramFetchError("Failed to parse result")
            
            duration = time.time() - start_time
            logger.info(f"✓ Successfully fetched '{program_title}' in {duration:.1f}s")
            
            return FetchResult(
                program_title=program_title,
                success=True,
                program=program,
                attempts=attempt,
                duration_seconds=duration
            )
            
        except ProgramFetchError as e:
            duration = time.time() - start_time
            
            # Retry logic
            if attempt <= self.config.max_retries:
                logger.warning(
                    f"Attempt {attempt} failed for '{program_title}': {e}. Retrying..."
                )
                return self.fetch_single_program(program_title, attempt + 1)
            
            logger.error(f"✗ Failed '{program_title}' after {attempt} attempts: {e}")
            return FetchResult(
                program_title=program_title,
                success=False,
                error=str(e),
                attempts=attempt,
                duration_seconds=duration
            )
    
    def fetch_programs_sync(self, program_titles: List[str]) -> List[Block]:
        """
        Fetch programs synchronously (blocking).
        
        Args:
            program_titles: List of program titles to fetch
        
        Returns:
            List of successfully fetched Program objects
        
        Raises:
            ProgramFetchError: If all programs fail
        """
        programs = []
        failed = []
        
        for title in program_titles:
            result = self.fetch_single_program(title)
            if result.success:
                programs.append(result.program)
            else:
                failed.append(title)
        
        if failed:
            logger.warning(f"Failed to fetch {len(failed)} programs: {failed}")
        
        if not programs:
            raise ProgramFetchError("All program fetches failed")
        
        return programs
    
    def fetch_programs_async(
        self,
        program_titles: List[str],
        on_complete: Optional[Callable[[List[Block], List[str]], None]] = None
    ) -> Thread:
        """
        Fetch programs asynchronously in background thread.
        
        Args:
            program_titles: List of program titles to fetch
            on_complete: Callback(programs, failed_titles) when done
        
        Returns:
            Thread object that can be joined
        
        Raises:
            ValueError: If program_titles is empty
            ProgramFetchError: If task creation fails (non-debug mode only)
        """
        if not program_titles:
            raise ValueError("program_titles cannot be empty")
        
        # Debug mode: simplified async path
        if self.config.debug_mode:
            def debug_worker():
                programs = []
                failed = []
                
                with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                    futures = {
                        executor.submit(self._fetch_debug, title): title
                        for title in program_titles
                    }
                    
                    for future in as_completed(futures):
                        result = future.result()
                        
                        if result.success:
                            programs.append(result.program)
                        else:
                            failed.append(result.program_title)
                
                # Store results
                with self._lock:
                    self._results.extend(
                        [FetchResult(p.title if hasattr(p, 'title') else '', True, p) 
                         for p in programs]
                    )
                    self._failed.extend(failed)
                
                # Invoke callback
                if on_complete:
                    on_complete(programs, failed)
                
                logger.info(
                    f"🐛 Debug fetch complete: {len(programs)} succeeded, {len(failed)} failed"
                )
            
            thread = Thread(target=debug_worker, daemon=True)
            thread.start()
            return thread
        
        # Normal API mode: original implementation
        # Validate all programs exist in catalog
        missing = [t for t in program_titles if t not in self.PROGRAM_CATALOG]
        if missing:
            raise ValueError(f"Programs not in catalog: {missing}")
        
        # Phase 1: Create all tasks upfront and verify
        logger.info(f"Creating tasks for {len(program_titles)} programs...")
        task_mapping: Dict[str, str] = {}  # task_id -> program_title
        
        for title in program_titles:
            try:
                link = self.PROGRAM_CATALOG[title]
                task_id = self.create_task(title, link)
                
                if not self.verify_task_active(task_id):
                    raise ProgramFetchError(f"Task not active: {task_id}")
                
                task_mapping[task_id] = title
                logger.info(f"✓ Task active for '{title}' ({task_id})")
                
            except ProgramFetchError as e:
                logger.error(f"Failed to create task for '{title}': {e}")
                raise
        
        logger.info(f"All {len(task_mapping)} tasks created. Starting polling...")
        
        # Phase 2: Poll and parse asynchronously
        def worker():
            programs = []
            failed = []
            
            def poll_and_parse(task_id: str, title: str, attempt: int = 1) -> FetchResult:
                """Poll specific task and parse, with retry"""
                start_time = time.time()
                
                try:
                    result_data = self.poll_task(task_id)
                    if not result_data:
                        raise ProgramFetchError("Task failed or timed out")
                    
                    program = self.parse_result(result_data)
                    if not program:
                        raise ProgramFetchError("Failed to parse result")
                    
                    duration = time.time() - start_time
                    return FetchResult(
                        program_title=title,
                        success=True,
                        program=program,
                        attempts=attempt,
                        duration_seconds=duration
                    )
                    
                except ProgramFetchError as e:
                    duration = time.time() - start_time
                    
                    # Retry with new task
                    if attempt <= self.config.max_retries:
                        logger.warning(f"Retry {attempt} for '{title}': {e}")
                        try:
                            link = self.PROGRAM_CATALOG[title]
                            new_task_id = self.create_task(title, link)
                            if self.verify_task_active(new_task_id):
                                return poll_and_parse(new_task_id, title, attempt + 1)
                        except ProgramFetchError:
                            pass
                    
                    return FetchResult(
                        program_title=title,
                        success=False,
                        error=str(e),
                        attempts=attempt,
                        duration_seconds=duration
                    )
            
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_title = {
                    executor.submit(poll_and_parse, task_id, title): title
                    for task_id, title in task_mapping.items()
                }
                
                for future in as_completed(future_to_title):
                    result = future.result()
                    
                    if result.success:
                        programs.append(result.program)
                        logger.info(
                            f"✓ '{result.program_title}' completed "
                            f"({result.attempts} attempts, {result.duration_seconds:.1f}s)"
                        )
                    else:
                        failed.append(result.program_title)
                        logger.error(f"✗ '{result.program_title}': {result.error}")
            
            # Store results
            with self._lock:
                self._results.extend(
                    [FetchResult(p.title if hasattr(p, 'title') else '', True, p) 
                     for p in programs]
                )
                self._failed.extend(failed)
            
            # Invoke callback
            if on_complete:
                on_complete(programs, failed)
            
            logger.info(
                f"Fetch complete: {len(programs)} succeeded, {len(failed)} failed"
            )
        
        thread = Thread(target=worker, daemon=True)
        thread.start()
        return thread


# Example usage
if __name__ == "__main__":    
    # === DEBUG MODE ===
    debug_config = FetchConfig(
        debug_mode=True,
        debug_get_program=get_program,
        max_workers=1
    )
    
    debug_fetcher = ProgramFetcher(config=debug_config)
    
    def on_complete_debug(programs, failed):
        print(f"\n🐛 Debug Mode Results:")
        print(f"✓ Success: {len(programs)} programs")
        print(f"✗ Failed: {len(failed)} programs")
    
    thread = debug_fetcher.fetch_programs_async(
        list(debug_fetcher.PROGRAM_CATALOG.keys()),
        on_complete=on_complete_debug
    )
    thread.join()
    
    # === NORMAL MODE ===
    # normal_config = FetchConfig(
    #     max_retries=2,
    #     max_workers=3,
    #     task_timeout=300,
    #     poll_interval=5
    # )
    
    # fetcher = ProgramFetcher(config=normal_config)
    
    # def on_complete(programs, failed):
    #     print(f"\n✓ Success: {len(programs)} programs")
    #     print(f"✗ Failed: {len(failed)} programs")
    #     if failed:
    #         print(f"  Failed: {', '.join(failed)}")
    #     for prog in programs:
    #         print(json.dumps(prog.to_dict(), indent=2))
    
    # thread = fetcher.fetch_programs_async(
    #     list(fetcher.PROGRAM_CATALOG.keys()),
    #     on_complete=on_complete
    # )
    
    # print("Fetching in background...")
    # thread.join()
    # print("Done!")