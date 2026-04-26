#!/usr/bin/env python3
"""
Chat Linux Client - Main Entry Point
Private multi-provider AI desktop client for Linux systems.

This application provides a unified interface for interacting with multiple AI providers
including OpenAI, Ollama (local), Groq, HuggingFace, and OpenRouter.
"""

import sys
import os
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import argparse

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import application modules
from ui.main_window import ChatWindow
from core.settings import SettingsManager
from utils.system_checks import SystemChecker


def setup_logging(log_level: str = "INFO") -> None:
    """Setup application logging."""
    # Create logs directory
    logs_dir = Path.home() / ".local" / "share" / "chat-linux-client" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup log file
    log_file = logs_dir / f"chat_client_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Chat Linux Client - Private multi-provider AI desktop client"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    parser.add_argument(
        "--new-chat",
        action="store_true",
        help="Start with a new chat session"
    )
    
    parser.add_argument(
        "--settings",
        action="store_true",
        help="Open settings dialog on startup"
    )
    
    parser.add_argument(
        "--check-system",
        action="store_true",
        help="Run system checks and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Chat Linux Client 1.0.0"
    )
    
    return parser.parse_args()


async def run_system_checks() -> None:
    """Run comprehensive system checks."""
    print("Running system checks...")
    
    checker = SystemChecker()
    results = await checker.check_all_systems()
    
    print("\n" + "="*50)
    print("SYSTEM CHECK REPORT")
    print("="*50)
    
    # System info
    print(f"\nSystem: {results['system_info']['platform']} {results['system_info']['platform_release']}")
    print(f"Python: {results['system_info']['python_version']}")
    
    # Python checks
    python_checks = results['python_checks']
    print(f"\nPython Environment:")
    print(f"  Version OK: {python_checks['python_version_ok']}")
    print(f"  Missing packages: {', '.join(python_checks['missing_packages']) if python_checks['missing_packages'] else 'None'}")
    
    # Network checks
    network_checks = results['network_checks']
    print(f"\nNetwork Connectivity:")
    print(f"  Internet: {'Available' if network_checks['internet_available'] else 'Not Available'}")
    
    # Provider checks
    provider_checks = results['provider_checks']
    print(f"\nAI Provider Connectivity:")
    for provider, check in provider_checks.items():
        status = "Available" if check['available'] else f"Not Available ({check.get('error', 'Unknown error')})"
        print(f"  {provider.title()}: {status}")
    
    # File system checks
    fs_checks = results['file_system_checks']
    print(f"\nFile System:")
    print(f"  Config dir accessible: {fs_checks['config_dir_accessible']}")
    print(f"  Data dir accessible: {fs_checks['data_dir_accessible']}")
    
    # Recommendations
    recommendations = checker.get_recommendations(results)
    if recommendations:
        print(f"\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "="*50)
    print("System check complete.")
    print("="*50)


def main() -> int:
    """Main application entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Run system checks if requested
        if args.check_system:
            asyncio.run(run_system_checks())
            return 0
        
        # Initialize application
        logger.info("Starting Chat Linux Client...")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Chat Linux Client")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("ChatLinuxClient")
        
        # Set high DPI scaling (PyQt6 handles this automatically)
        
        # Load settings
        settings_manager = SettingsManager()
        
        # Create and show main window
        main_window = ChatWindow()
        main_window.show()
        
        # Handle command line arguments
        if args.new_chat:
            main_window.clear_chat()
        
        if args.settings:
            # This would open settings dialog when implemented
            logger.info("Settings dialog requested (not yet implemented)")
        
        # Setup cleanup
        def cleanup():
            logger.info("Application shutting down...")
            settings_manager.save()
        
        app.aboutToQuit.connect(cleanup)
        
        # Start the application
        logger.info("Application started successfully")
        return app.exec()
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
