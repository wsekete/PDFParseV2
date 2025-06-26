# Phase 2: Claude Desktop Integration - Detailed Task List

## 🎯 **OBJECTIVE**
Create a seamless AI-powered PDF field naming workflow:
1. Upload PDF to Claude Desktop
2. Extract fields with ./pdf_extract  
3. Generate intelligent API names using AI
4. Review and edit names interactively
5. Export structured data for PDF modification

---

## 📋 **TASK BREAKDOWN**

### **Phase 2.1: MCP Server Foundation** 
*Priority: HIGH | Estimated: 3-4 hours*

#### Task 2.1.1: MCP Server Architecture
- [ ] **Create MCP server directory structure**
  - `src/mcp_tools/pdf_naming_server.py` - Main MCP server
  - `src/mcp_tools/tools/` - Individual MCP tool implementations
  - `src/mcp_tools/config/` - Configuration and schema files

#### Task 2.1.2: Core MCP Tools Implementation ✅ COMPLETE
- [x] **`extract_fields` tool** - Wraps existing PDF extraction
  - Input: PDF file path or base64 data
  - Output: Structured field data (CSV format)
  - Error handling for invalid PDFs
  
- [x] **`generate_names` tool** - AI-powered name generation  
  - Input: Field data + training examples
  - Output: BEM-style API names with confidence scores
  - Integration with naming engine
  
- [x] **`validate_names` tool** - Name validation and conflict detection
  - Input: Generated names + existing field names  
  - Output: Validation results with suggestions
  - Duplicate detection and BEM compliance checking

- [x] **`export_mapping` tool** - Export final field mappings
  - Input: Reviewed and approved field names
  - Output: Structured JSON/CSV for PDF modifier
  - Include metadata for safe PDF modification

#### Task 2.1.3: Claude Desktop Configuration ✅ COMPLETE
- [x] **Create `claude_desktop_config.json`**
  - MCP server registration
  - Tool permissions and capabilities
  - Development and production configurations
- [x] **Enhanced configuration with detailed tool schemas**
- [x] **Setup documentation (`CLAUDE_DESKTOP_SETUP.md`)**
- [x] **Automated testing script (`test_mcp_setup.py`)**
- [x] **All setup validation tests passing**

#### Task 2.1.4: MCP Server Testing
- [ ] **Unit tests for each MCP tool**
- [ ] **Integration tests with sample PDFs**
- [ ] **Claude Desktop connection testing**

---

### **Phase 2.2: Intelligent Naming Engine**
*Priority: HIGH | Estimated: 4-5 hours*

#### Task 2.2.1: Training Data Integration
- [ ] **Load Clean Field Data patterns** (`training_data/Clean Field Data - Sheet1.csv`)
  - Parse 6,338 field examples
  - Extract BEM naming patterns
  - Build pattern recognition database
  - Category and context analysis

#### Task 2.2.2: BEM Naming Logic Implementation
- [ ] **Core naming rules** (`src/naming_engine/bem_generator.py`)
  ```
  block_element__modifier
  - Blocks: form sections (owner-information, pricing)
  - Elements: field purposes (name, phone-number)  
  - Modifiers: field variations (monthly, primary)
  - Radio groups: --group suffix
  ```

- [ ] **Context-aware naming** (`src/naming_engine/context_analyzer.py`)
  - Field label analysis
  - Surrounding text interpretation
  - Section header categorization
  - Field type-specific logic

#### Task 2.2.3: AI Prompt Integration
- [ ] **Implement naming prompt structure**
  ```
  Process each field:
  Field: {label="{label}", type="{type}", context="{surrounding_text}", section="{section_header}"}
  Generated API name: [apply naming logic with training examples]
  ```

- [ ] **Confidence scoring system**
  - Pattern match confidence (high/medium/low)
  - Alternative name suggestions
  - Validation against training data

#### Task 2.2.4: Special Field Handling
- [ ] **Radio button groups** - Automatic --group suffix detection
- [ ] **Signature fields** - Standard signatures_[role] format  
- [ ] **Checkbox logic** - BEM pattern compliance
- [ ] **Text field optimization** - Descriptive but concise naming

---

### **Phase 2.3: Interactive Review Interface**
*Priority: MEDIUM | Estimated: 3-4 hours*

#### Task 2.3.1: Artifact Design
- [ ] **Field mapping table format**
  ```
  | Field ID | Original Label | Generated Name | Type | Confidence | Actions |
  |----------|----------------|----------------|------|------------|---------|
  | field_1  | First Name     | owner-info_first-name | TextField | High | ✏️ Edit |
  ```

- [ ] **Interactive elements**
  - Editable name cells with validation
  - Confidence indicators (🟢🟡🔴)
  - Quick action buttons (Accept/Edit/Regenerate)
  - Bulk operations (Accept All High Confidence)

#### Task 2.3.2: Validation and Feedback
- [ ] **Real-time validation**
  - BEM syntax checking
  - Duplicate name detection
  - Character limit enforcement
  - Special character validation

- [ ] **User guidance**
  - Naming convention tooltips
  - Example suggestions
  - Error explanations with corrections
  - Pattern-based auto-complete

#### Task 2.3.3: Review Workflow
- [ ] **Progressive review modes**
  - Review by confidence level (Low → Medium → High)
  - Review by field type (RadioGroups → TextFields → etc.)
  - Review by section (Personal Info → Payment → Signatures)

---

### **Phase 2.4: PDF Modifier Foundation**
*Priority: MEDIUM | Estimated: 2-3 hours*

#### Task 2.4.1: Output Format Design
- [ ] **Structured mapping format**
  ```json
  {
    "pdf_metadata": {
      "original_path": "document.pdf",
      "field_count": 73,
      "extraction_timestamp": "2025-01-24T10:30:00Z"
    },
    "field_mappings": [
      {
        "field_id": "uuid-123",
        "original_name": "/Tx.FirstName",
        "new_name": "owner-information_first-name", 
        "field_type": "TextField",
        "coordinates": {"x": 100, "y": 200, "width": 150, "height": 20},
        "validation_status": "approved"
      }
    ],
    "modification_plan": {
      "backup_required": true,
      "modification_type": "acrofield_rename",
      "estimated_changes": 73
    }
  }
  ```

#### Task 2.4.2: Validation System
- [ ] **PDF field identifier validation**
  - Valid PDF name characters
  - Length restrictions
  - Unicode handling
  - Conflict resolution

- [ ] **Safety checks**
  - Required backup creation
  - Modification impact assessment
  - Rollback capability design
  - Change logging requirements

---

### **Phase 2.5: Integration & Testing**
*Priority: MEDIUM | Estimated: 2-3 hours*

#### Task 2.5.1: End-to-End Workflow Testing
- [ ] **Test complete workflow** 
  1. PDF upload to Claude Desktop
  2. Field extraction via MCP tool
  3. Name generation and review
  4. Export structured mapping
  5. Validation of output format

#### Task 2.5.2: Real PDF Validation
- [ ] **Test with training data PDFs**
  - W-4R_parsed.pdf (10 fields)
  - LIFE-1528-Q__parsed.pdf (73 fields) 
  - FAF-0485AO__parsed.pdf (25 CheckBoxes)

- [ ] **Compare against expected outputs**
  - Field count accuracy
  - Name generation quality
  - BEM compliance verification

#### Task 2.5.3: Performance & Error Handling
- [ ] **Large PDF testing** (100+ fields)
- [ ] **Malformed PDF handling**
- [ ] **Network error recovery**
- [ ] **Memory usage optimization**

---

### **Phase 2.6: Documentation & Polish**
*Priority: LOW | Estimated: 1-2 hours*

#### Task 2.6.1: User Documentation
- [ ] **Claude Desktop setup guide**
- [ ] **Workflow tutorial with screenshots**
- [ ] **Troubleshooting guide**
- [ ] **BEM naming convention reference**

#### Task 2.6.2: Developer Documentation  
- [ ] **MCP server API documentation**
- [ ] **Naming engine architecture**
- [ ] **Extension points for custom logic**
- [ ] **Testing and validation procedures**

---

## 🔄 **IMPLEMENTATION ORDER**

### Week 1: Foundation
1. ✅ Phase 2.1.1-2 - MCP Server core structure ✅ COMPLETE (2025-06-26)
2. 🚧 Phase 2.2.1-2 - Basic naming engine

### Week 2: Intelligence  
3. ✅ Phase 2.2.3-4 - AI integration and special handling
4. ✅ Phase 2.1.3-4 - Claude Desktop integration

### Week 3: Polish
5. ✅ Phase 2.3 - Interactive review interface
6. ✅ Phase 2.4 - PDF modifier foundation  
7. ✅ Phase 2.5-6 - Testing and documentation

---

## 📊 **SUCCESS CRITERIA**

### Functional Requirements
- [ ] **Seamless PDF upload** in Claude Desktop triggers field extraction
- [ ] **AI-generated names** follow BEM conventions with >80% accuracy  
- [ ] **Interactive review** allows editing with real-time validation
- [ ] **Structured export** ready for PDF modification

### Technical Requirements  
- [ ] **MCP integration** works reliably with Claude Desktop
- [ ] **Processing time** <30 seconds for typical PDFs (50-100 fields)
- [ ] **Error handling** graceful degradation with helpful messages
- [ ] **Output format** validated against PDF modification requirements

### User Experience
- [ ] **Intuitive workflow** - minimal learning curve
- [ ] **Clear feedback** - progress indicators and validation messages  
- [ ] **Flexible review** - efficient editing and bulk operations
- [ ] **Professional output** - ready for production PDF modification

---

## 🔗 **RELATED FILES**
- `CLAUDE.md` - Project overview and Phase 1 status
- `src/pdf_parser/field_extractor.py` - Existing extraction engine
- `training_data/Clean Field Data - Sheet1.csv` - Naming pattern examples
- `training_data/pdf_csv_pairs/` - Test PDFs and expected outputs

---

**Last Updated**: 2025-06-26  
**Status**: Phase 2.1.3 Complete - Claude Desktop Configuration Ready ✅  
**Next Step**: Phase 2.1.4 - MCP Server Testing