# ============================================================
# Business AI Data Generator
# Database Connection + Setup Module
# Compatible with GCP Cloud SQL PostgreSQL 18.2
# ============================================================

import os
import sys
import time
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from datetime import datetime
from typing import Optional, Dict, Any

# ============================================================
# CONNECTION CONFIGURATION
# ============================================================

class DatabaseConfig:
    """
    Holds all database configuration.
    Reads from environment variables.
    Never hardcode credentials.
    """
    
    def __init__(self):
        # Primary connection details
        self.host     = os.environ.get('DB_HOST', '34.131.80.243')
        self.port     = int(os.environ.get('DB_PORT', '5432'))
        self.dbname   = os.environ.get('DB_NAME', 'gotrackpro')
        self.user     = os.environ.get('DB_USER', '')
        self.password = os.environ.get('DB_PASSWORD', '')
        
        # SSL Configuration
        # GCP requires SSL - sslmode=require
        self.sslmode  = os.environ.get('DB_SSLMODE', 'require')
        
        # Connection pool settings
        self.min_connections = 1
        self.max_connections = 5  # Keep low for Colab
        
        # Timeouts
        self.connect_timeout = 30
        self.query_timeout   = 60
        
    def get_connection_string(self) -> str:
        """Returns full connection string."""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.dbname}"
            f"?sslmode={self.sslmode}"
        )
    
    def get_psycopg2_params(self) -> Dict[str, Any]:
        """Returns params dict for psycopg2."""
        return {
            'host':             self.host,
            'port':             self.port,
            'dbname':           self.dbname,
            'user':             self.user,
            'password':         self.password,
            'sslmode':          self.sslmode,
            'connect_timeout':  self.connect_timeout,
        }
    
    def validate(self) -> bool:
        """Check all required fields are set."""
        missing = []
        if not self.user:
            missing.append('DB_USER')
        if not self.password:
            missing.append('DB_PASSWORD')
        if not self.host:
            missing.append('DB_HOST')
        if not self.dbname:
            missing.append('DB_NAME')
            
        if missing:
            print(f"[ERROR] Missing environment variables: {missing}")
            return False
        return True


# ============================================================
# DATABASE MANAGER
# ============================================================

class DatabaseManager:
    """
    Manages all database operations.
    Handles connections, retries, and errors.
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection_pool = None
        self._setup_complete = False
        
    def initialize(self) -> bool:
        """
        Full initialization sequence.
        Call this once at start of each Colab session.
        """
        print("\n" + "="*55)
        print("  BUSINESS AI DATABASE INITIALIZATION")
        print("="*55)
        
        # Step 1: Validate config
        print("\n[1/5] Validating configuration...")
        if not self.config.validate():
            return False
        print("      ✅ Configuration valid")
        
        # Step 2: Test connection
        print("\n[2/5] Testing connection to GCP PostgreSQL...")
        if not self._test_connection():
            return False
        print("      ✅ Connection successful")
        print(f"      📍 Host: {self.config.host}:{self.config.port}")
        print(f"      🗄️  Database: {self.config.dbname}")
        
        # Step 3: Create connection pool
        print("\n[3/5] Creating connection pool...")
        if not self._create_pool():
            return False
        print("      ✅ Connection pool ready")
        
        # Step 4: Check pgvector
        print("\n[4/5] Checking pgvector extension...")
        self._check_and_install_pgvector()
        
        # Step 5: Verify tables
        print("\n[5/5] Verifying database tables...")
        self._verify_tables()
        
        self._setup_complete = True
        print("\n" + "="*55)
        print("  ✅ DATABASE READY FOR GENERATION")
        print("="*55 + "\n")
        return True
    
    def _test_connection(self) -> bool:
        """Test basic connectivity with retry logic."""
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(1, max_retries + 1):
            try:
                conn = psycopg2.connect(
                    **self.config.get_psycopg2_params()
                )
                
                # Test with simple query
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                
                cursor.close()
                conn.close()
                
                # Show version info
                version_short = version.split(',')[0]
                print(f"      📊 Version: {version_short}")
                return True
                
            except psycopg2.OperationalError as e:
                print(f"      ⚠️  Attempt {attempt}/{max_retries} failed")
                print(f"      Error: {str(e)[:100]}")
                
                if attempt < max_retries:
                    print(f"      Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print("\n      ❌ CONNECTION FAILED")
                    print("\n      TROUBLESHOOTING STEPS:")
                    print("      1. Go to GCP Console → Cloud SQL")
                    print("      2. Connections → Networking")
                    print("      3. Authorized Networks → Add 0.0.0.0/0")
                    print("      4. Wait 2 minutes → Try again")
                    return False
                    
            except Exception as e:
                print(f"      ❌ Unexpected error: {e}")
                return False
    
    def _create_pool(self) -> bool:
        """Create connection pool."""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                **self.config.get_psycopg2_params()
            )
            return True
        except Exception as e:
            print(f"      ❌ Pool creation failed: {e}")
            return False
    
    def _check_and_install_pgvector(self):
        """Check pgvector and install if missing."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if already installed
            cursor.execute(
                "SELECT extname, extversion FROM pg_extension "
                "WHERE extname = 'vector';"
            )
            result = cursor.fetchone()
            
            if result:
                print(f"      ✅ pgvector {result[1]} installed")
            else:
                # Try to install
                print("      📦 Installing pgvector...")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                conn.commit()
                print("      ✅ pgvector installed successfully")
                
            cursor.close()
            self.return_connection(conn)
            
        except Exception as e:
            print(f"      ⚠️  pgvector check failed: {e}")
            print("      ℹ️  Embeddings will be stored as JSONB instead")
    
    def _verify_tables(self):
        """Check all required tables exist."""
        required_tables = [
            'training_samples',
            'generation_log', 
            'category_stats',
            'prompt_templates'
        ]
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            existing = [row[0] for row in cursor.fetchall()]
            
            all_good = True
            for table in required_tables:
                if table in existing:
                    print(f"      ✅ {table}")
                else:
                    print(f"      ❌ {table} - MISSING")
                    all_good = False
            
            if not all_good:
                print("\n      ⚠️  Some tables missing.")
                print("      Run scripts/db_setup.sql first")
                print("      Instructions:")
                print("      1. Open GCP Console → Cloud SQL")
                print("      2. Open Cloud Shell or connect via psql")
                print("      3. Run: psql -U user -d gotrackpro -f db_setup.sql")
            
            # Show current data counts
            cursor.execute("SELECT COUNT(*) FROM training_samples;")
            total = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT COUNT(*) FROM training_samples "
                "WHERE quality_flag = 'PASS';"
            )
            passed = cursor.fetchone()[0]
            
            print(f"\n      📊 Current dataset: {total:,} total | "
                  f"{passed:,} passed")
            
            cursor.close()
            self.return_connection(conn)
            
        except Exception as e:
            print(f"      ❌ Table verification failed: {e}")
    
    def get_connection(self):
        """Get connection from pool."""
        if self.connection_pool:
            return self.connection_pool.getconn()
        else:
            # Fallback: direct connection
            return psycopg2.connect(
                **self.config.get_psycopg2_params()
            )
    
    def return_connection(self, conn):
        """Return connection to pool."""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
        else:
            conn.close()
    
    def execute_query(
        self, 
        query: str, 
        params: tuple = None,
        fetch: bool = False
    ) -> Optional[Any]:
        """
        Execute any query with error handling.
        Auto-commits and returns results if fetch=True.
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                self.return_connection(conn)
                return result
            else:
                conn.commit()
                cursor.close()
                self.return_connection(conn)
                return True
                
        except psycopg2.IntegrityError as e:
            # Duplicate key etc - not critical
            if conn:
                conn.rollback()
                self.return_connection(conn)
            return None
            
        except Exception as e:
            print(f"[DB ERROR] Query failed: {e}")
            print(f"[DB ERROR] Query: {query[:100]}")
            if conn:
                conn.rollback()
                self.return_connection(conn)
            return None
    
    def close(self):
        """Close all connections cleanly."""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("[DB] Connection pool closed")


# ============================================================
# GLOBAL DATABASE INSTANCE
# ============================================================

_db_manager: Optional[DatabaseManager] = None

def get_db() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError(
            "Database not initialized. "
            "Call initialize_database() first."
        )
    return _db_manager

def initialize_database() -> DatabaseManager:
    """
    Initialize database connection.
    Call this at the start of every Colab session.
    """
    global _db_manager
    
    config = DatabaseConfig()
    _db_manager = DatabaseManager(config)
    
    success = _db_manager.initialize()
    
    if not success:
        raise RuntimeError(
            "Database initialization failed. "
            "Check error messages above."
        )
    
    return _db_manager