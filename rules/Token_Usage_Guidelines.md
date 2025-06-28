# Token Usage Guidelines

## 1. Mission Statement
Define best practices for using design tokens in DafnckMachine v3.1 to ensure consistency, scalability, and maintainability across the UI.

**Example:**
- "Apply tokens for color, typography, spacing, and border radius in all UI components."

## 2. Token Types and Purpose
List the types of tokens and their intended use.
- Color tokens: Theming and accessibility
- Typography tokens: Font consistency
- Spacing tokens: Layout and alignment
- Border radius tokens: Consistent rounding

**Example Table:**
| Token Type   | Example Token      | Usage Example                |
|-------------|-------------------|------------------------------|
| Color       | color.primary     | Button background            |
| Typography  | fontFamily        | Headings, body text          |
| Spacing     | spacing.md        | Padding in cards and modals  |
| Border      | borderRadius.md   | Card and button corners      |

## 3. Implementation Guidelines
Describe how to implement and reference tokens in code.
- Use token variables in CSS/JS
- Reference tokens in design tools (e.g., Figma)
- Avoid hardcoding values

**Example:**
- "Use `var(--color-primary)` for all primary backgrounds."

## 4. Theming and Customization
Explain how tokens enable theming and easy updates.
- Light/dark mode
- Brand customization
- Global updates via token changes

## 5. Success Criteria
- Tokens are used consistently across all UI
- Theming and customization are easy to implement
- No hardcoded style values in codebase

## 6. Validation Checklist
- [ ] All token types are documented
- [ ] Usage examples are provided
- [ ] Implementation guidelines are clear
- [ ] Theming and customization are addressed

---
*This document follows the DafnckMachine v3.1 PRD template. Update as new token types or usage patterns are introduced.* 