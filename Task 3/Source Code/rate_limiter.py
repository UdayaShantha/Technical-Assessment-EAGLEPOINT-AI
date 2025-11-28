import time
from threading import Lock
from collections import defaultdict
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta


class RateLimiter:
    """
    A thread-safe rate limiter using the Fixed Window algorithm.
    
    Key Features:
    - Per-user rate limiting
    - Automatic window reset after time expires
    - Thread-safe implementation
    - No external dependencies
    - Tracks requests per 60-second window
    
    Design Rationale (Fixed Window chosen over alternatives):
    - Simplicity: Easy to understand and maintain
    - Memory efficient: Single counter per user
    - Performance: O(1) time complexity for checks
    - Suitable for per-user limits
    - No complex state tracking needed
    
    Alternative algorithms considered:
    1. Token Bucket: Better for bursts, but more complex
    2. Sliding Window: More accurate but higher memory cost
    3. Sliding Window Counter: Moderate complexity, better accuracy
    
    For this use case (5 req/60 sec), Fixed Window is optimal.
    """
    
    def __init__(self, max_requests: int = 5, window_size: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed per window.
                               Default: 5 (as per requirements)
            window_size (int): Time window duration in seconds.
                             Default: 60 (as per requirements)
                             
        Raises:
            ValueError: If max_requests <= 0 or window_size <= 0
        """
        
        # Validate inputs
        if max_requests <= 0:
            raise ValueError("max_requests must be greater than 0")
        if window_size <= 0:
            raise ValueError("window_size must be greater than 0")
        
        self.max_requests = max_requests
        self.window_size = window_size
        
        # Core Data Structure
        # Dictionary tracking per-user request windows
        # Structure: {user_id: (window_start_timestamp, request_count)}

        # Using tuple for immutability ensures atomic-like operations
        # when combined with locks. (timestamp, count) captures all state.
        self.user_requests: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0, 0))
        
        # Thread Safety
        # Reentrant lock to handle nested/recursive locking scenarios
        # Protects access to user_requests dictionary
        # Prevents race conditions in concurrent environments
        self.lock = Lock()
    
    def is_allowed(self, user_id: str) -> bool:
        """
        Determine if a request from a user should be allowed.
        
        Algorithm Steps:
        1. Acquire lock for thread safety
        2. Get current time and user's window state
        3. Check if window has expired
        4. If expired: reset window and counter
        5. If within limit: increment counter and allow
        6. If exceeded limit: deny request
        
        Args:
            user_id (str): Unique identifier for the user/client
                          Examples: "user_123", "api_key_xyz", "192.168.1.1"
        
        Returns:
            bool: True if request is allowed, False if rate limit exceeded
        """
        
        with self.lock:
            # Step 1: Get current time (reference point for window)
            current_time = time.time()
            
            # Step 2: Retrieve user's current window state
            # If user doesn't exist, defaultdict returns (0, 0)
            window_start, request_count = self.user_requests[user_id]
            
            # Step 3: Check if current window has expired
            # If time elapsed >= window_size, we start a new window
            time_elapsed = current_time - window_start
            window_expired = time_elapsed >= self.window_size
            
            if window_expired:
                # Step 4a: Window expired - reset to new window
                # New window starts now with 0 requests
                window_start = current_time
                request_count = 0
                
                # Update state
                self.user_requests[user_id] = (window_start, request_count)
            
            # Step 5: Check if request should be allowed
            if request_count < self.max_requests:
                # Within limit - allow request
                # Increment counter for this window
                new_count = request_count + 1
                self.user_requests[user_id] = (window_start, new_count)
                return True
            else:
                # Step 6: Limit exceeded - deny request
                # Don't update state, just return False
                return False
    
    def get_status(self, user_id: str) -> dict:
        """
        Get detailed status information for a user.
        
        Useful for monitoring, debugging, and providing feedback
        about current rate limit state.
        
        Args:
            user_id (str): Unique identifier for the user
        
        Returns:
            dict: Status dictionary with keys:
                - user_id: The user identifier
                - requests_made: Number of requests in current window
                - requests_remaining: Requests still available
                - window_start: Unix timestamp when window started
                - time_until_reset: Seconds until window resets
                - limit: Maximum requests allowed
                - window_size: Window duration in seconds
        """
        
        with self.lock:
            current_time = time.time()
            window_start, request_count = self.user_requests[user_id]
            
            # Check if in new window
            time_elapsed = current_time - window_start
            if time_elapsed >= self.window_size:
                # Window has expired, treat as new window
                window_start = current_time
                request_count = 0
            
            # Calculate remaining requests
            remaining = self.max_requests - request_count
            
            # Calculate seconds until window resets
            time_until_reset = self.window_size - (current_time - window_start)
            
            return {
                "user_id": user_id,
                "requests_made": request_count,
                "requests_remaining": remaining,
                "window_start": window_start,
                "time_until_reset": round(time_until_reset, 2),
                "limit": self.max_requests,
                "window_size": self.window_size
            }
    
    def reset_user(self, user_id: str) -> None:
        """
        Manually reset rate limit for a specific user.
        
        Useful for administrative operations (e.g., granting extra requests
        to a specific user, or resetting after abuse detection).
        
        Args:
            user_id (str): User identifier to reset
        """
        
        with self.lock:
            self.user_requests[user_id] = (0, 0)
    
    def reset_all(self) -> None:
        """
        Reset rate limits for all users.
        
        Use with caution - typically only during system maintenance
        or configuration changes.
        """
        
        with self.lock:
            self.user_requests.clear()
    
    def get_all_users_status(self) -> dict:
        """
        Get status for all tracked users.
        
        Returns:
            dict: Mapping of user_id to status dictionaries
        """
        
        with self.lock:
            return {
                user_id: {
                    "requests_made": request_count,
                    "requests_remaining": self.max_requests - request_count,
                    "time_until_reset": round(
                        self.window_size - (time.time() - window_start), 2
                    )
                }
                for user_id, (window_start, request_count) 
                in self.user_requests.items()
            }


#Example one
def example_basic_usage():
    """
    Example : Basic rate limiting for API endpoint
    
    Scenario: Protecting an API endpoint from being overwhelmed
    by a single user making too many requests.
    """
    print("\n" + "=" * 70)
    print("Example 1: Basic API Endpoint Protection")
    print("=" * 70)
    
    limiter = RateLimiter(max_requests=5, window_size=60)
    
    # Simulate API endpoint
    def api_endpoint(user_id: str, action: str) -> dict:
        """Simulate an API endpoint that respects rate limits."""
        
        if limiter.is_allowed(user_id):
            return {
                "status": "success",
                "message": f"Processing {action} for {user_id}",
                "remaining": limiter.get_status(user_id)["requests_remaining"]
            }
        else:
            return {
                "status": "error",
                "message": "Rate limit exceeded",
                "remaining": 0
            }
    
    # Simulate requests from a user
    user = "alice"
    for i in range(7):
        result = api_endpoint(user, f"action_{i}")
        status = "✓" if result["status"] == "success" else "✗"
        print(f"{status} Request {i+1}: {result['message']} | "
              f"Remaining: {result['remaining']}")


#Example Two
def example_multiple_users():
    """
    Example : Rate limiting multiple independent users
    
    Scenario: A service with multiple users, each with their
    own request quota that operates independently.
    """
    print("\n" + "=" * 70)
    print("Example 2: Multiple Independent Users")
    print("=" * 70)
    
    limiter = RateLimiter(max_requests=5, window_size=60)
    
    users = ["alice", "bob", "charlie"]
    
    # Each user makes 5 requests (should all succeed)
    print("\nFirst round - all users within limit:")
    for user in users:
        for req in range(5):
            limiter.is_allowed(user)
        status = limiter.get_status(user)
        print(f"  {user:8} | Made: {status['requests_made']}, "
              f"Remaining: {status['requests_remaining']}")
    
    # All users try 6th request (should fail for all)
    print("\nSecond round - 6th request for each user:")
    for user in users:
        allowed = limiter.is_allowed(user)
        result = "✓ Allowed" if allowed else "✗ Blocked"
        print(f"  {user:8} | {result}")


#Example Three
def example_status_monitoring():
    """
    Example : Monitoring user rate limit status
    
    Scenario: Dashboard or monitoring system that needs to
    display current rate limit status for users.
    """
    print("\n" + "=" * 70)
    print("Example 3: Rate Limit Status Monitoring")
    print("=" * 70)
    
    limiter = RateLimiter(max_requests=5, window_size=60)
    
    # Simulate some activity
    users_activity = {
        "user_1": 2,  # 2 requests
        "user_2": 5,  # 5 requests (at limit)
        "user_3": 0   # 0 requests
    }
    
    for user, count in users_activity.items():
        for _ in range(count):
            limiter.is_allowed(user)
    
    # Display all statuses
    print("\nCurrent Rate Limit Status:")
    print("-" * 70)
    all_status = limiter.get_all_users_status()
    
    for user_id, status in all_status.items():
        bar_length = status['requests_made']
        bar = "█" * bar_length + "░" * (5 - bar_length)
        print(f"{user_id:8} | Requests: [{bar}] | "
              f"Remaining: {status['requests_remaining']}")


#Example Four
def example_web_server_simulation():
    """
    Example : Web server handling concurrent requests
    
    Scenario: A simple web server handling requests from
    multiple users with rate limiting.
    """
    print("\n" + "=" * 70)
    print("Example 4: Web Server Request Handling")
    print("=" * 70)
    
    limiter = RateLimiter(max_requests=5, window_size=60)
    
    # Simulate web server handling requests
    def handle_request(user_id: str, request_data: dict) -> dict:
        """Handle incoming HTTP request with rate limiting."""
        
        if not limiter.is_allowed(user_id):
            return {
                "status_code": 429,  # Too Many Requests
                "body": "Rate limit exceeded. Try again in 60 seconds.",
                "headers": {
                    "X-RateLimit-Limit": "5",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 60)
                }
            }
        
        status = limiter.get_status(user_id)
        return {
            "status_code": 200,
            "body": f"Success: {request_data.get('action', 'unknown')}",
            "headers": {
                "X-RateLimit-Limit": str(status["limit"]),
                "X-RateLimit-Remaining": str(status["requests_remaining"]),
                "X-RateLimit-Reset": str(int(time.time() + status["time_until_reset"]))
            }
        }
    
    # Simulate incoming requests
    requests_queue = [
        ("user_123", {"action": "fetch_data"}),
        ("user_123", {"action": "fetch_data"}),
        ("user_456", {"action": "update_profile"}),
        ("user_123", {"action": "fetch_data"}),
        ("user_123", {"action": "fetch_data"}),
        ("user_123", {"action": "fetch_data"}),
        ("user_123", {"action": "fetch_data"}),  # This will be blocked
        ("user_456", {"action": "delete_account"}),
    ]
    
    print("\nProcessing incoming requests:")
    print("-" * 70)
    for user_id, request in requests_queue:
        response = handle_request(user_id, request)
        status_text = "200 OK" if response["status_code"] == 200 else "429 Rate Limited"
        remaining = response["headers"]["X-RateLimit-Remaining"]
        print(f"{user_id:10} | {status_text:20} | "
              f"Remaining: {remaining}")


#Example Five
def example_error_handling():
    """
    Example : Error handling and edge cases
    
    Scenario: Demonstrating proper error handling and
    validation of rate limiter inputs.
    """
    print("\n" + "=" * 70)
    print("Example 5: Error Handling & Validation")
    print("=" * 70)
    
    # Test invalid configurations
    test_cases = [
        {"max_requests": 5, "window_size": 60, "description": "Valid config"},
        {"max_requests": -1, "window_size": 60, "description": "Negative requests"},
        {"max_requests": 5, "window_size": 0, "description": "Zero window"},
    ]
    
    for test in test_cases:
        try:
            limiter = RateLimiter(
                max_requests=test["max_requests"],
                window_size=test["window_size"]
            )
            print(f"✓ {test['description']:20} | Success")
        except ValueError as e:
            print(f"✗ {test['description']:20} | Error: {e}")


#Example Six
def example_custom_limits():
    """
    Example : Custom rate limits for different use cases
    
    Scenario: Different endpoints or services with
    different rate limit requirements.
    """
    print("\n" + "=" * 70)
    print("Example 6: Custom Rate Limits")
    print("=" * 70)
    
    # Different limiters for different endpoints
    search_limiter = RateLimiter(max_requests=100, window_size=60)
    upload_limiter = RateLimiter(max_requests=10, window_size=60)
    payment_limiter = RateLimiter(max_requests=5, window_size=3600)  # Per hour
    
    user = "user_xyz"
    
    print(f"\n{user} making requests to different endpoints:")
    print("-" * 70)
    
    # Search requests (high limit)
    searches = sum(1 for _ in range(50) if search_limiter.is_allowed(user))
    print(f"Search requests:  {searches}/100 allowed")
    
    # Upload requests (medium limit)
    uploads = sum(1 for _ in range(10) if upload_limiter.is_allowed(user))
    print(f"Upload requests:  {uploads}/10 allowed")
    
    # Payment requests (low limit per hour)
    payments = sum(1 for _ in range(5) if payment_limiter.is_allowed(user))
    print(f"Payment requests: {payments}/5 allowed (per hour)")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_multiple_users()
    example_status_monitoring()
    example_web_server_simulation()
    example_error_handling()
    example_custom_limits()
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
