"""
Base class for all system agents
"""

import threading
import time
from queue import Queue, Empty  # Import Empty exception directly
from typing import Any, Optional

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, input_queue: Optional[Queue] = None, output_queue: Optional[Queue] = None):
        """
        Initialize a base agent
        
        Args:
            name: Agent name
            input_queue: Queue for inputs (optional)
            output_queue: Queue for outputs (optional)
        """
        self.name = name
        self.input_queue = input_queue or Queue()
        self.output_queue = output_queue
        self.running = False
        self.thread = None
    
    def start(self) -> None:
        """
        Start the agent in a separate thread
        """
        if self.running:
            print(f"WARNING - Agent {self.name} already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"INFO - Agent {self.name} started")
    
    def stop(self) -> None:
        """
        Stop the agent
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            print(f"INFO - Agent {self.name} stopped")
    
    def _run(self) -> None:
        """
        Main method executed in the thread
        To be overridden in derived classes
        """
        while self.running:
            try:
                # Get an item from the input queue with timeout
                data = self.input_queue.get(timeout=0.1)
                
                # Process the item
                result = self.process(data)
                
                # If an output queue is defined and there's a result
                if self.output_queue is not None and result is not None:
                    self.output_queue.put(result)
                    
            except Empty:
                # This is a normal timeout from the queue, just continue
                pass
            except Exception as e:
                # Log other types of exceptions
                print(f"ERROR - Agent {self.name} encountered an error: {str(e)}")
                    
            # Small pause to avoid CPU saturation
            time.sleep(0.01)
    
    def process(self, data: Any) -> Any:
        """
        Process an input and produce an output
        To be overridden in derived classes
        
        Args:
            data: Data to process
            
        Returns:
            Any: Processing result or None
        """
        raise NotImplementedError("The process method must be implemented in subclasses")
    
    def send(self, data: Any) -> None:
        """
        Send data to the agent via its input queue
        
        Args:
            data: Data to send
        """
        self.input_queue.put(data)