"""
System checks for verifying environment and dependencies.
"""

import os
import sys
import subprocess
import platform
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import aiohttp
import asyncio
from datetime import datetime


class SystemChecker:
    """Performs system checks and environment verification."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get basic system information."""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_executable": sys.executable
        }
    
    async def check_all_systems(self) -> Dict[str, any]:
        """Perform comprehensive system checks."""
        results = {
            "system_info": self.system_info,
            "python_checks": self.check_python_environment(),
            "network_checks": await self.check_network_connectivity(),
            "provider_checks": await self.check_provider_connectivity(),
            "file_system_checks": self.check_file_system(),
            "dependency_checks": self.check_dependencies(),
            "performance_checks": await self.check_system_performance()
        }
        
        return results
    
    def check_python_environment(self) -> Dict[str, any]:
        """Check Python environment and packages."""
        checks = {
            "python_version_ok": sys.version_info >= (3, 8),
            "python_version": sys.version,
            "site_packages": [],
            "missing_packages": [],
            "package_versions": {}
        }
        
        # Required packages
        required_packages = [
            "PyQt6",
            "aiohttp",
            "cryptography",
            "sqlite3"  # Built-in, but check availability
        ]
        
        for package in required_packages:
            try:
                if package == "sqlite3":
                    import sqlite3
                    checks["package_versions"][package] = sqlite3.sqlite_version
                else:
                    module = __import__(package)
                    version = getattr(module, "__version__", "unknown")
                    checks["package_versions"][package] = version
            except ImportError:
                checks["missing_packages"].append(package)
        
        return checks
    
    async def check_network_connectivity(self) -> Dict[str, any]:
        """Check basic network connectivity."""
        checks = {
            "internet_available": False,
            "dns_resolution": {},
            "connection_errors": []
        }
        
        # Test basic internet connectivity
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://httpbin.org/ip") as response:
                    if response.status == 200:
                        checks["internet_available"] = True
        except Exception as e:
            checks["connection_errors"].append(f"Internet connectivity test failed: {e}")
        
        # Test DNS resolution for various services
        test_domains = [
            "api.openai.com",
            "api.groq.com",
            "api-inference.huggingface.co",
            "openrouter.ai",
            "localhost"  # For Ollama
        ]
        
        for domain in test_domains:
            try:
                import socket
                ip = socket.gethostbyname(domain)
                checks["dns_resolution"][domain] = ip
            except Exception as e:
                checks["dns_resolution"][domain] = f"Resolution failed: {e}"
        
        return checks
    
    async def check_provider_connectivity(self) -> Dict[str, any]:
        """Check connectivity to AI providers."""
        checks = {
            "ollama": {"available": False, "error": None},
            "groq": {"available": False, "error": None},
            "huggingface": {"available": False, "error": None},
            "openrouter": {"available": False, "error": None}
        }
        
        # Check Ollama (localhost)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get("http://localhost:11434/api/tags") as response:
                    checks["ollama"]["available"] = response.status == 200
        except Exception as e:
            checks["ollama"]["error"] = str(e)
        
        # Check Groq API
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://api.groq.com/openai/v1/models") as response:
                    checks["groq"]["available"] = response.status == 200
        except Exception as e:
            checks["groq"]["error"] = str(e)
        
        # Check HuggingFace API
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://api-inference.huggingface.co/models") as response:
                    checks["huggingface"]["available"] = response.status == 200
        except Exception as e:
            checks["huggingface"]["error"] = str(e)
        
        # Check OpenRouter API
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://openrouter.ai/api/v1/models") as response:
                    checks["openrouter"]["available"] = response.status == 200
        except Exception as e:
            checks["openrouter"]["error"] = str(e)
        
        return checks
    
    def check_file_system(self) -> Dict[str, any]:
        """Check file system permissions and space."""
        checks = {
            "config_dir_accessible": False,
            "data_dir_accessible": False,
            "temp_dir_accessible": False,
            "disk_space": {},
            "permission_errors": []
        }
        
        # Check config directory
        try:
            config_dir = Path.home() / ".config" / "chat-linux-client"
            config_dir.mkdir(parents=True, exist_ok=True)
            test_file = config_dir / ".test"
            test_file.write_text("test")
            test_file.unlink()
            checks["config_dir_accessible"] = True
        except Exception as e:
            checks["permission_errors"].append(f"Config directory error: {e}")
        
        # Check data directory
        try:
            if platform.system() == "Windows":
                data_dir = Path.home() / "AppData" / "Local" / "ChatLinuxClient" / "data"
            else:
                data_dir = Path.home() / ".local" / "share" / "chat-linux-client"
            
            data_dir.mkdir(parents=True, exist_ok=True)
            test_file = data_dir / ".test"
            test_file.write_text("test")
            test_file.unlink()
            checks["data_dir_accessible"] = True
        except Exception as e:
            checks["permission_errors"].append(f"Data directory error: {e}")
        
        # Check temp directory
        try:
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            test_file = temp_dir / ".chat_client_test"
            test_file.write_text("test")
            test_file.unlink()
            checks["temp_dir_accessible"] = True
        except Exception as e:
            checks["permission_errors"].append(f"Temp directory error: {e}")
        
        # Check disk space
        try:
            import shutil
            for path in [Path.home(), temp_dir if 'temp_dir' in locals() else Path("/tmp")]:
                if path.exists():
                    total, used, free = shutil.disk_usage(path)
                    checks["disk_space"][str(path)] = {
                        "total_gb": round(total / (1024**3), 2),
                        "used_gb": round(used / (1024**3), 2),
                        "free_gb": round(free / (1024**3), 2)
                    }
        except Exception as e:
            checks["permission_errors"].append(f"Disk space check error: {e}")
        
        return checks
    
    def check_dependencies(self) -> Dict[str, any]:
        """Check external dependencies and tools."""
        checks = {
            "git_available": False,
            "curl_available": False,
            "wget_available": False,
            "docker_available": False,
            "system_tools": {}
        }
        
        # Check for common tools
        tools = ["git", "curl", "wget", "docker"]
        
        for tool in tools:
            try:
                result = subprocess.run(
                    ["which" if platform.system() != "Windows" else "where", tool],
                    capture_output=True,
                    text=True
                )
                checks[f"{tool}_available"] = result.returncode == 0
                if result.returncode == 0:
                    checks["system_tools"][tool] = result.stdout.strip()
            except Exception:
                checks[f"{tool}_available"] = False
        
        return checks
    
    async def check_system_performance(self) -> Dict[str, any]:
        """Check system performance metrics."""
        checks = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_io": {},
            "network_latency": {}
        }
        
        try:
            import psutil
            
            # CPU usage
            checks["cpu_usage"] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            checks["memory_usage"] = memory.percent
            checks["memory_total_gb"] = round(memory.total / (1024**3), 2)
            checks["memory_available_gb"] = round(memory.available / (1024**3), 2)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                checks["disk_io"] = {
                    "read_mb": round(disk_io.read_bytes / (1024**2), 2),
                    "write_mb": round(disk_io.write_bytes / (1024**2), 2)
                }
            
        except ImportError:
            self.logger.warning("psutil not available for performance checks")
        except Exception as e:
            self.logger.error(f"Performance check failed: {e}")
        
        # Network latency
        test_hosts = ["google.com", "github.com"]
        for host in test_hosts:
            try:
                import socket
                start_time = asyncio.get_event_loop().time()
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, 80),
                    timeout=5
                )
                latency = (asyncio.get_event_loop().time() - start_time) * 1000
                checks["network_latency"][host] = round(latency, 2)
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                checks["network_latency"][host] = f"Failed: {e}"
        
        return checks
    
    def check_display_server(self) -> Dict[str, any]:
        """Check display server and GUI environment."""
        checks = {
            "display_available": False,
            "display_server": "unknown",
            "wayland": False,
            "x11": False,
            "environment_variables": {}
        }
        
        # Check environment variables
        display_vars = ["DISPLAY", "WAYLAND_DISPLAY", "XDG_SESSION_TYPE"]
        for var in display_vars:
            value = os.getenv(var)
            checks["environment_variables"][var] = value
            if value:
                checks["display_available"] = True
        
        # Detect display server type
        if os.getenv("WAYLAND_DISPLAY"):
            checks["display_server"] = "wayland"
            checks["wayland"] = True
        elif os.getenv("DISPLAY"):
            checks["display_server"] = "x11"
            checks["x11"] = True
        
        return checks
    
    def generate_system_report(self) -> str:
        """Generate a comprehensive system report."""
        report_lines = [
            "Chat Linux Client - System Report",
            "=" * 40,
            "",
            f"Platform: {self.system_info['platform']} {self.system_info['platform_release']}",
            f"Architecture: {self.system_info['architecture']}",
            f"Python: {self.system_info['python_version']}",
            f"Python Executable: {self.system_info['python_executable']}",
            ""
        ]
        
        # Add display server info
        display_info = self.check_display_server()
        report_lines.extend([
            "Display Server:",
            f"  Available: {display_info['display_available']}",
            f"  Type: {display_info['display_server']}",
            f"  Wayland: {display_info['wayland']}",
            f"  X11: {display_info['x11']}",
            ""
        ])
        
        # Add dependency info
        deps = self.check_dependencies()
        report_lines.extend([
            "System Tools:",
            f"  Git: {'Available' if deps['git_available'] else 'Not Available'}",
            f"  Curl: {'Available' if deps['curl_available'] else 'Not Available'}",
            f"  Docker: {'Available' if deps['docker_available'] else 'Not Available'}",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def get_recommendations(self, check_results: Dict[str, any]) -> List[str]:
        """Get system recommendations based on check results."""
        recommendations = []
        
        # Python version check
        if not check_results["python_checks"]["python_version_ok"]:
            recommendations.append(
                "Upgrade Python to version 3.8 or higher for best compatibility"
            )
        
        # Missing packages
        missing = check_results["python_checks"]["missing_packages"]
        if missing:
            recommendations.append(
                f"Install missing packages: {', '.join(missing)}"
            )
        
        # Network connectivity
        if not check_results["network_checks"]["internet_available"]:
            recommendations.append(
                "Check internet connection for cloud-based AI providers"
            )
        
        # File system permissions
        fs_errors = check_results["file_system_checks"]["permission_errors"]
        if fs_errors:
            recommendations.append(
                "Fix file system permissions for config and data directories"
            )
        
        # Ollama availability
        if not check_results["provider_checks"]["ollama"]["available"]:
            recommendations.append(
                "Install and start Ollama for local AI model support: "
                "https://ollama.ai/download"
            )
        
        # Performance issues
        perf = check_results.get("performance_checks", {})
        if perf.get("memory_usage", 0) > 80:
            recommendations.append(
                "High memory usage detected. Consider closing other applications"
            )
        
        if perf.get("cpu_usage", 0) > 80:
            recommendations.append(
                "High CPU usage detected. Consider closing other applications"
            )
        
        return recommendations
