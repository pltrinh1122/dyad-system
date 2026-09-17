# Backup System Operations Guide

## Overview

This guide covers comprehensive backup strategies for system protection, including:
- **Snapshots** (quick recovery from configuration errors)
- **External Backups** (disaster recovery from hardware failure)
- **Best Practices** for both approaches

## Timeshift Commands Quick Reference

```bash
# List all snapshots
sudo timeshift --list

# Create snapshot with description
sudo timeshift --create --comments "Before system update"

# Create snapshot (uses default comments)
sudo timeshift --create

# Restore specific snapshot by name
sudo timeshift --restore --snapshot 2025-10-14_17-27-42

# Restore latest snapshot
sudo timeshift --restore

# Delete specific snapshot
sudo timeshift --delete --snapshot 2025-10-14_17-27-42

# GUI Interface (Recommended for visual confirmation)
sudo timeshift-gtk

# View configuration
sudo cat /etc/timeshift/timeshift.json

# Edit configuration
sudo nano /etc/timeshift/timeshift.json

# Check snapshot space usage
sudo btrfs filesystem du /timeshift/snapshots/

# Before Major System Update workflow:
# 1. Create snapshot
sudo timeshift --create --comments "Before apt upgrade $(date +%Y%m%d)"

# 2. Perform update
sudo apt update && sudo apt upgrade

# 3. If something breaks, restore:
# sudo timeshift --restore --snapshot <snapshot-name>
```

> **Note**: Timeshift can be configured for automatic cleanup. See full configuration section below.

## Understanding Backup Layers

### Layer 1: Snapshots (Quick Recovery)
- **Purpose**: Rapid recovery from configuration errors, software updates, or accidental changes
- **Technology**: Btrfs snapshots (or similar filesystem snapshots)
- **Recovery Time**: Minutes to hours
- **Protection Scope**: 
  - ✅ System configuration errors
  - ✅ Software update issues
  - ✅ Accidental file deletion/modification
  - ✅ Quick rollback needs

### Layer 2: External Backups (Disaster Recovery)
- **Purpose**: Complete system recovery from hardware failure, corruption, or catastrophic events
- **Technology**: External storage, cloud backup, or network storage
- **Recovery Time**: Hours to days
- **Protection Scope**:
  - ✅ Hardware failure
  - ✅ Disk corruption
  - ✅ Fire/flood/theft
  - ✅ Complete system loss
  - ✅ Filesystem corruption

### Why You Need Both

```
┌─────────────────────────────────────┐
│     External Backups                │
│  (Disaster Recovery Layer)          │
│  - Protects against hardware        │
│    failure, theft, disasters        │
└─────────────────────────────────────┘
              ↑
              │ Complements
              │
┌─────────────────────────────────────┐
│     Snapshots                       │
│  (Quick Recovery Layer)             │
│  - Protects against config errors,  │
│    updates, accidental changes      │
└─────────────────────────────────────┘
```

**Snapshots are NOT backups** - they're part of a comprehensive backup strategy.

## Snapshot Management (Quick Recovery)

### Recommended Tool: Timeshift

Timeshift provides automated snapshot management for Btrfs systems.

#### Installation
```bash
# Ubuntu/Debian
sudo apt install timeshift

# Or use package manager
```

#### Configuration

**GUI Setup** (Recommended):
```bash
sudo timeshift-gtk
```

Configure:
- **Schedule**: Hourly, daily, weekly, monthly snapshots
- **Retention**: How many snapshots to keep
- **Location**: `/timeshift/snapshots/` (default)
- **Include/Exclude**: What to snapshot

**Recommended Exclusions** (to save space and avoid unnecessary files):
- `/tmp/*` - Temporary files (cleared on boot)
- `/var/tmp/*` - Persistent temporary files (should NOT be in snapshots)
- `/var/log/*` - System and application logs (should NOT be in snapshots)
- `/var/cache/*` - Application caches
- `/var/run/*` - Runtime files
- `/var/lock/*` - Lock files
- `/proc/*`, `/sys/*`, `/dev/*` - Virtual filesystems
- `/mnt/*`, `/media/*` - Mounted drives
- `/lost+found` - Filesystem recovery directory
- `/timeshift/*` - Avoid snapshotting snapshots

**CLI Configuration**:
```bash
# View current exclusion list
sudo cat /etc/timeshift/timeshift.json | jq '.exclude'

# View full config
sudo cat /etc/timeshift/timeshift.json

# Edit config (if needed)
sudo nano /etc/timeshift/timeshift.json
```

**Where exclusion list is maintained:**
- **Location**: `/etc/timeshift/timeshift.json`
- **Section**: `"exclude"` array in the JSON configuration
- **GUI Method**: Configure via `sudo timeshift-gtk` → Settings → Filters → Exclude patterns
- **CLI Method**: Edit `/etc/timeshift/timeshift.json` directly

> **Note**: Timeshift automatically excludes virtual filesystems (`/proc`, `/sys`, `/dev`) and mounted drives in Btrfs mode, but it's good practice to be explicit. For rsync mode, these exclusions are essential.

**Why exclude `/var/tmp/` and `/var/log/`?**
- **`/var/tmp/`**: Contains temporary files that change frequently; not needed for system recovery; wastes snapshot space
- **`/var/log/`**: Logs change very frequently and can grow large; not critical for system recovery (you restore system state, not log history); including them wastes significant snapshot space; can be backed up separately if needed for forensic purposes

#### Common Operations

```bash
# Manual snapshot before major changes:
sudo timeshift --create --comments "Before system update"

# Or use GUI (easier and safer)


# List Snapshots:
timeshift --list


# Restore specific snapshot:
sudo timeshift --restore --snapshot 2025-10-14_17-27-42

# Or use GUI (recommended - safer with visual confirmation)


# Delete Snapshot:
sudo timeshift --delete --snapshot 2025-10-14_17-27-42
```

#### Best Practices

1. **Create Snapshots Before Major Changes**
   - System updates (`apt upgrade`)
   - Configuration changes
   - Package installations
   - Major software updates

2. **Automated Snapshots**
   - Configure Timeshift for automatic snapshots
   - Hourly for recent changes
   - Daily for regular backups
   - Weekly/monthly for long-term retention

3. **Monitor Disk Space**
   ```bash
   # Check filesystem usage
   df -h /
   
   # Check snapshot space
   sudo btrfs filesystem du /timeshift/snapshots/
   ```

4. **Regular Cleanup**
   - Timeshift handles this automatically (if configured)
   - Or manually delete old snapshots:
     ```bash
     sudo timeshift --delete --snapshot <old-snapshot>
     ```


## External Backup Management (Disaster Recovery)

### Backup Types

#### 1. Full System Backup
- Complete system image
- Includes OS, applications, data
- Large size, slow to create/restore
- Best for: Complete system recovery

#### 2. Incremental Backup
- Only changed files since last backup
- Smaller size, faster to create
- Requires base backup + increments
- Best for: Regular scheduled backups

#### 3. File-Level Backup
- Individual files and directories
- Selective backup/restore
- Flexible but slower
- Best for: Data protection

### Backup Tools

#### rsync (Recommended for Linux)
- **Pros**: Native Linux, flexible, efficient
- **Cons**: Command-line only, requires scripting
- **Best for**: File-level backups, incremental backups

**Example**:
```bash
# Full system backup
sudo rsync -aAXv --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found"} / /backup/

# Incremental backup
sudo rsync -aAXv --link-dest=/backup/last-backup / /backup/backup-$(date +%Y%m%d)
```

#### Timeshift (Can Use rsync Mode)
- **Pros**: GUI + CLI, automated scheduling
- **Cons**: GUI dependencies (for CLI too)
- **Best for**: System backups with GUI management

**Configuration**:
- Can use rsync mode instead of Btrfs snapshots
- Useful for non-Btrfs filesystems
- See Timeshift GUI for configuration

#### Dedicated Backup Tools
- **Borg Backup**: Deduplication, compression, encryption
- **Restic**: Encrypted, deduplicated backups
- **Duplicity**: Encrypted backups with cloud support
- **BackInTime**: GUI-based rsync frontend

### Backup Locations

#### 1. External USB Drive
- **Pros**: Portable, offline, fast
- **Cons**: Physical security, can be lost
- **Best for**: Local backups, quick recovery

**Setup**:
```bash
# Mount external drive
sudo mkdir -p /mnt/backup
sudo mount /dev/sdX1 /mnt/backup

# Backup
sudo rsync -aAXv / /mnt/backup/system-backup-$(date +%Y%m%d)
```

#### 2. Network Storage (NAS)
- **Pros**: Centralized, accessible from multiple systems
- **Cons**: Network dependency, initial setup
- **Best for**: Multiple systems, centralized backup

**Setup**:
```bash
# Mount NFS/SMB share
sudo mount -t nfs nas:/backups /mnt/backup

# Backup
sudo rsync -aAXv / /mnt/backup/system-backup-$(date +%Y%m%d)
```

#### 3. Cloud Storage
- **Pros**: Off-site, automated, scalable
- **Cons**: Cost, bandwidth, privacy concerns
- **Best for**: Off-site backup, disaster recovery

**Options**:
- AWS S3, Google Cloud Storage
- BackBlaze B2, Wasabi
- Nextcloud, OwnCloud (self-hosted)

#### 4. Secondary Internal Drive
- **Pros**: Fast, always available
- **Cons**: Not protected from hardware failure
- **Best for**: Quick recovery, not disaster recovery

## Comprehensive Backup Strategy

### Recommended Approach

#### Daily Operations (Snapshots)
- **Automated**: Timeshift creates snapshots automatically
- **Manual**: Create snapshots before major changes
- **Location**: `/timeshift/snapshots/` (Btrfs snapshots)
- **Retention**: Keep 7-30 days of snapshots

#### Weekly Operations (External Backup)
- **Full Backup**: Complete system backup to external drive
- **Location**: External USB drive or network storage
- **Retention**: Keep 4-12 weeks of backups

#### Monthly Operations (Archive Backup)
- **Archive Backup**: Long-term backup to cloud or separate storage
- **Location**: Cloud storage or separate external drive
- **Retention**: Keep 6-12 months of monthly backups

### Example Workflow

```bash
# Daily (automated by Timeshift)
# - Hourly snapshots (last 24 hours)
# - Daily snapshots (last 7 days)
# - Weekly snapshots (last 4 weeks)

# Weekly (manual or scripted)
#!/bin/bash
# weekly-backup.sh
BACKUP_DIR="/mnt/external-backup/weekly"
DATE=$(date +%Y%m%d)

# Create full system backup
sudo rsync -aAXv \
  --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found","/timeshift/*"} \
  / "$BACKUP_DIR/system-backup-$DATE"

# Cleanup old backups (keep last 12 weeks)
find "$BACKUP_DIR" -name "system-backup-*" -mtime +84 -delete

# Monthly (manual or scripted)
# Upload to cloud storage or archive to separate drive
```

## Backup Verification

### Verify Snapshots
```bash
# List snapshots
timeshift --list

# Test restore (in dry-run or test environment)
# Verify snapshot integrity
sudo btrfs scrub start /
```

### Verify External Backups
```bash
# Test restore from backup
# Restore to test directory
sudo rsync -aAXv /backup/system-backup-20251104 /test-restore/

# Verify file integrity
diff -r / /test-restore

# Check backup completeness
du -sh /backup/system-backup-*
```

## Recovery Procedures

### Quick Recovery (Snapshots)

**Scenario**: System update broke something

```bash
# 1. List available snapshots
timeshift --list

# 2. Restore snapshot from before update
sudo timeshift --restore --snapshot 2025-11-04_10-00-00

# 3. Reboot and verify
```

### Disaster Recovery (External Backup)

**Scenario**: Hard drive failure

```bash
# 1. Boot from live USB
# 2. Mount new drive
sudo mount /dev/sdX1 /mnt/new-root

# 3. Restore from backup
sudo rsync -aAXv /backup/system-backup-20251104/* /mnt/new-root/

# 4. Reinstall GRUB
sudo grub-install --root-directory=/mnt/new-root /dev/sdX
sudo update-grub

# 5. Reboot
```

## Best Practices Summary

### Snapshots
- Create before major changes
- Use automated scheduling (Timeshift)
- Monitor di✅site (3-2-1 rule: 3 copies, 2 different media, 1 off-site)
- Verify backups (test restore)
- Encrypt sensitive data
- Document recovery procedures

### Both
- Test restore procedures
- Monitor backup health
- Document backup strategy
- Review and update regularly

## 3-2-1 Backup Rule

**Industry Standard**:
- **3 copies** of your data
- **2 different media types** (e.g., local drive + cloud)
- **1 off-site** backup

**Example**:
1. **Primary**: Live system (with snapshots)
2. **Local Backup**: External USB drive (weekly)
3. **Off-site Backup**: Cloud storage (monthly)

## Monitoring and Maintenance

### Regular Tasks

#### Daily
- Check snapshot status (automated)
- Monitor disk space

#### Weekly
- Create external backup
- Verify backup integrity
- Cleanup old backups

#### Monthly
- Archive backup to off-site
- Review backup strategy
- Test restore procedure
- Run filesystem scrub: `sudo btrfs scrub start /`

### Disk Space Monitoring

```bash
# Check filesystem usage
df -h /

# Check snapshot space
sudo btrfs filesystem du /timeshift/snapshots/

# Check backup space
du -sh /backup/*
```

## Troubleshooting

### Issue: Disk Space Full

**Snapshots**:
```bash
# List snapshots
timeshift --list

# Delete old snapshots
sudo timeshift --delete --snapshot <old-snapshot>
```

**External Backups**:
```bash
# Check backup size
du -sh /backup/*

# Delete old backups
rm -rf /backup/system-backup-20251001
```

### Issue: Backup Fails

**Check**:
- Disk space: `df -h`
- Permissions: `ls -la /backup`
- Network connectivity (for network backups)
- Backup media health

### Issue: Restore Fails

**Check**:
- Backup integrity: Test restore to test directory
- Disk space for restore
- Permissions on backup files
- Backup media corruption

## Tools and Resources

### Snapshot Tools
- **Timeshift**: Recommended (GUI + CLI)
- **btrsnap.sh**: Alternative (headless, custom)
- **Snapper**: SUSE/OpenSUSE standard

### Backup Tools
- **rsync**: Native Linux, flexible
- **Borg Backup**: Deduplication, encryption
- **Restic**: Encrypted, deduplicated
- **Duplicity**: Cloud integration
- **BackInTime**: GUI rsync frontend

### Documentation
- `btrfs-op/BTRFS_SNAPSHOT_BEST_PRACTICES.md` - Snapshot best practices
- `btrfs-op/BTRFS_SNAPSHOTS_VS_TIMESHIFT.md` - Tool comparison
- `btrfs-op/BTRSNAP_VALUE_ASSESSMENT.md` - Tool selection guide

## References

- Btrfs Documentation: https://btrfs.readthedocs.io/
- Timeshift Documentation: https://github.com/linuxmint/timeshift
- rsync Documentation: `man rsync`
- Arch Linux Backup Guide: https://wiki.archlinux.org/title/Backup_programs
- 3-2-1 Backup Rule: https://www.backblaze.com/blog/the-3-2-1-backup-strategy/

---

**Last Updated**: November 4, 2025  
**Related Documents**:
- `btrfs-op/BTRFS_SNAPSHOT_BEST_PRACTICES.md`
- `btrfs-op/BTRFS_SNAPSHOTS_VS_TIMESHIFT.md`
- `btrfs-op/BTRSNAP_VALUE_ASSESSMENT.md`

