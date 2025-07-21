"""
Automated Backup Manager for Economics AI Dashboard
Ensures data safety during cleanup operations
"""

import shutil
import datetime
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
import hashlib

class BackupManager:
    """Manages automated backups of the database and related files"""
    
    def __init__(self, db_path: str = "data/database/economics_ai.db", backup_dir: str = "backups"):
        """
        Initialize the backup manager
        
        Args:
            db_path: Path to the database file
            backup_dir: Directory to store backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Backup metadata file
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load backup metadata from file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"backups": [], "last_backup": None}
    
    def _save_metadata(self):
        """Save backup metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def create_backup(self, tag: str = "", source_id: Optional[int] = None) -> Path:
        """
        Create a backup of the database
        
        Args:
            tag: Optional tag for the backup (e.g., "pre_source_3_cleanup")
            source_id: Optional source ID being processed
            
        Returns:
            Path to the created backup
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        # Generate backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        tag_part = f"_{tag}" if tag else ""
        source_part = f"_source{source_id}" if source_id else ""
        backup_name = f"economics_ai{tag_part}{source_part}_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        # Calculate original file checksum
        original_checksum = self._calculate_checksum(self.db_path)
        
        # Copy the database
        shutil.copy2(self.db_path, backup_path)
        
        # Verify backup integrity
        backup_checksum = self._calculate_checksum(backup_path)
        if original_checksum != backup_checksum:
            backup_path.unlink()  # Delete corrupted backup
            raise RuntimeError("Backup verification failed - checksums don't match")
        
        # Get file sizes
        original_size = self.db_path.stat().st_size
        backup_size = backup_path.stat().st_size
        
        # Update metadata
        backup_info = {
            "filename": backup_name,
            "path": str(backup_path),
            "timestamp": timestamp,
            "tag": tag,
            "source_id": source_id,
            "checksum": backup_checksum,
            "size_bytes": backup_size,
            "original_size_bytes": original_size
        }
        
        self.metadata["backups"].append(backup_info)
        self.metadata["last_backup"] = timestamp
        self._save_metadata()
        
        self.logger.info(f"Backup created: {backup_path}")
        self.logger.info(f"Checksum: {backup_checksum}")
        
        return backup_path
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore a specific backup
        
        Args:
            backup_name: Name of the backup file to restore
            
        Returns:
            True if successful, False otherwise
        """
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            self.logger.error(f"Backup not found: {backup_path}")
            return False
        
        # Create a safety backup of current state before restoring
        try:
            self.create_backup(tag="pre_restore")
        except Exception as e:
            self.logger.warning(f"Could not create pre-restore backup: {e}")
        
        # Restore the backup
        try:
            shutil.copy2(backup_path, self.db_path)
            self.logger.info(f"Restored backup: {backup_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False
    
    def cleanup_old_backups(self, keep_last: int = 10, keep_days: int = 7):
        """
        Clean up old backups, keeping the most recent ones
        
        Args:
            keep_last: Number of most recent backups to keep
            keep_days: Keep all backups from the last N days
        """
        if not self.metadata["backups"]:
            return
        
        # Sort backups by timestamp
        sorted_backups = sorted(
            self.metadata["backups"], 
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        # Determine cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        cutoff_timestamp = cutoff_date.strftime("%Y%m%d_%H%M%S")
        
        # Identify backups to keep
        backups_to_keep = []
        backups_to_delete = []
        
        for i, backup in enumerate(sorted_backups):
            if i < keep_last or backup["timestamp"] > cutoff_timestamp:
                backups_to_keep.append(backup)
            else:
                backups_to_delete.append(backup)
        
        # Delete old backups
        for backup in backups_to_delete:
            backup_path = Path(backup["path"])
            if backup_path.exists():
                backup_path.unlink()
                self.logger.info(f"Deleted old backup: {backup['filename']}")
        
        # Update metadata
        self.metadata["backups"] = backups_to_keep
        self._save_metadata()
        
        self.logger.info(f"Cleaned up {len(backups_to_delete)} old backups")
    
    def list_backups(self) -> List[Dict]:
        """List all available backups with their metadata"""
        return sorted(
            self.metadata["backups"], 
            key=lambda x: x["timestamp"],
            reverse=True
        )
    
    def get_latest_backup(self) -> Optional[Dict]:
        """Get information about the most recent backup"""
        if self.metadata["backups"]:
            return max(self.metadata["backups"], key=lambda x: x["timestamp"])
        return None
    
    def verify_backup(self, backup_name: str) -> bool:
        """
        Verify the integrity of a backup
        
        Args:
            backup_name: Name of the backup to verify
            
        Returns:
            True if backup is valid, False otherwise
        """
        # Find backup in metadata
        backup_info = None
        for backup in self.metadata["backups"]:
            if backup["filename"] == backup_name:
                backup_info = backup
                break
        
        if not backup_info:
            self.logger.error(f"Backup not found in metadata: {backup_name}")
            return False
        
        backup_path = Path(backup_info["path"])
        
        if not backup_path.exists():
            self.logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Verify checksum
        current_checksum = self._calculate_checksum(backup_path)
        stored_checksum = backup_info.get("checksum")
        
        if current_checksum == stored_checksum:
            self.logger.info(f"Backup verified: {backup_name}")
            return True
        else:
            self.logger.error(f"Backup corrupted: {backup_name}")
            return False


if __name__ == "__main__":
    # Test the backup manager
    logging.basicConfig(level=logging.INFO)
    
    manager = BackupManager()
    
    # Create a test backup
    print("Creating backup...")
    backup_path = manager.create_backup(tag="test", source_id=3)
    print(f"Backup created: {backup_path}")
    
    # List backups
    print("\nAvailable backups:")
    for backup in manager.list_backups():
        print(f"  - {backup['filename']} ({backup['size_bytes']} bytes)")
    
    # Verify the backup
    latest = manager.get_latest_backup()
    if latest:
        print(f"\nVerifying latest backup: {latest['filename']}")
        is_valid = manager.verify_backup(latest['filename'])
        print(f"Backup valid: {is_valid}")