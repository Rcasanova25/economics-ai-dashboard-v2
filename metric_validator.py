"""
Metric Validation Module
Handles all validation logic for economic metrics using schema-based rules
"""

import re
import pandas as pd
from typing import Dict, List, Tuple, Optional
from metric_validation_schema import METRIC_VALIDATION_SCHEMA, CROSS_METRIC_RULES, RECLASSIFICATION_PRIORITY


class MetricValidator:
    """Validates economic metrics against defined schemas and rules"""
    
    def __init__(self):
        self.schema = METRIC_VALIDATION_SCHEMA
        self.cross_rules = CROSS_METRIC_RULES
        self.reclassification_priority = RECLASSIFICATION_PRIORITY
        
        # ICT sector patterns - MUST BE PRESERVED
        self.ict_patterns = [
            r'\bict\b',
            r'\binformation.*communication.*technology\b',
            r'\btelecom\b',
            r'\bdigital.*infrastructure\b',
            r'\binformation.*technology\b',
            r'\bcommunication.*technology\b'
        ]
        
        # Meaningful zero context patterns
        self.meaningful_zero_patterns = [
            'survey', 'study', 'finding', 'result', 'observed', 
            'measured', 'no change', 'zero growth', 'unchanged',
            'remained flat', 'no increase', 'no decrease', 'stable at',
            'respondents reported', 'participants indicated', 'reported no',
            'participants reported', 'companies reported', 'firms reported',
            'analysis found', 'research shows', 'data indicates'
        ]
        
    def validate_against_schema(self, metric_type: str, value: float, unit: str, context: str) -> List[Dict]:
        """
        Validate a record against the schema for its metric type
        
        Returns:
            List of validation issues found, each with reason and confidence
        """
        # Find matching schema
        schema_key = self._find_schema_key(metric_type)
        if not schema_key:
            return []  # No schema for this metric type
            
        schema = self.schema[schema_key]
        issues = []
        
        # Check unit validity
        if unit in schema.get('invalid_units', []):
            issues.append({
                'reason': f"Invalid unit '{unit}' for {metric_type}",
                'confidence': 0.95,
                'severity': 'high'
            })
        elif unit not in schema.get('valid_units', []):
            issues.append({
                'reason': f"Unexpected unit '{unit}' for {metric_type}",
                'confidence': 0.85,
                'severity': 'medium'
            })
            
        # Check value ranges
        if unit in schema.get('value_ranges', {}):
            min_val, max_val = schema['value_ranges'][unit]
            if not (min_val <= value <= max_val):
                issues.append({
                    'reason': f"Value {value} outside expected range [{min_val}, {max_val}] for {unit}",
                    'confidence': 0.90,
                    'severity': 'medium'
                })
                
        # Check zero values
        if value == 0 and not schema.get('zero_value_valid', True):
            # First check if this is a meaningful zero from a survey/study
            if not self.is_meaningful_zero(value, context):
                # Then check if context suggests it's a change metric
                change_patterns = ['change', 'increase', 'decrease', 'growth', 'reduction', 'decline']
                if not any(pattern in context.lower() for pattern in change_patterns):
                    issues.append({
                        'reason': f"Zero value suspicious for {metric_type}",
                        'confidence': 0.80,
                        'severity': 'low'
                    })
                
        # Check required patterns
        patterns_required = schema.get('patterns_required', [])
        if patterns_required and not any(pattern in context.lower() for pattern in patterns_required):
            issues.append({
                'reason': f"Context missing required patterns for {metric_type}",
                'confidence': 0.70,
                'severity': 'low'
            })
            
        # Check excluded patterns
        patterns_exclude = schema.get('patterns_exclude', [])
        if any(pattern in context.lower() for pattern in patterns_exclude):
            issues.append({
                'reason': f"Context contains excluded patterns for {metric_type}",
                'confidence': 0.75,
                'severity': 'medium'
            })
            
        return issues
    
    def apply_cross_metric_rules(self, metric_type: str, value: float, unit: str, 
                                year: int, context: str) -> List[Dict]:
        """
        Apply cross-metric validation rules that check logical consistency
        
        Returns:
            List of rule violations found
        """
        issues = []
        
        for rule in self.cross_rules:
            try:
                # Try to apply the rule with available parameters
                rule_params = {
                    'metric_type': metric_type,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'context': context
                }
                
                # Get the parameters the rule condition expects
                import inspect
                sig = inspect.signature(rule['condition'])
                expected_params = list(sig.parameters.keys())
                
                # Filter to only pass expected parameters
                filtered_params = {k: v for k, v in rule_params.items() if k in expected_params}
                
                # Check if the condition applies
                if rule['condition'](**filtered_params):
                    issues.append({
                        'reason': rule['rule'],
                        'action': rule['action'],
                        'confidence': rule['confidence'],
                        'severity': 'high'  # Cross-metric rules are usually high severity
                    })
            except Exception as e:
                # Log but don't crash on individual rule failures
                print(f"Warning: Rule '{rule.get('rule', 'unknown')}' failed to apply: {str(e)}")
                continue
                    
        return issues
    
    def classify_metric_type(self, context: str, value: float, unit: str, 
                           current_type: str = None) -> str:
        """
        Classify vague metric types using schema patterns and context
        
        Returns:
            Classified metric type or 'unknown_metric' if no match
        """
        context_lower = context.lower()
        
        # Check each metric type in priority order
        for metric_type in self.reclassification_priority:
            if metric_type not in self.schema:
                continue
                
            schema = self.schema[metric_type]
            
            # Check if unit is valid for this metric type
            if unit in schema.get('invalid_units', []):
                continue
                
            # Check value ranges if specified
            if unit in schema.get('value_ranges', {}):
                min_val, max_val = schema['value_ranges'][unit]
                if not (min_val <= value <= max_val):
                    continue
                    
            # Check required patterns
            patterns = schema.get('patterns_required', [])
            if patterns and any(pattern in context_lower for pattern in patterns):
                # Check excluded patterns
                excluded = schema.get('patterns_exclude', [])
                if not any(exc in context_lower for exc in excluded):
                    return metric_type
                    
        return current_type if current_type else 'unknown_metric'
    
    def detect_citation_year(self, value: float, year: int, context: str) -> bool:
        """
        Detect if a value is likely a citation year rather than a metric
        
        Returns:
            True if likely a citation, False otherwise
        """
        # Check if value equals year and is in reasonable year range
        if value == year and 1900 <= value <= 2030:
            # Look for citation patterns
            citation_patterns = [
                r'\(\d{4}\)',  # (2024)
                r'\b(?:19|20)\d{2}\)',  # Years starting with 19 or 20
                r'et al\.?\s*\(?(?:19|20)\d{2}',  # et al. 2024 or et al. (2024)
                r'[A-Z][a-z]+\s+\(?(?:19|20)\d{2}',  # Author (2024)
                r'[A-Z][a-z]+\s+and\s+[A-Z][a-z]+\s*\(?(?:19|20)\d{2}',  # Author and Author (2024)
            ]
            
            for pattern in citation_patterns:
                if re.search(pattern, context):
                    return True
                    
            # Additional keywords that suggest citations
            citation_keywords = ['article', 'paper', 'study', 'research', 'publication', 
                               'journal', 'conference', 'proceedings']
            if any(keyword in context.lower() for keyword in citation_keywords):
                return True
                
        return False
    
    def validate_unit_metric_consistency(self, metric_type: str, unit: str) -> Tuple[bool, str]:
        """
        Check if a unit is consistent with the metric type
        
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        schema_key = self._find_schema_key(metric_type)
        if not schema_key:
            return True, ""  # No schema to validate against
            
        schema = self.schema[schema_key]
        
        if unit in schema.get('invalid_units', []):
            return False, f"Unit '{unit}' is invalid for {metric_type}"
            
        valid_units = schema.get('valid_units', [])
        if valid_units and unit not in valid_units:
            return False, f"Unit '{unit}' is not in valid units for {metric_type}: {valid_units}"
            
        return True, ""
    
    def _find_schema_key(self, metric_type: str) -> Optional[str]:
        """Find the schema key for a given metric type"""
        # Direct match
        if metric_type in self.schema:
            return metric_type
            
        # Handle variations (e.g., labor_metrics -> employment_metric)
        mappings = {
            'labor_metrics': 'employment_metric',
            'labor_metric': 'employment_metric',
            'financial_metric': 'investment_metric',  # If we want to treat these similarly
        }
        
        return mappings.get(metric_type)
    
    def get_validation_summary(self, issues: List[Dict]) -> Dict:
        """
        Summarize validation issues for reporting
        
        Returns:
            Dictionary with counts by severity and top issues
        """
        if not issues:
            return {
                'total_issues': 0,
                'by_severity': {},
                'top_issues': []
            }
            
        severity_counts = {}
        issue_counts = {}
        
        for issue in issues:
            # Count by severity
            severity = issue.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by reason
            reason = issue.get('reason', 'unknown')
            issue_counts[reason] = issue_counts.get(reason, 0) + 1
            
        # Get top 5 issues
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_issues': len(issues),
            'by_severity': severity_counts,
            'top_issues': [{'reason': reason, 'count': count} for reason, count in top_issues]
        }
    
    def is_ict_data(self, context: str) -> bool:
        """
        Check if context contains ICT (Information & Communication Technology) references
        
        Args:
            context: Text context to check
            
        Returns:
            True if ICT-related content detected
        """
        context_lower = context.lower()
        
        for pattern in self.ict_patterns:
            if re.search(pattern, context_lower, re.IGNORECASE):
                return True
                
        return False
    
    def is_meaningful_zero(self, value: float, context: str) -> bool:
        """
        Check if a zero value represents a meaningful economic finding
        
        Args:
            value: The numeric value
            context: Text context describing the value
            
        Returns:
            True if this is a meaningful zero (e.g., "survey found 0% growth")
        """
        if value != 0:
            return False
            
        context_lower = context.lower()
        
        # Check for survey/study context patterns
        for pattern in self.meaningful_zero_patterns:
            if pattern in context_lower:
                return True
                
        return False