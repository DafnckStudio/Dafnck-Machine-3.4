def create_output_specification_yaml(agent_path, agent_data):
    """Create output specification file with ALL fields"""
    output_spec = agent_data.get('outputSpec', {})
    
    if output_spec:
        # Extract all fields from the JSON outputSpec
        output_data = {
            'output_specification': {
                'type': output_spec.get('type', ''),
                'format': output_spec.get('format', ''),
                'schema': output_spec.get('schema', {}),
                'validationRules': output_spec.get('validationRules', []),
                'example': output_spec.get('example', {})
            }
        }
        
        # Remove empty fields to keep YAML clean
        output_spec_clean = {}
        for key, value in output_data['output_specification'].items():
            if value:  # Only include non-empty values
                output_spec_clean[key] = value
        
        if output_spec_clean:
            final_output_data = {'output_specification': output_spec_clean}
            
            output_path = agent_path / 'output_format' / 'output_specification.yaml'
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(final_output_data, f, default_flow_style=False, allow_unicode=True)
            
            print(f"  ✅ Created output_specification.yaml with {len(output_spec_clean)} fields")