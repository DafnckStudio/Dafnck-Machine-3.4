# Agent Operations Manual
## DafnckMachine-V3.1 Quick Reference

### 🎯 **Agent Quick Start** (30 seconds)
1. **Check your current step**: Look at the workflow file you're in
2. **Read the Agent Context**: Every workflow file has agent instructions at the top
3. **Access Brain System**: Use lightweight configs, not full JSON files
4. **Execute & Update**: Complete tasks and update state
5. **Navigate**: Follow Previous/Next step links

---

## 🧠 **Brain System Integration**

### **DNA System** - Agent Registry & Capabilities
```bash
# Quick Agent Lookup
Agent ID: [Your assigned agent from workflow file]
Capabilities: [Listed in workflow file Agent Context]
Communication: [Use protocols specified in workflow]
```

### **STEP System** - Task Execution
```bash
# Task Structure: N.X format (e.g., 1.1, 1.2, 2.1)
Current Task: [From workflow file header]
Subtasks: [Listed in Task Breakdown section]
Validation: [Check Success Criteria checklist]
```

### **GENESIS System** - Adaptive Configuration
```bash
# Auto-adapts based on:
- Project type detection
- Performance feedback
- Error patterns
- Resource utilization
```

---

## 📁 **File Structure Navigation**

### **01_Workflow** - Your Primary Workspace
- Each file = One workflow step
- Contains: Agent instructions, tasks, validation
- Pattern: `XX_Step_Name.md`
- Navigation: Previous/Next step links

### **02_Vision** - Project Context
- High-level project goals
- Strategic direction
- Stakeholder requirements
- Reference when making decisions

### **03_Project** - Implementation Output
- Actual project files
- Generated code
- Documentation
- Deliverables

---

## ⚡ **Performance Best Practices**

### **Lightweight Operations**
1. **Use Step-Specific Configs**: Don't load entire Brain system
2. **Cache Frequently Used Data**: Store common configurations locally
3. **Lazy Load**: Only access what you need for current step
4. **Batch Operations**: Group similar tasks together

### **Agent Context Loading**
```markdown
# Every workflow file contains:
## Agent Context
- **Assigned Agent**: [Your agent ID]
- **Required Capabilities**: [Specific to this step]
- **Brain Integration**: [Lightweight config references]
- **Previous Step Output**: [What you receive]
- **Expected Output**: [What you should produce]
```

---

## 🔄 **Workflow Execution Pattern**

### **Standard Agent Flow**
1. **Enter Workflow Step**
   - Read Agent Context header
   - Check Previous Step outputs
   - Load step-specific configuration

2. **Execute Tasks**
   - Follow numbered task structure (1.1, 1.2, etc.)
   - Use Brain system for complex decisions
   - Update progress in real-time

3. **Validate & Complete**
   - Check Success Criteria checklist
   - Generate required outputs
   - Update state for next agent

4. **Navigate to Next Step**
   - Follow Next Step link
   - Pass outputs to next agent
   - Update global project state

---

## 🛠 **Brain System Quick Reference**

### **When to Use Full Brain System**
- Complex decision making
- Multi-agent coordination
- Learning from failures
- Adaptive configuration

### **When to Use Lightweight Interface**
- Simple task execution
- Standard operations
- Performance-critical paths
- Routine validations

### **Brain System Access Patterns**
```bash
# Lightweight (Recommended for most operations)
GET /brain/step-config/{current_step}
GET /brain/agent-context/{agent_id}/{step_id}

# Full System (For complex operations)
GET /brain/dna/full-config
GET /brain/step/execution-engine
GET /brain/genesis/adaptive-config
```

---

## 📊 **State Management**

### **Always Update**
- Current step progress
- Task completion status
- Error conditions
- Performance metrics

### **State Synchronization**
- Real-time updates to Brain system
- Cross-agent communication
- Workflow progression tracking
- Quality gate validation

---

## 🚨 **Error Handling**

### **Common Issues & Solutions**
1. **Configuration Not Found**: Use fallback configs in workflow file
2. **Agent Capability Mismatch**: Check DNA registry for alternatives
3. **Task Validation Failure**: Review Success Criteria and retry
4. **Performance Degradation**: Switch to lightweight operations

### **Escalation Path**
1. **Retry with different approach**
2. **Request agent reassignment**
3. **Escalate to Orchestrator Agent**
4. **Human intervention (last resort)**

---

## 🎯 **Success Metrics**

### **Agent Performance Indicators**
- Task completion time
- Validation success rate
- Error frequency
- Resource utilization

### **System Health Checks**
- Brain system responsiveness
- State synchronization accuracy
- Cross-agent communication
- Workflow progression rate

---

## 📚 **Quick Reference Commands**

```bash
# Check current workflow state
GET /workflow/current-state

# Get step-specific agent config
GET /brain/agent-config/{step_id}

# Update task progress
POST /workflow/update-progress

# Validate current step
GET /workflow/validate/{step_id}

# Navigate to next step
POST /workflow/advance/{next_step_id}
```

---

**💡 Remember**: This manual is embedded in every workflow file's Agent Context section. You don't need to reference this full manual every time - just use the step-specific guidance in each workflow file.

**🔄 Last Updated**: Auto-generated based on Brain system evolution

**📞 Support**: Orchestrator Agent handles escalations and system issues 