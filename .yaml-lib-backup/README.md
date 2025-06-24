# YAML-LIB Backup Directory

This directory contains a complete backup of the `dhafnck_mcp_main/yaml-lib` agent configuration files.

## 📁 What's Backed Up

This backup preserves all critical agent configuration files from the main yaml-lib directory:

- **Agent Definitions** (`*_agent/job_desc.yaml`) - Core agent roles and capabilities
- **Context Files** (`contexts/*.yaml`) - Agent instructions and specifications  
- **Rules** (`rules/*.yaml`) - Behavioral rules and error handling
- **Output Formats** (`output_format/*.yaml`) - Response formatting specifications
- **Tools** (`tools/*.yaml`) - Tool configurations and capabilities

## 🎯 Purpose

This backup system protects against:
- ✅ Accidental file deletion during development
- ✅ Test interference with agent configurations
- ✅ Git operations that might affect yaml-lib
- ✅ System crashes or corruption
- ✅ Mistaken cleanup scripts

## 🔄 Backup Management

### Automatic Backup Creation
Backups are automatically created when you run:
```bash
./preserve_yaml_lib.sh protect
./preserve_yaml_lib.sh backup
```

### Manual Restore
If yaml-lib files are missing or corrupted:
```bash
./preserve_yaml_lib.sh restore
```

### Integrity Check
Verify backup and main directory sync:
```bash
./preserve_yaml_lib.sh check
```

## 📊 Directory Structure

```
.yaml-lib-backup/
├── README.md                           # This file
├── convert_json_to_yaml.py            # Utility scripts
├── convert_yaml_to_mdc_format.py      # Format converters
├── coding_agent/                      # Agent configurations
│   ├── job_desc.yaml                  # Agent definition
│   ├── contexts/                      # Context specifications
│   ├── rules/                         # Behavioral rules
│   ├── output_format/                 # Response formats
│   └── tools/                         # Tool configurations
├── devops_agent/                      # DevOps agent files
├── security_auditor_agent/            # Security agent files
└── [... all other *_agent directories]
```

## 🚨 Important Notes

### **DO NOT MODIFY FILES IN THIS DIRECTORY**
- This is a **read-only backup** for restoration purposes
- Modifications here will be overwritten on next backup
- Always edit files in the main `dhafnck_mcp_main/yaml-lib/` directory

### **Backup Sync**
- Backup is updated when protection script runs
- Not automatically synced with main directory changes
- Run `./preserve_yaml_lib.sh backup` after making changes

### **Git Tracking**
- This directory is intentionally **not tracked by Git**
- Prevents backup conflicts with version control
- Local protection mechanism only

## 🔧 Maintenance

### Regular Backup Updates
```bash
# After making changes to yaml-lib
./preserve_yaml_lib.sh backup
```

### Verify Backup Integrity
```bash
# Check if backup matches main directory
diff -r dhafnck_mcp_main/yaml-lib/ .yaml-lib-backup/
```

### Clean Old Backups (if needed)
```bash
# Only if disk space is a concern
rm -rf .yaml-lib-backup.old
```

## 🆘 Emergency Recovery

### If Main yaml-lib Directory is Deleted
```bash
./preserve_yaml_lib.sh restore
```

### If Backup is Corrupted
1. Check Git history: `git log --oneline -- dhafnck_mcp_main/yaml-lib/`
2. Restore from Git: `git checkout HEAD~1 -- dhafnck_mcp_main/yaml-lib/`
3. Create new backup: `./preserve_yaml_lib.sh backup`

### If Both Main and Backup are Lost
1. Check previous branches: `git branch -a`
2. Restore from branch: `git checkout v1 -- cursor_agent/yaml-lib`
3. Copy to correct location: `cp -r cursor_agent/yaml-lib/* dhafnck_mcp_main/yaml-lib/`
4. Create backup: `./preserve_yaml_lib.sh backup`

## 📈 Backup Statistics

- **Created**: $(date)
- **Agent Count**: $(find . -name "*_agent" -type d | wc -l) agents
- **YAML Files**: $(find . -name "*.yaml" -type f | wc -l) configuration files
- **Total Size**: $(du -sh . | cut -f1) of agent configurations

## 🔗 Related Files

- **Protection Script**: `../preserve_yaml_lib.sh` - Main protection tool
- **Git Hook**: `../.git/hooks/pre-commit` - Prevents accidental commits
- **Main Directory**: `../dhafnck_mcp_main/yaml-lib/` - Active agent configs

## 📝 Version Info

- **Backup Format**: Complete directory mirror
- **Sync Method**: `rsync -av --delete`
- **Restore Method**: `rsync -av --delete` (reverse)
- **Protection Level**: Local filesystem backup

---

**🛡️ This backup ensures your agent configurations are always recoverable!**

For more information, run: `./preserve_yaml_lib.sh help`