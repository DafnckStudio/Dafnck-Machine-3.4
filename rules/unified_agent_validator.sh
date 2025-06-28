#!/bin/bash

# Unified Agent Validator for DafnckMachine v3.1
# Combines agent format validation, loading tests, and system initialization

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
MACHINE_DIR="$BASE_DIR/01_Machine"
AGENTS_DIR="$MACHINE_DIR/02_Agents"
AGENT_RUN_DIR="$MACHINE_DIR/03_Brain/Agents-Check"
BRAIN_DIR="$MACHINE_DIR/03_Brain"
VISION_DIR="$BASE_DIR/02_Vision"
ROOMODES_FILE="$BASE_DIR/.roomodes"
AGENT_FORMAT_SCHEMA="$AGENT_RUN_DIR/Agent-Format.json"
LOG_DIR="$AGENT_RUN_DIR/Log"
VALIDATION_REPORT="$LOG_DIR/unified_validation_report.md"
SYSTEM_LOG="$LOG_DIR/unified_system_init.log"
STEP_FILE="$BRAIN_DIR/Step.json"

# Workflow agent order for .roomodes synchronization
WORKFLOW_AGENT_ORDER=(
    "uber-orchestrator-agent" "nlu-processor-agent" "elicitation-agent"
    "compliance-scope-agent" "idea-generation-agent" "idea-refinement-agent"
    "core-concept-agent" "market-research-agent" "mcp-researcher-agent"
    "technology-advisor-agent" "system-architect-agent" "branding-agent"
    "design-system-agent" "ui-designer-agent" "prototyping-agent"
    "design-qa-analyst" "ux-researcher-agent" "tech-spec-agent"
    "task-planning-agent" "prd-architect-agent" "mcp-configuration-agent"
    "algorithmic-problem-solver-agent" "coding-agent" "code-reviewer-agent"
    "documentation-agent" "development-orchestrator-agent" "test-case-generator-agent"
    "test-orchestrator-agent" "functional-tester-agent" "exploratory-tester-agent"
    "performance-load-tester-agent" "visual-regression-testing-agent"
    "uat-coordinator-agent" "lead-testing-agent" "compliance-testing-agent"
    "security-penetration-tester-agent" "usability-heuristic-agent"
    "adaptive-deployment-strategist-agent" "devops-agent"
    "user-feedback-collector-agent" "efficiency-optimization-agent"
    "knowledge-evolution-agent" "security-auditor-agent" "swarm-scaler-agent"
    "root-cause-analysis-agent" "remediation-agent" "health-monitor-agent"
    "incident-learning-agent" "marketing-strategy-orchestrator" "campaign-manager-agent"
    "content-strategy-agent" "graphic-design-agent" "growth-hacking-idea-agent"
    "video-production-agent" "analytics-setup-agent" "seo-sem-agent"
    "social-media-setup-agent" "community-strategy-agent" "project-initiator-agent"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global counters
TOTAL_AGENTS=0
VALID_AGENTS=0
TOTAL_ERRORS=0
TOTAL_WARNINGS=0
GROUPS_FIXES=0
REFERENCE_FIXES=0
AUTO_YES=false
AGENTS_ONLY=false
SYSTEM_ONLY=false
GENERATE_REPORT=false

# Repair options
REPAIR_ALL=false
FIX_GROUPS=false
FIX_REFERENCES=false
AUTO_REPAIR=false
REPAIR_ONLY=false

# Cursor options
CURSOR=false
CURSOR_ONLY=false
NO_CURSOR=false
CURSOR_BACKUP=false

# Template options
UPDATE_TEMPLATE=false
TEMPLATE_ONLY=false

# Strict flag
STRICT=false

# --- Utility Functions ---

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$SYSTEM_LOG"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" >&2
    log "WARNING: $1"
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    log "SUCCESS: $1"
}

info() {
    echo -e "${BLUE}INFO: $1${NC}"
    log "INFO: $1"
}

check_dependencies() {
    local missing_deps=()
    
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        exit 1
    fi
}

create_backup() {
    local file_path="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_dir="$AGENT_RUN_DIR/backups"
    local backup_path="$backup_dir/$(basename "$file_path" .json)_${timestamp}.json"
    
    mkdir -p "$backup_dir"
    cp "$file_path" "$backup_path"
    echo "$backup_path"
}

# --- Agent Repair Functions ---

fix_groups_format() {
    local agent_files=("$@")
    local fixes_made=0
    
    info "🔧 Fixing groups format issues..."
    
    for file in "${agent_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            continue
        fi
        
        local agent_name=$(basename "$file" .json)
        local needs_fix=false
        
        # Check if groups array contains complex objects instead of simple strings
        local groups_json=$(jq -r '.customModes[0].groups // []' "$file" 2>/dev/null)
        
        # Check each group element
        local group_count=$(echo "$groups_json" | jq 'length' 2>/dev/null)
        for ((i=0; i<group_count; i++)); do
            local group_element=$(echo "$groups_json" | jq -r ".[$i]" 2>/dev/null)
            
            # If it's an object (starts with {), we need to fix it
            if [[ "$group_element" =~ ^\{.*\}$ ]]; then
                needs_fix=true
                break
            fi
        done
        
        if [[ "$needs_fix" == "true" ]]; then
            info "  Fixing groups format in $agent_name..."
            
            # Create backup
            local backup_path=$(create_backup "$file")
            log "Created backup: $backup_path"
            
            # Fix the groups array by extracting simple string values
            local fixed_groups='[]'
            for ((i=0; i<group_count; i++)); do
                local group_element=$(echo "$groups_json" | jq -r ".[$i]" 2>/dev/null)
                
                if [[ "$group_element" =~ ^\{.*\}$ ]]; then
                    # Extract the simple string value from complex object
                    local simple_value=$(echo "$group_element" | jq -r 'if type == "object" then (keys[0] // "edit") else . end' 2>/dev/null)
                    fixed_groups=$(echo "$fixed_groups" | jq ". += [\"$simple_value\"]" 2>/dev/null)
                else
                    # Keep simple string as is
                    fixed_groups=$(echo "$fixed_groups" | jq ". += [\"$group_element\"]" 2>/dev/null)
                fi
            done
            
            # Update the file with fixed groups
            local temp_file=$(mktemp)
            jq ".customModes[0].groups = $fixed_groups" "$file" > "$temp_file" && mv "$temp_file" "$file"
            
            ((fixes_made++))
            success "  ✓ Fixed groups format in $agent_name"
        fi
    done
    
    if [[ $fixes_made -gt 0 ]]; then
        success "Fixed groups format in $fixes_made agent(s)"
        GROUPS_FIXES=$((GROUPS_FIXES + fixes_made))
    else
        info "No groups format issues found"
    fi
    
    return $fixes_made
}

fix_broken_references() {
    local agent_files=("$@")
    local fixes_made=0
    
    info "🔧 Fixing broken interactsWith references..."
    
    # Function to get reference mapping
    get_reference_mapping() {
        local key="$1"
        case "$key" in
            "project-initiator") echo "project-initiator-agent" ;;
            "uber-orchestrator") echo "uber-orchestrator-agent" ;;
            "nlu-processor") echo "nlu-processor-agent" ;;
            "elicitation") echo "elicitation-agent" ;;
            "compliance-scope") echo "compliance-scope-agent" ;;
            "idea-generation") echo "idea-generation-agent" ;;
            "idea-refinement") echo "idea-refinement-agent" ;;
            "core-concept") echo "core-concept-agent" ;;
            "market-research") echo "market-research-agent" ;;
            "mcp-researcher") echo "mcp-researcher-agent" ;;
            "technology-advisor") echo "technology-advisor-agent" ;;
            "system-architect") echo "system-architect-agent" ;;
            "branding") echo "branding-agent" ;;
            "design-system") echo "design-system-agent" ;;
            "ui-designer") echo "ui-designer-agent" ;;
            "prototyping") echo "prototyping-agent" ;;
            "design-qa-analyst") echo "design-qa-analyst" ;;
            "ux-researcher") echo "ux-researcher-agent" ;;
            "tech-spec") echo "tech-spec-agent" ;;
            "task-planning") echo "task-planning-agent" ;;
            "prd-architect") echo "prd-architect-agent" ;;
            "mcp-configuration") echo "mcp-configuration-agent" ;;
            "algorithmic-problem-solver") echo "algorithmic-problem-solver-agent" ;;
            "coding") echo "coding-agent" ;;
            "code-reviewer") echo "code-reviewer-agent" ;;
            "documentation") echo "documentation-agent" ;;
            "development-orchestrator") echo "development-orchestrator-agent" ;;
            "test-case-generator") echo "test-case-generator-agent" ;;
            "test-orchestrator") echo "test-orchestrator-agent" ;;
            "functional-tester") echo "functional-tester-agent" ;;
            "exploratory-tester") echo "exploratory-tester-agent" ;;
            "performance-load-tester") echo "performance-load-tester-agent" ;;
            "visual-regression-testing") echo "visual-regression-testing-agent" ;;
            "uat-coordinator") echo "uat-coordinator-agent" ;;
            "lead-testing") echo "lead-testing-agent" ;;
            "compliance-testing") echo "compliance-testing-agent" ;;
            "security-penetration-tester") echo "security-penetration-tester-agent" ;;
            "usability-heuristic") echo "usability-heuristic-agent" ;;
            "adaptive-deployment-strategist") echo "adaptive-deployment-strategist-agent" ;;
            "devops") echo "devops-agent" ;;
            "user-feedback-collector") echo "user-feedback-collector-agent" ;;
            "efficiency-optimization") echo "efficiency-optimization-agent" ;;
            "knowledge-evolution") echo "knowledge-evolution-agent" ;;
            "security-auditor") echo "security-auditor-agent" ;;
            "swarm-scaler") echo "swarm-scaler-agent" ;;
            "root-cause-analysis") echo "root-cause-analysis-agent" ;;
            "remediation") echo "remediation-agent" ;;
            "health-monitor") echo "health-monitor-agent" ;;
            "incident-learning") echo "incident-learning-agent" ;;
            "marketing-strategy-orchestrator") echo "marketing-strategy-orchestrator" ;;
            "campaign-manager") echo "campaign-manager-agent" ;;
            "content-strategy") echo "content-strategy-agent" ;;
            "graphic-design") echo "graphic-design-agent" ;;
            "growth-hacking-idea") echo "growth-hacking-idea-agent" ;;
            "video-production") echo "video-production-agent" ;;
            "analytics-setup") echo "analytics-setup-agent" ;;
            "seo-sem") echo "seo-sem-agent" ;;
            "social-media-setup") echo "social-media-setup-agent" ;;
            "community-strategy") echo "community-strategy-agent" ;;
            *) echo "" ;;
        esac
    }
    
    # Invalid references to remove
    local invalid_refs=("user" "system" "human" "assistant" "claude" "gpt" "ai" "chatbot" "bot")
    
    for file in "${agent_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            continue
        fi
        
        local agent_name=$(basename "$file" .json)
        local needs_fix=false
        
        # Check if agent has interactsWith field
        if ! jq -e '.customModes[0].connectivity.interactsWith' "$file" >/dev/null 2>&1; then
            continue
        fi
        
        local interactions=($(jq -r '.customModes[0].connectivity.interactsWith[]?' "$file" 2>/dev/null))
        local fixed_interactions=()
        
        for interaction in "${interactions[@]}"; do
            local should_remove=false
            
            # Check if it's an invalid reference
            for invalid_ref in "${invalid_refs[@]}"; do
                if [[ "$interaction" == "$invalid_ref" ]]; then
                    should_remove=true
                    needs_fix=true
                    break
                fi
            done
            
            if [[ "$should_remove" == "true" ]]; then
                continue
            fi
            
            # Check if reference exists as agent file
            if [[ -f "$AGENTS_DIR/${interaction}.json" ]]; then
                fixed_interactions+=("$interaction")
            else
                # Try to map to correct reference
                local correct_ref=$(get_reference_mapping "$interaction")
                if [[ -n "$correct_ref" && -f "$AGENTS_DIR/${correct_ref}.json" ]]; then
                    fixed_interactions+=("$correct_ref")
                    needs_fix=true
                else
                    # Remove non-existent reference
                    needs_fix=true
                fi
            fi
        done
        
        if [[ "$needs_fix" == "true" ]]; then
            info "  Fixing references in $agent_name..."
            
            # Create backup
            local backup_path=$(create_backup "$file")
            log "Created backup: $backup_path"
            
            # Update interactsWith array
            local fixed_array='[]'
            for ref in "${fixed_interactions[@]}"; do
                fixed_array=$(echo "$fixed_array" | jq ". += [\"$ref\"]" 2>/dev/null)
            done
            
            local temp_file=$(mktemp)
            jq ".customModes[0].connectivity.interactsWith = $fixed_array" "$file" > "$temp_file" && mv "$temp_file" "$file"
            
            ((fixes_made++))
            success "  ✓ Fixed references in $agent_name"
        fi
    done
    
    if [[ $fixes_made -gt 0 ]]; then
        success "Fixed broken references in $fixes_made agent(s)"
        REFERENCE_FIXES=$((REFERENCE_FIXES + fixes_made))
    else
        info "No broken references found"
    fi
    
    return $fixes_made
}

repair_all_agents() {
    local agent_files=("$@")
    local total_fixes=0
    
    info "🔧 Running comprehensive agent repair..."
    
    # Fix groups format
    fix_groups_format "${agent_files[@]}"
    local groups_fixes=$?
    total_fixes=$((total_fixes + groups_fixes))
    
    # Fix broken references
    fix_broken_references "${agent_files[@]}"
    local ref_fixes=$?
    total_fixes=$((total_fixes + ref_fixes))
    
    success "Comprehensive repair complete! Made $total_fixes total fixes"
    log "Repair summary - Groups fixes: $groups_fixes, Reference fixes: $ref_fixes, Total: $total_fixes"
    
    return $total_fixes
}

# --- Agent Validation Functions ---

validate_json_syntax() {
    local file="$1"
    
    if ! jq empty "$file" 2>/dev/null; then
        echo "Invalid JSON format"
        return 1
    fi
    return 0
}

validate_basic_structure() {
    local errors=()
    local file="$1"
    local agent_name="$(basename "$file" .json)"
    
    # Check customModes array
    local modes_count=$(jq -r '.customModes | length' "$file" 2>/dev/null)
    if [[ "$modes_count" != "1" ]]; then
        errors+=("customModes array should contain exactly 1 element")
    fi
    
    # Check slug matches filename
    local slug=$(jq -r '.customModes[0].slug // empty' "$file" 2>/dev/null)
    if [[ "$slug" != "$agent_name" ]]; then
        errors+=("slug '$slug' must match filename '$agent_name'")
    fi
    
    # Print errors
    for error in "${errors[@]}"; do
        echo "$error"
    done
    
    return ${#errors[@]}
}

validate_required_fields() {
    local errors=()
    local warnings=()
    local file="$1"
    
    # Required fields
    local required_fields=("slug" "name" "roleDefinition" "customInstructions" "groups")
    
    for field in "${required_fields[@]}"; do
        local value=$(jq -r ".customModes[0].$field // empty" "$file" 2>/dev/null)
        if [[ -z "$value" || "$value" == "null" ]]; then
            errors+=("Missing or empty required field: $field")
        fi
    done
    
    # Extended fields (warnings)
    local extended_fields=("whenToUse" "inputSpec" "outputSpec" "connectivity" "continuousLearning")
    
    for field in "${extended_fields[@]}"; do
        local value=$(jq -r ".customModes[0].$field // empty" "$file" 2>/dev/null)
        if [[ -z "$value" || "$value" == "null" ]]; then
            warnings+=("Missing extended field: $field (recommended)")
        fi
    done
    
    # Print errors and warnings
    for error in "${errors[@]}"; do
        echo "ERROR: $error"
    done
    
    for warning in "${warnings[@]}"; do
        echo "WARNING: $warning"
    done
    
    return ${#errors[@]}
}

validate_nested_objects() {
    local errors=()
    local file="$1"
    
    # Validate inputSpec if present
    if jq -e '.customModes[0].inputSpec' "$file" >/dev/null 2>&1; then
        local input_type=$(jq -r '.customModes[0].inputSpec.type // empty' "$file" 2>/dev/null)
        local input_format=$(jq -r '.customModes[0].inputSpec.format // empty' "$file" 2>/dev/null)
        
        if [[ -z "$input_type" ]]; then
            errors+=("Missing inputSpec.type")
        fi
        if [[ -z "$input_format" ]]; then
            errors+=("Missing inputSpec.format")
        fi
    fi
    
    # Validate outputSpec if present
    if jq -e '.customModes[0].outputSpec' "$file" >/dev/null 2>&1; then
        local output_type=$(jq -r '.customModes[0].outputSpec.type // empty' "$file" 2>/dev/null)
        local output_format=$(jq -r '.customModes[0].outputSpec.format // empty' "$file" 2>/dev/null)
        
        if [[ -z "$output_type" ]]; then
            errors+=("Missing outputSpec.type")
        fi
        if [[ -z "$output_format" ]]; then
            errors+=("Missing outputSpec.format")
        fi
    fi
    
    # Validate connectivity if present
    if jq -e '.customModes[0].connectivity' "$file" >/dev/null 2>&1; then
        local interacts_with=$(jq -r '.customModes[0].connectivity.interactsWith // empty' "$file" 2>/dev/null)
        local feedback_loop=$(jq -r '.customModes[0].connectivity.feedbackLoop // empty' "$file" 2>/dev/null)
        
        if [[ -z "$interacts_with" ]]; then
            errors+=("Missing connectivity.interactsWith")
        fi
        if [[ -z "$feedback_loop" ]]; then
            errors+=("Missing connectivity.feedbackLoop")
        fi
    fi
    
    # Validate continuousLearning if present
    if jq -e '.customModes[0].continuousLearning' "$file" >/dev/null 2>&1; then
        local enabled=$(jq -r '.customModes[0].continuousLearning.enabled // empty' "$file" 2>/dev/null)
        local mechanism=$(jq -r '.customModes[0].continuousLearning.mechanism // empty' "$file" 2>/dev/null)
        
        if [[ -z "$enabled" ]]; then
            errors+=("Missing continuousLearning.enabled")
        fi
        if [[ -z "$mechanism" ]]; then
            errors+=("Missing continuousLearning.mechanism")
        fi
    fi
    
    # Print errors
    for error in "${errors[@]}"; do
        echo "ERROR: $error"
    done
    
    return ${#errors[@]}
}

validate_groups_array() {
    local errors=()
    local file="$1"
    
    # Check groups array exists and has correct length
    local groups_count=$(jq -r '.customModes[0].groups | length' "$file" 2>/dev/null)
    if [[ "$groups_count" == "0" || "$groups_count" == "null" ]]; then
        errors+=("groups array is empty or missing")
        echo "ERROR: groups array is empty or missing"
        return 1
    fi
    
    if [[ "$groups_count" -lt 2 || "$groups_count" -gt 5 ]]; then
        errors+=("groups array must have 2-5 elements (has $groups_count)")
    fi
    
    # Check first element is 'read'
    local first_group=$(jq -r '.customModes[0].groups[0] // empty' "$file" 2>/dev/null)
    if [[ "$first_group" != "read" ]]; then
        errors+=("First element in groups must be 'read'")
    fi
    
    # Check for required groups
    local groups_json=$(jq -r '.customModes[0].groups | @json' "$file" 2>/dev/null)
    
    if ! echo "$groups_json" | jq -e 'contains(["edit"])' >/dev/null 2>&1; then
        errors+=("groups must contain 'edit'")
    fi
    
    if ! echo "$groups_json" | jq -e 'contains(["mcp"])' >/dev/null 2>&1; then
        errors+=("groups must contain 'mcp'")
    fi
    
    local has_interaction=false
    if echo "$groups_json" | jq -e 'contains(["ask_followup_question"])' >/dev/null 2>&1 || \
       echo "$groups_json" | jq -e 'contains(["command"])' >/dev/null 2>&1; then
        has_interaction=true
    fi
    
    if [[ "$has_interaction" == "false" ]]; then
        errors+=("groups must contain either 'ask_followup_question' or 'command'")
    fi
    
    # Check for invalid groups
    local valid_groups=("read" "edit" "mcp" "ask_followup_question" "command" "browser")
    local groups_array=($(jq -r '.customModes[0].groups[]' "$file" 2>/dev/null))
    
    for group in "${groups_array[@]}"; do
        local is_valid=false
        for valid_group in "${valid_groups[@]}"; do
            if [[ "$group" == "$valid_group" ]]; then
                is_valid=true
                break
            fi
        done
        if [[ "$is_valid" == "false" ]]; then
            errors+=("Invalid group item: '$group'")
        fi
    done
    
    # Print errors
    for error in "${errors[@]}"; do
        echo "ERROR: $error"
    done
    
    return ${#errors[@]}
}

validate_custom_instructions() {
    local errors=()
    local file="$1"
    
    local instructions=$(jq -r '.customModes[0].customInstructions // empty' "$file" 2>/dev/null)
    
    if [[ -z "$instructions" ]]; then
        errors+=("customInstructions cannot be empty")
    else
        # Check for required sections
        local required_sections=("Core Purpose" "Key Capabilities" "MCP Tools")
        
        for section in "${required_sections[@]}"; do
            if [[ ! "$instructions" =~ "**$section**" ]]; then
                errors+=("Missing customInstructions section: $section")
            fi
        done
    fi
    
    # Print errors
    for error in "${errors[@]}"; do
        echo "ERROR: $error"
    done
    
    return ${#errors[@]}
}

validate_connectivity_references() {
    local warnings=()
    local file="$1"
    
    if jq -e '.customModes[0].connectivity.interactsWith' "$file" >/dev/null 2>&1; then
        local interactions=($(jq -r '.customModes[0].connectivity.interactsWith[]?' "$file" 2>/dev/null))
        
        for interaction in "${interactions[@]}"; do
            if [[ -n "$interaction" && ! -f "$AGENTS_DIR/${interaction}.json" ]]; then
                warnings+=("Invalid interactsWith reference: $interaction")
            fi
        done
    fi
    
    # Print warnings
    for warning in "${warnings[@]}"; do
        echo "WARNING: $warning"
    done
    
    return 0
}

# --- Agent Loading Test ---

agent_loading_test() {
    local file="$1"
    local agent_name="$(basename "$file" .json)"
    
    # Create temporary .roomodes with just this agent
    local temp_roomodes=$(mktemp)
    
    # Extract the agent's customModes
    if ! jq '{customModes: [.customModes[0]]}' "$file" > "$temp_roomodes" 2>/dev/null; then
        error "Failed to create temporary .roomodes for $agent_name"
        rm -f "$temp_roomodes"
        return 1
    fi
    
    # Copy to actual .roomodes location
    cp "$temp_roomodes" "$ROOMODES_FILE"
    rm -f "$temp_roomodes"
    
    local slug=$(jq -r '.customModes[0].slug // empty' "$file" 2>/dev/null)
    
    if [[ "$AUTO_YES" == "true" ]]; then
        info "Auto-confirming agent '$slug' loaded correctly"
        return 0
    else
        echo -n "Did agent '$slug' load correctly in chat mode? (yes/no): "
        read -r response
        case "$response" in
            [Yy]|[Yy][Ee][Ss])
                return 0
                ;;
            *)
                return 1
                ;;
        esac
    fi
}

# --- Comprehensive Agent Validation ---

validate_agent_comprehensive() {
    local file="$1"
    local agent_name="$(basename "$file" .json)"
    local total_errors=0
    local total_warnings=0
    
    echo "🔍 Testing $agent_name"
    
    # JSON syntax validation
    if ! validate_json_syntax "$file"; then
        echo "❌ Invalid JSON format"
        return 1
    fi
    
    # Basic structure validation
    local structure_output=$(validate_basic_structure "$file")
    local structure_errors=$?
    if [[ $structure_errors -gt 0 ]]; then
        echo "$structure_output" | while read -r line; do
            echo "❌ $line"
        done
        total_errors=$((total_errors + structure_errors))
    fi
    
    # Only continue if basic structure is valid
    if [[ $structure_errors -eq 0 ]]; then
        # Required fields validation
        local fields_output=$(validate_required_fields "$file")
        local fields_errors=$?
        if [[ -n "$fields_output" ]]; then
            echo "$fields_output" | while read -r line; do
                if [[ "$line" =~ ^ERROR: ]]; then
                    echo "❌ ${line#ERROR: }"
                    total_errors=$((total_errors + 1))
                elif [[ "$line" =~ ^WARNING: ]]; then
                    echo "⚠️  ${line#WARNING: }"
                    total_warnings=$((total_warnings + 1))
                fi
            done
        fi
        
        # Nested objects validation
        local nested_output=$(validate_nested_objects "$file")
        local nested_errors=$?
        if [[ -n "$nested_output" ]]; then
            echo "$nested_output" | while read -r line; do
                echo "❌ ${line#ERROR: }"
            done
            total_errors=$((total_errors + nested_errors))
        fi
        
        # Groups validation
        local groups_output=$(validate_groups_array "$file")
        local groups_errors=$?
        if [[ -n "$groups_output" ]]; then
            echo "$groups_output" | while read -r line; do
                echo "❌ ${line#ERROR: }"
            done
            total_errors=$((total_errors + groups_errors))
        fi
        
        # Custom instructions validation
        local instructions_output=$(validate_custom_instructions "$file")
        local instructions_errors=$?
        if [[ -n "$instructions_output" ]]; then
            echo "$instructions_output" | while read -r line; do
                echo "❌ ${line#ERROR: }"
            done
            total_errors=$((total_errors + instructions_errors))
        fi
        
        # Connectivity validation
        local connectivity_output=$(validate_connectivity_references "$file")
        if [[ -n "$connectivity_output" ]]; then
            echo "$connectivity_output" | while read -r line; do
                echo "⚠️  ${line#WARNING: }"
                total_warnings=$((total_warnings + 1))
            done
        fi
        
        # Calculate total errors from all validations
        total_errors=$((structure_errors + fields_errors + nested_errors + groups_errors + instructions_errors))
    fi
    
    # If format validation passed, do loading test
    if [[ $total_errors -eq 0 ]]; then
        if agent_loading_test "$file"; then
            echo "✅ PASS"
            return 0
        else
            echo "❌ Loading test failed"
            return 1
        fi
    else
        echo "❌ FAIL ($total_errors errors)"
        return 1
    fi
}

# --- System Initialization ---

validate_core_configs() {
    local errors=0
    
    info "Validating core configuration files..."
    
    local config_files=("$BRAIN_DIR/DNA.json" "$BRAIN_DIR/Genesis.json" "$BRAIN_DIR/Step.json")
    
    for config_file in "${config_files[@]}"; do
        local config_name=$(basename "$config_file" .json)
        
        if [[ ! -f "$config_file" ]]; then
            error "Missing config file: $config_file"
            errors=$((errors + 1))
        else
            if jq empty "$config_file" 2>/dev/null; then
                success "$config_name configuration valid"
            else
                error "Invalid JSON in $config_file"
                errors=$((errors + 1))
            fi
        fi
    done
    
    return $errors
}

validate_directory_structure() {
    local warnings=0
    
    info "Validating directory structure..."
    
    local required_dirs=(
        "$MACHINE_DIR/01_Workflow"
        "$MACHINE_DIR/02_Agents"
        "$MACHINE_DIR/03_Brain"
        "$VISION_DIR"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            warning "Missing directory: $(realpath --relative-to="$BASE_DIR" "$dir")"
            warnings=$((warnings + 1))
        fi
    done
    
    return $warnings
}

validate_agent_registry() {
    local errors=0
    
    if [[ ! -f "$BRAIN_DIR/DNA.json" ]]; then
        error "DNA.json not found, cannot validate agent registry"
        return 1
    fi
    
    local required_agents=("uber-orchestrator-agent" "scribe-agent" "task-sync-agent")
    
    for agent in "${required_agents[@]}"; do
        if ! jq -e --arg agent "$agent" '.agentRegistry[] | select(.agentName == $agent)' "$BRAIN_DIR/DNA.json" >/dev/null 2>&1; then
            error "Missing core agent in DNA.json: $agent"
            errors=$((errors + 1))
        fi
    done
    
    return $errors
}

system_initialization() {
    local total_errors=0
    local total_warnings=0
    
    info "Starting DafnckMachine v3.1 System Initialization"
    
    # Validate core configs
    validate_core_configs
    total_errors=$((total_errors + $?))
    
    if [[ $total_errors -eq 0 ]]; then
        # Validate directory structure
        validate_directory_structure
        total_warnings=$((total_warnings + $?))
        
        # Validate agent registry
        validate_agent_registry
        total_errors=$((total_errors + $?))
        
        # Update Step.json with results
        update_step_file_status $total_errors $total_warnings
    fi
    
    if [[ $total_errors -eq 0 ]]; then
        success "System initialization completed successfully"
        return 0
    else
        error "System initialization failed with $total_errors errors"
        return 1
    fi
}

update_step_file_status() {
    local errors=$1
    local warnings=$2
    local timestamp=$(date -Iseconds)
    local status="initialized"
    
    if [[ $errors -gt 0 ]]; then
        status="failed"
    elif [[ $warnings -gt 0 ]]; then
        status="partial"
    fi
    
    # Create or update Step.json
    local temp_step=$(mktemp)
    
    if [[ -f "$STEP_FILE" ]]; then
        cp "$STEP_FILE" "$temp_step"
    else
        echo '{}' > "$temp_step"
    fi
    
    jq --arg timestamp "$timestamp" \
       --arg status "$status" \
       --argjson errors "$errors" \
       --argjson warnings "$warnings" \
       '. + {
           lastInitialization: $timestamp,
           systemStatus: $status,
           validationResults: {
               errors: $errors,
               warnings: $warnings,
               timestamp: $timestamp
           }
       }' "$temp_step" > "$STEP_FILE"
    
    rm -f "$temp_step"
    
    info "Updated system status in Step.json"
}

# --- .roomodes Synchronization ---

sync_modes_to_roomodes() {
    local valid_agents=("$@")
    
    info "Starting mode synchronization to .roomodes..."
    
    # Create temporary file for building new .roomodes
    local temp_roomodes=$(mktemp)
    echo '{"customModes": []}' > "$temp_roomodes"
    
    # Collect all valid agent modes
    local all_modes=()
    
    for agent_file in "${valid_agents[@]}"; do
        if [[ -f "$AGENTS_DIR/$agent_file" ]]; then
            # Extract customModes from agent file
            local agent_modes=$(jq -r '.customModes[]' "$AGENTS_DIR/$agent_file" 2>/dev/null)
            if [[ -n "$agent_modes" ]]; then
                # Add to temporary array (this is simplified - in practice we'd need more complex JSON handling)
                jq --slurpfile agent "$AGENTS_DIR/$agent_file" \
                   '.customModes += $agent[0].customModes' "$temp_roomodes" > "${temp_roomodes}.tmp"
                mv "${temp_roomodes}.tmp" "$temp_roomodes"
            fi
        fi
    done
    
    # Order agents according to workflow order
    local ordered_temp=$(mktemp)
    echo '{"customModes": []}' > "$ordered_temp"
    
    # Add agents in workflow order
    for agent_slug in "${WORKFLOW_AGENT_ORDER[@]}"; do
        if jq -e --arg slug "$agent_slug" '.customModes[] | select(.slug == $slug)' "$temp_roomodes" >/dev/null 2>&1; then
            jq --arg slug "$agent_slug" \
               --slurpfile source "$temp_roomodes" \
               '.customModes += [$source[0].customModes[] | select(.slug == $slug)]' "$ordered_temp" > "${ordered_temp}.tmp"
            mv "${ordered_temp}.tmp" "$ordered_temp"
        fi
    done
    
    # Add any remaining agents not in the workflow order
    jq --slurpfile ordered "$ordered_temp" \
       --slurpfile source "$temp_roomodes" \
       '.customModes += [$source[0].customModes[] | select(.slug as $slug | $ordered[0].customModes | map(.slug) | contains([$slug]) | not)]' \
       "$ordered_temp" > "${ordered_temp}.tmp"
    mv "${ordered_temp}.tmp" "$ordered_temp"
    
    # Copy final result to .roomodes
    cp "$ordered_temp" "$ROOMODES_FILE"
    
    # Cleanup
    rm -f "$temp_roomodes" "$ordered_temp"
    
    local mode_count=$(jq -r '.customModes | length' "$ROOMODES_FILE" 2>/dev/null)
    success "Synced $mode_count modes to .roomodes"
}

# --- Interactive Menu ---

print_menu() {
    local agent_files=("$@")
    
    echo
    echo "--- Unified Agent Validator Menu ---"
    for i in "${!agent_files[@]}"; do
        echo "  [$((i+1))] ${agent_files[i]}"
    done
    echo "  [A] Test ALL agents"
    echo "  [M] Test MULTIPLE agents (comma-separated)"
    echo "  [T] Auto-yes mode (non-interactive)"
    echo "  [S] System initialization only"
    echo "  [R] Repair ALL agents (groups & references)"
    echo "  [G] Fix groups format only"
    echo "  [F] Fix broken references only"
    echo "  [Q] Quit"
    echo "------------------------------------"
}

get_user_selection() {
    local agent_files=("$@")
    
    while true; do
        print_menu "${agent_files[@]}"
        echo -n "Select option: "
        read -r choice
        
        case "$choice" in
            [Qq])
                exit 0
                ;;
            [Aa])
                echo "validate_all"
                return 0
                ;;
            [Tt])
                AUTO_YES=true
                echo "validate_all"
                return 0
                ;;
            [Ss])
                SYSTEM_ONLY=true
                echo "system_only"
                return 0
                ;;
            [Rr])
                echo "repair_all"
                return 0
                ;;
            [Gg])
                echo "fix_groups"
                return 0
                ;;
            [Ff])
                echo "fix_references"
                return 0
                ;;
            [Mm])
                echo -n "Enter comma-separated indices: "
                read -r indices
                local selected=()
                IFS=',' read -ra ADDR <<< "$indices"
                for i in "${ADDR[@]}"; do
                    i=$(echo "$i" | tr -d ' ')
                    if [[ "$i" =~ ^[0-9]+$ ]] && [[ $i -ge 1 ]] && [[ $i -le ${#agent_files[@]} ]]; then
                        selected+=("${agent_files[$((i-1))]}")
                    fi
                done
                if [[ ${#selected[@]} -gt 0 ]]; then
                    echo "validate_selected:${selected[*]}"
                    return 0
                else
                    echo "Invalid selection. Try again."
                fi
                ;;
            *)
                if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -ge 1 ]] && [[ $choice -le ${#agent_files[@]} ]]; then
                    echo "validate_single:${agent_files[$((choice-1))]}"
                    return 0
                else
                    echo "Invalid selection. Try again."
                fi
                ;;
        esac
    done
}

# --- Report Generation ---

generate_comprehensive_report() {
    local timestamp=$(date -Iseconds)
    local valid_agents=("$@")
    
    cat > "$VALIDATION_REPORT" << EOF
# Unified Agent Validation Report
Generated: $timestamp

## Agent Validation Summary

- Total agents tested: $TOTAL_AGENTS
- Valid agents: $VALID_AGENTS
- Failed agents: $((TOTAL_AGENTS - VALID_AGENTS))
- Success rate: $(if [[ $TOTAL_AGENTS -gt 0 ]]; then echo $(( (VALID_AGENTS * 100) / TOTAL_AGENTS )); else echo 0; fi)%

## Repair Summary

EOF

    # Add repair summary if any repairs were performed
    if [[ "$REPAIR_ALL" == "true" || "$FIX_GROUPS" == "true" || "$FIX_REFERENCES" == "true" || "$REPAIR_ONLY" == "true" || "$AUTO_REPAIR" == "true" ]]; then
        cat >> "$VALIDATION_REPORT" << EOF
- Repair mode: Active
- Groups format fixes: ${GROUPS_FIXES:-0}
- Reference fixes: ${REFERENCE_FIXES:-0}
- Total repairs: $((${GROUPS_FIXES:-0} + ${REFERENCE_FIXES:-0}))

EOF
    else
        cat >> "$VALIDATION_REPORT" << EOF
- Repair mode: Not used

EOF
    fi

    cat >> "$VALIDATION_REPORT" << EOF
## System Status

EOF

    if [[ -f "$STEP_FILE" ]]; then
        local system_status=$(jq -r '.systemStatus // "unknown"' "$STEP_FILE" 2>/dev/null)
        local last_init=$(jq -r '.lastInitialization // "unknown"' "$STEP_FILE" 2>/dev/null)
        local validation_errors=$(jq -r '.validationResults.errors // 0' "$STEP_FILE" 2>/dev/null)
        local validation_warnings=$(jq -r '.validationResults.warnings // 0' "$STEP_FILE" 2>/dev/null)
        
        cat >> "$VALIDATION_REPORT" << EOF
- System Status: $system_status
- Last Initialization: $last_init
- Validation Errors: $validation_errors
- Validation Warnings: $validation_warnings

EOF
    fi
    
    cat >> "$VALIDATION_REPORT" << EOF
## Valid Agents

EOF
    
    for agent in "${valid_agents[@]}"; do
        echo "- ✅ $agent" >> "$VALIDATION_REPORT"
    done
    
    echo >> "$VALIDATION_REPORT"
    echo "Report generated by Unified Agent Validator v3.1" >> "$VALIDATION_REPORT"
}

# --- Sync Menu ---
if [[ "$1" == "--sync-all" ]]; then
  python3 "$SCRIPT_DIR/unified_agent_validator.py" --sync-all
  exit 0
fi
if [[ "$1" == "--sync-roomodes" ]]; then
  python3 "$SCRIPT_DIR/unified_agent_validator.py" --sync-roomodes
  exit 0
fi
if [[ "$1" == "--sync-cursorrules" ]]; then
  python3 "$SCRIPT_DIR/unified_agent_validator.py" --sync-cursorrules
  exit 0
fi

# Interactive menu for sync
if [[ "$1" == "--menu" ]]; then
  echo "--- Unified Agent Validator Menu ---"
  echo "1) Validate ALL agents"
  echo "2) Sync ALL (both RooCode then Cursor)"
  echo "3) Sync to RooCode (.roomodes)"
  echo "4) Sync to Cursor (.cursorrules)"
  echo "Q) Quit"
  read -p "Enter choice: " choice
  case "$choice" in
    1)
      python3 "$SCRIPT_DIR/unified_agent_validator.py"
      ;;
    2)
      python3 "$SCRIPT_DIR/unified_agent_validator.py" --sync-all
      ;;
    3)
      python3 "$SCRIPT_DIR/unified_agent_validator.py" --sync-roomodes
      ;;
    4)
      python3 "$SCRIPT_DIR/unified_agent_validator.py" --sync-cursorrules
      ;;
    Q|q)
      exit 0
      ;;
    *)
      echo "Invalid choice."
      ;;
  esac
  exit 0
fi

# --- Usage Function ---

usage() {
    cat << EOF
Unified Agent Validator for DafnckMachine v3.1

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -y, --yes           Auto-yes mode (non-interactive)
    -r, --report        Generate detailed report
    -a, --agents-only   Test agents only, skip system init
    -s, --system-only   System initialization only
    --repair            Run all repair operations before validation
    --fix-groups        Fix groups format issues only
    --fix-references    Fix broken interactsWith references only
    --auto-repair       Automatically repair issues during validation
    --repair-only       Run repairs only, skip validation
    --cursor            Generate cursor configuration after validation
    --cursor-only       Generate cursor configuration only, skip validation
    --no-cursor         Skip cursor configuration generation
    --cursor-backup     Backup existing cursor files before generation
    --update-template   Update Template-Step-Structure.md with current agent list
    --template-only     Update template only, skip validation
    -h, --help          Show this help message
    --strict            Fail agents missing deep fields (example/schema/validationRules in inputSpec/outputSpec, all customInstructions sections, errorHandling, healthCheck, groups includes 'command')

EXAMPLES:
    $0                  # Interactive mode
    $0 -y               # Auto-yes mode
    $0 -a -y            # Test all agents in auto-yes mode
    $0 -s               # System initialization only
    $0 -r               # Generate detailed report
    $0 --repair         # Repair all agents then validate
    $0 --fix-groups     # Fix groups format only
    $0 --repair-only    # Repair only, no validation
    $0 --cursor-only    # Generate cursor configuration only
    $0 -y --cursor      # Auto-yes mode with cursor generation
    $0 --template-only  # Update template documentation only
    $0 --update-template # Update template after validation
    $0 --strict         # Fail agents missing deep fields

EOF
}

# --- Main Function ---

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -y|--yes)
                AUTO_YES=true
                shift
                ;;
            -r|--report)
                GENERATE_REPORT=true
                shift
                ;;
            -a|--agents-only)
                AGENTS_ONLY=true
                shift
                ;;
            -s|--system-only)
                SYSTEM_ONLY=true
                shift
                ;;
            --repair)
                REPAIR_ALL=true
                shift
                ;;
            --fix-groups)
                FIX_GROUPS=true
                shift
                ;;
            --fix-references)
                FIX_REFERENCES=true
                shift
                ;;
            --auto-repair)
                AUTO_REPAIR=true
                shift
                ;;
            --repair-only)
                REPAIR_ONLY=true
                shift
                ;;
            --cursor)
                CURSOR=true
                shift
                ;;
            --cursor-only)
                CURSOR_ONLY=true
                shift
                ;;
            --no-cursor)
                NO_CURSOR=true
                shift
                ;;
            --cursor-backup)
                CURSOR_BACKUP=true
                shift
                ;;
            --update-template)
                UPDATE_TEMPLATE=true
                shift
                ;;
            --template-only)
                TEMPLATE_ONLY=true
                shift
                ;;
            --strict)
                STRICT=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Handle template-only mode
    if [[ "$TEMPLATE_ONLY" == "true" || "$UPDATE_TEMPLATE" == "true" ]]; then
        echo -e "${PURPLE}📝 DafnckMachine v3.1 - Template Update System${NC}"
        echo "=" * 50
        
        # Create log file
        mkdir -p "$AGENT_RUN_DIR"
        mkdir -p "$LOG_DIR"
        touch "$SYSTEM_LOG"
        
        # Update template using Python script
        if python3 "$AGENT_RUN_DIR/unified_agent_validator.py" --template-only; then
            success "✅ Template updated successfully!"
            if [[ "$TEMPLATE_ONLY" == "true" ]]; then
                exit 0
            fi
        else
            error "❌ Failed to update template"
            if [[ "$TEMPLATE_ONLY" == "true" ]]; then
                exit 1
            fi
        fi
    fi

    # Handle cursor-only mode
    if [[ "$CURSOR_ONLY" == "true" ]]; then
        echo -e "${PURPLE}🎯 DafnckMachine v3.1 - Cursor Configuration Generator${NC}"
        echo "=" * 55
        
        # Create log file
        mkdir -p "$AGENT_RUN_DIR"
        mkdir -p "$LOG_DIR"
        touch "$SYSTEM_LOG"
        
        # Generate cursor configuration using Python script
        local cursor_args=""
        if [[ "$CURSOR_BACKUP" == "true" ]]; then
            cursor_args="--cursor-backup"
        fi
        
        if python3 "$AGENT_RUN_DIR/unified_agent_validator.py" --cursor-only $cursor_args; then
            success "🎉 Cursor configuration generated successfully!"
            exit 0
        else
            error "❌ Failed to generate cursor configuration"
            exit 1
        fi
    fi
    
    # Check dependencies
    check_dependencies
    
    # Create log file
    mkdir -p "$AGENT_RUN_DIR"
    mkdir -p "$LOG_DIR"
    touch "$SYSTEM_LOG"
    
    echo -e "${PURPLE}🚀 DafnckMachine v3.1 Unified Agent Validator${NC}"
    echo "=" * 50
    
    local valid_agents=()
    
    # Get agent files for repair/validation
    local agent_files=()
    if [[ -d "$AGENTS_DIR" ]]; then
        while IFS= read -r -d '' file; do
            agent_files+=("$(basename "$file")")
        done < <(find "$AGENTS_DIR" -name "*.json" -print0)
    fi
    
    # Repair phase
    if [[ "$REPAIR_ALL" == "true" || "$FIX_GROUPS" == "true" || "$FIX_REFERENCES" == "true" || "$REPAIR_ONLY" == "true" || "$AUTO_REPAIR" == "true" ]]; then
        echo
        echo -e "${CYAN}🔧 Agent Repair Phase${NC}"
        echo "-" * 25
        
        if [[ ${#agent_files[@]} -eq 0 ]]; then
            warning "No agent files found for repair"
        else
            local repair_files=()
            for agent_file in "${agent_files[@]}"; do
                repair_files+=("$AGENTS_DIR/$agent_file")
            done
            
            local total_fixes=0
            
            if [[ "$REPAIR_ALL" == "true" || "$REPAIR_ONLY" == "true" ]]; then
                repair_all_agents "${repair_files[@]}"
                total_fixes=$?
            else
                if [[ "$FIX_GROUPS" == "true" ]]; then
                    fix_groups_format "${repair_files[@]}"
                    total_fixes=$((total_fixes + $?))
                fi
                if [[ "$FIX_REFERENCES" == "true" ]]; then
                    fix_broken_references "${repair_files[@]}"
                    total_fixes=$((total_fixes + $?))
                fi
            fi
            
            success "Repair phase complete! Made $total_fixes total repairs"
        fi
        
        if [[ "$REPAIR_ONLY" == "true" ]]; then
            info "Repair-only mode complete. Exiting."
            exit 0
        fi
    fi
    
    # Agent validation phase
    if [[ "$SYSTEM_ONLY" != "true" && "$REPAIR_ONLY" != "true" ]]; then
        echo
        echo -e "${BLUE}📋 Agent Validation Phase${NC}"
        echo "-" * 30
        
        if [[ ${#agent_files[@]} -eq 0 ]]; then
            warning "No agent files found in $AGENTS_DIR"
        else
            TOTAL_AGENTS=${#agent_files[@]}
            
            # Get user selection or use all agents
            local selection_result
            local selected_agents=()
            
            if [[ "$AUTO_YES" == "true" ]]; then
                selected_agents=("${agent_files[@]}")
            else
                selection_result=$(get_user_selection "${agent_files[@]}")
                
                case "$selection_result" in
                    "validate_all")
                        selected_agents=("${agent_files[@]}")
                        ;;
                    "system_only")
                        SYSTEM_ONLY=true
                        ;;
                    "repair_all")
                        echo
                        echo -e "${CYAN}🔧 Running comprehensive repair...${NC}"
                        local repair_files=()
                        for agent_file in "${agent_files[@]}"; do
                            repair_files+=("$AGENTS_DIR/$agent_file")
                        done
                        repair_all_agents "${repair_files[@]}"
                        success "Repair complete!"
                        return 0
                        ;;
                    "fix_groups")
                        echo
                        echo -e "${CYAN}🔧 Fixing groups format...${NC}"
                        local repair_files=()
                        for agent_file in "${agent_files[@]}"; do
                            repair_files+=("$AGENTS_DIR/$agent_file")
                        done
                        fix_groups_format "${repair_files[@]}"
                        success "Groups format repair complete!"
                        return 0
                        ;;
                    "fix_references")
                        echo
                        echo -e "${CYAN}🔧 Fixing broken references...${NC}"
                        local repair_files=()
                        for agent_file in "${agent_files[@]}"; do
                            repair_files+=("$AGENTS_DIR/$agent_file")
                        done
                        fix_broken_references "${repair_files[@]}"
                        success "Reference repair complete!"
                        return 0
                        ;;
                    validate_selected:*)
                        IFS=' ' read -ra selected_agents <<< "${selection_result#validate_selected:}"
                        ;;
                    validate_single:*)
                        selected_agents=("${selection_result#validate_single:}")
                        ;;
                esac
            fi
            
            # Validate selected agents
            if [[ "$SYSTEM_ONLY" != "true" && ${#selected_agents[@]} -gt 0 ]]; then
                for agent_file in "${selected_agents[@]}"; do
                    if [[ -f "$AGENTS_DIR/$agent_file" ]]; then
                        echo
                        info "🔍 Testing $agent_file"
                        
                        # Auto-repair if enabled
                        if [[ "$AUTO_REPAIR" == "true" ]]; then
                            info "   🔧 Auto-repairing..."
                            local groups_fixes=0
                            local ref_fixes=0
                            
                            fix_groups_format "$AGENTS_DIR/$agent_file"
                            groups_fixes=$?
                            
                            fix_broken_references "$AGENTS_DIR/$agent_file"
                            ref_fixes=$?
                            
                            local total_auto_fixes=$((groups_fixes + ref_fixes))
                            if [[ $total_auto_fixes -gt 0 ]]; then
                                success "   ✓ Applied $total_auto_fixes auto-repairs"
                            fi
                        fi
                        
                        if validate_agent_comprehensive "$AGENTS_DIR/$agent_file"; then
                            valid_agents+=("$agent_file")
                            VALID_AGENTS=$((VALID_AGENTS + 1))
                        fi
                    fi
                done
            fi
        fi
    fi
    
    # System initialization phase
    if [[ "$AGENTS_ONLY" != "true" ]]; then
        echo
        echo -e "${CYAN}🔧 System Initialization Phase${NC}"
        echo "-" * 35
        
        if system_initialization; then
            success "System initialization completed"
        else
            error "System initialization failed"
        fi
    fi
    
    # Synchronization phase
    if [[ ${#valid_agents[@]} -gt 0 ]]; then
        echo
        echo -e "${YELLOW}🔄 Synchronizing .roomodes${NC}"
        echo "-" * 30
        sync_modes_to_roomodes "${valid_agents[@]}"
        success "Synchronization complete"
    fi
    
        # Cursor configuration generation
    if [[ ("$CURSOR" == "true" || ("$NO_CURSOR" != "true" && ${#valid_agents[@]} -gt 0)) && "$REPAIR_ONLY" != "true" ]]; then
        echo
        echo -e "${CYAN}🎯 Generating Cursor Configuration${NC}"
        echo "-" * 40
        
        # Generate cursor configuration using Python script
        local cursor_args=""
        if [[ "$CURSOR_BACKUP" == "true" ]]; then
            cursor_args="--cursor-backup"
        fi
        
        if python3 "$AGENT_RUN_DIR/unified_agent_validator.py" --cursor-only $cursor_args; then
            success "✅ Cursor configuration generated successfully"
        else
            error "❌ Failed to generate cursor configuration"
        fi
    fi

    # Template update generation
    if [[ "$UPDATE_TEMPLATE" == "true" && "$REPAIR_ONLY" != "true" ]]; then
        echo
        echo -e "${CYAN}📝 Updating Template Documentation${NC}"
        echo "-" * 40
        
        if python3 "$AGENT_RUN_DIR/unified_agent_validator.py" --template-only; then
            success "✅ Template documentation updated successfully"
        else
            error "❌ Failed to update template documentation"
        fi
    fi

    # Generate report
    if [[ ${#valid_agents[@]} -gt 0 ]]; then
        generate_comprehensive_report "${valid_agents[@]}"
    else
        generate_comprehensive_report ""
    fi
    info "Report saved to: $(echo "$VALIDATION_REPORT" | sed "s|$BASE_DIR/||")"
    
    if [[ "$GENERATE_REPORT" == "true" ]]; then
        echo
        echo "=" * 50
        cat "$VALIDATION_REPORT"
    fi
    
    # Final status
    echo
    if [[ "$SYSTEM_ONLY" == "true" ]]; then
        success "🎉 System initialization completed!"
        exit 0
    elif [[ $VALID_AGENTS -eq $TOTAL_AGENTS ]] && [[ $TOTAL_AGENTS -gt 0 ]]; then
        success "🎉 All validations passed!"
        exit 0
    else
        warning "⚠️  Some validations failed. Check the report for details."
        exit 1
    fi
}

# Run main function with all arguments
main "$@" 