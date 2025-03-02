# ServiceNow Catalog Optimization Plan

This document outlines the plan for implementing catalog optimization features in the ServiceNow MCP integration.

## Overview

The catalog optimization features will help users analyze, manage, and improve their existing ServiceNow service catalogs. These features will provide insights into catalog usage, performance, and structure, and offer recommendations for optimization.

## Optimization Tools

### 1. Catalog Analytics Tools

#### 1.1 Get Catalog Usage Statistics

**Parameters:**
```python
class CatalogUsageStatsParams(BaseModel):
    """Parameters for getting catalog usage statistics."""
    
    time_period: str = Field("last_30_days", description="Time period for statistics (last_7_days, last_30_days, last_90_days, last_year)")
    category_id: Optional[str] = Field(None, description="Filter by category ID")
    include_inactive: bool = Field(False, description="Whether to include inactive items")
```

**Returns:**
- Most ordered items
- Least ordered items
- Average processing time
- Abandonment rate (items added to cart but not ordered)
- User satisfaction ratings

**Implementation:**
- Query the ServiceNow API for order statistics
- Aggregate data by item and category
- Calculate metrics like order volume, processing time, and abandonment rate

#### 1.2 Get Item Performance Metrics

**Parameters:**
```python
class ItemPerformanceParams(BaseModel):
    """Parameters for getting performance metrics for a catalog item."""
    
    item_id: str = Field(..., description="Catalog item ID")
    time_period: str = Field("last_30_days", description="Time period for metrics")
```

**Returns:**
- Order volume over time
- Average fulfillment time
- Approval rates
- Rejection reasons
- User ratings and feedback

**Implementation:**
- Query the ServiceNow API for item-specific metrics
- Calculate performance indicators
- Identify trends over the specified time period

### 2. Catalog Management Tools

#### 2.1 Update Catalog Item

**Parameters:**
```python
class UpdateCatalogItemParams(BaseModel):
    """Parameters for updating a catalog item."""
    
    item_id: str = Field(..., description="Catalog item ID to update")
    name: Optional[str] = Field(None, description="New name for the item")
    short_description: Optional[str] = Field(None, description="New short description")
    description: Optional[str] = Field(None, description="New detailed description")
    category: Optional[str] = Field(None, description="New category ID")
    price: Optional[str] = Field(None, description="New price")
    active: Optional[bool] = Field(None, description="Whether the item is active")
    order: Optional[int] = Field(None, description="Display order in the category")
```

**Implementation:**
- Build a PATCH request to update the catalog item
- Only include fields that are provided in the parameters
- Return the updated item details

#### 2.2 Update Catalog Category

**Parameters:**
```python
class UpdateCatalogCategoryParams(BaseModel):
    """Parameters for updating a catalog category."""
    
    category_id: str = Field(..., description="Category ID to update")
    title: Optional[str] = Field(None, description="New title for the category")
    description: Optional[str] = Field(None, description="New description")
    parent: Optional[str] = Field(None, description="New parent category ID")
    active: Optional[bool] = Field(None, description="Whether the category is active")
    order: Optional[int] = Field(None, description="Display order")
```

**Implementation:**
- Build a PATCH request to update the catalog category
- Only include fields that are provided in the parameters
- Return the updated category details

#### 2.3 Update Item Variable

**Parameters:**
```python
class UpdateItemVariableParams(BaseModel):
    """Parameters for updating a catalog item variable."""
    
    variable_id: str = Field(..., description="Variable ID to update")
    label: Optional[str] = Field(None, description="New label for the variable")
    help_text: Optional[str] = Field(None, description="New help text")
    default_value: Optional[str] = Field(None, description="New default value")
    mandatory: Optional[bool] = Field(None, description="Whether the variable is mandatory")
    order: Optional[int] = Field(None, description="Display order")
```

**Implementation:**
- Build a PATCH request to update the catalog item variable
- Only include fields that are provided in the parameters
- Return the updated variable details

### 3. Catalog Optimization Tools

#### 3.1 Get Optimization Recommendations

**Parameters:**
```python
class OptimizationRecommendationsParams(BaseModel):
    """Parameters for getting catalog optimization recommendations."""
    
    category_id: Optional[str] = Field(None, description="Filter by category ID")
    recommendation_types: List[str] = Field(
        ["inactive_items", "low_usage", "high_abandonment", "slow_fulfillment", "description_quality"],
        description="Types of recommendations to include"
    )
```

**Returns:**
- Inactive items that could be retired
- Items with low usage that might need promotion
- Items with high abandonment rates that might need simplification
- Items with slow fulfillment that need process improvements
- Items with poor description quality

**Implementation:**
- Query the ServiceNow API for various metrics
- Apply analysis algorithms to identify optimization opportunities
- Generate recommendations based on the analysis

#### 3.2 Get Catalog Structure Analysis

**Parameters:**
```python
class CatalogStructureAnalysisParams(BaseModel):
    """Parameters for analyzing catalog structure."""
    
    include_inactive: bool = Field(False, description="Whether to include inactive categories and items")
```

**Returns:**
- Categories with too many or too few items
- Deeply nested categories that might be hard to navigate
- Inconsistent naming patterns
- Duplicate or similar items across categories

**Implementation:**
- Query the ServiceNow API for the catalog structure
- Analyze the structure for usability issues
- Generate recommendations for improving the structure

## Implementation Plan

### Phase 1: Analytics Tools
1. Implement `get_catalog_usage_stats`
2. Implement `get_item_performance`
3. Create tests for analytics tools

### Phase 2: Management Tools
1. Implement `update_catalog_item`
2. Implement `update_catalog_category`
3. Implement `update_item_variable`
4. Create tests for management tools

### Phase 3: Optimization Tools
1. Implement `get_optimization_recommendations`
2. Implement `get_catalog_structure_analysis`
3. Create tests for optimization tools

### Phase 4: Integration
1. Register all tools with the MCP server
2. Create example scripts for optimization workflows
3. Update documentation

## Example Usage

### Example 1: Analyzing Catalog Usage

```python
# Get catalog usage statistics
params = CatalogUsageStatsParams(time_period="last_90_days")
result = get_catalog_usage_stats(config, auth_manager, params)

# Print the most ordered items
print("Most ordered items:")
for item in result["most_ordered_items"]:
    print(f"- {item['name']}: {item['order_count']} orders")

# Print items with high abandonment rates
print("\nItems with high abandonment rates:")
for item in result["high_abandonment_items"]:
    print(f"- {item['name']}: {item['abandonment_rate']}% abandonment rate")
```

### Example 2: Getting Optimization Recommendations

```python
# Get optimization recommendations
params = OptimizationRecommendationsParams(
    recommendation_types=["inactive_items", "low_usage", "description_quality"]
)
result = get_optimization_recommendations(config, auth_manager, params)

# Print the recommendations
for rec in result["recommendations"]:
    print(f"\n{rec['title']}")
    print(f"Impact: {rec['impact']}, Effort: {rec['effort']}")
    print(f"{rec['description']}")
    print(f"Recommended Action: {rec['action']}")
    print(f"Affected Items: {len(rec['items'])}")
    for item in rec['items'][:3]:
        print(f"- {item['name']}: {item['short_description']}")
```

### Example 3: Updating a Catalog Item

```python
# Update a catalog item
params = UpdateCatalogItemParams(
    item_id="sys_id_of_item",
    short_description="Updated description that is more clear and informative",
    price="99.99"
)
result = update_catalog_item(config, auth_manager, params)

if result["success"]:
    print(f"Successfully updated item: {result['data']['name']}")
else:
    print(f"Error: {result['message']}")
```

## Considerations

1. **Data Access**: These tools require access to ServiceNow reporting and analytics data, which might require additional permissions.

2. **Performance**: Some of these analyses could be resource-intensive, especially for large catalogs.

3. **Custom Metrics**: ServiceNow instances often have custom metrics and KPIs for catalog performance, which would need to be considered.

4. **Change Management**: Any changes to the catalog should follow proper change management processes.

5. **User Feedback**: Incorporating user feedback data would make the optimization recommendations more valuable. 