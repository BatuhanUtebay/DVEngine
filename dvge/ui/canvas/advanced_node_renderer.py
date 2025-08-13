# dvge/ui/canvas/advanced_node_renderer.py

"""Advanced node rendering for specialized node types."""

from ...constants import *
from ...models import ShopNode, RandomEventNode, TimerNode, InventoryNode


class AdvancedNodeRenderer:
    """Handles rendering of advanced node types on the canvas."""
    
    def __init__(self, canvas):
        self.canvas = canvas
    
    def create_advanced_node_content(self, node, x, y, tags):
        """Creates content for advanced node types."""
        if isinstance(node, ShopNode):
            return self._create_shop_content(node, x, y, tags)
        elif isinstance(node, RandomEventNode):
            return self._create_random_event_content(node, x, y, tags)
        elif isinstance(node, TimerNode):
            return self._create_timer_content(node, x, y, tags)
        elif isinstance(node, InventoryNode):
            return self._create_inventory_content(node, x, y, tags)
        return {}
    
    def _create_shop_content(self, node, x, y, tags):
        """Creates visual content for shop nodes."""
        content_items = {}
        current_y = y + NODE_HEADER_HEIGHT + max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        
        # Shop icon
        content_items['shop_icon'] = self.canvas.create_text(
            x + 20, current_y + 10, text="🏪", font=("Segoe UI Emoji", 16),
            fill=COLOR_ACCENT, anchor="nw", tags=tags
        )
        
        # Currency info
        content_items['currency_text'] = self.canvas.create_text(
            x + 50, current_y + 15, text=f"Currency: {node.currency_variable}",
            fill=COLOR_TEXT_MUTED, anchor="nw", font=FONT_OPTION, tags=tags
        )
        current_y += 30
        
        # Items for sale
        if node.items_for_sale:
            content_items['sale_label'] = self.canvas.create_text(
                x + 20, current_y, text="For Sale:", fill=COLOR_SUCCESS,
                anchor="nw", font=FONT_OPTION, tags=tags
            )
            current_y += 20
            
            for i, item in enumerate(node.items_for_sale[:3]):  # Show max 3 items
                item_text = f"• {item.get('name', 'Item')} - {item.get('price', 0)}"
                content_items[f'sale_item_{i}'] = self.canvas.create_text(
                    x + 30, current_y, text=item_text, fill=COLOR_TEXT,
                    anchor="nw", font=("Courier", 9), tags=tags
                )
                current_y += 18
            
            if len(node.items_for_sale) > 3:
                content_items['sale_more'] = self.canvas.create_text(
                    x + 30, current_y, text=f"... and {len(node.items_for_sale) - 3} more",
                    fill=COLOR_TEXT_MUTED, anchor="nw", font=("Courier", 9), tags=tags
                )
                current_y += 18
        
        # Items to buy
        if node.items_to_buy:
            content_items['buy_label'] = self.canvas.create_text(
                x + 20, current_y, text="Will Buy:", fill=COLOR_WARNING,
                anchor="nw", font=FONT_OPTION, tags=tags
            )
            current_y += 20
            
            for i, item in enumerate(node.items_to_buy[:2]):  # Show max 2 items
                item_text = f"• {item.get('name', 'Item')} - {item.get('price', 0)}"
                content_items[f'buy_item_{i}'] = self.canvas.create_text(
                    x + 30, current_y, text=item_text, fill=COLOR_TEXT,
                    anchor="nw", font=("Courier", 9), tags=tags
                )
                current_y += 18
        
        return content_items
    
    def _create_random_event_content(self, node, x, y, tags):
        """Creates visual content for random event nodes."""
        content_items = {}
        current_y = y + NODE_HEADER_HEIGHT + max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        
        # Random icon
        content_items['random_icon'] = self.canvas.create_text(
            x + 20, current_y + 10, text="🎲", font=("Segoe UI Emoji", 16),
            fill=COLOR_WARNING, anchor="nw", tags=tags
        )
        
        # Auto trigger info
        trigger_text = "Auto-trigger" if node.auto_trigger else "Manual trigger"
        content_items['trigger_text'] = self.canvas.create_text(
            x + 50, current_y + 15, text=trigger_text,
            fill=COLOR_TEXT_MUTED, anchor="nw", font=FONT_OPTION, tags=tags
        )
        current_y += 35
        
        # Outcomes
        if node.random_outcomes:
            content_items['outcomes_label'] = self.canvas.create_text(
                x + 20, current_y, text="Possible Outcomes:",
                fill=COLOR_ACCENT, anchor="nw", font=FONT_OPTION, tags=tags
            )
            current_y += 20
            
            total_weight = sum(outcome.get('weight', 1) for outcome in node.random_outcomes)
            
            for i, outcome in enumerate(node.random_outcomes[:3]):  # Show max 3 outcomes
                weight = outcome.get('weight', 1)
                percentage = (weight / total_weight * 100) if total_weight > 0 else 0
                desc = outcome.get('description', 'Unknown outcome')
                outcome_text = f"• {desc} ({percentage:.1f}%)"
                
                content_items[f'outcome_{i}'] = self.canvas.create_text(
                    x + 30, current_y, text=outcome_text, fill=COLOR_TEXT,
                    anchor="nw", font=("Courier", 9), tags=tags
                )
                current_y += 18
            
            if len(node.random_outcomes) > 3:
                content_items['outcomes_more'] = self.canvas.create_text(
                    x + 30, current_y, text=f"... and {len(node.random_outcomes) - 3} more",
                    fill=COLOR_TEXT_MUTED, anchor="nw", font=("Courier", 9), tags=tags
                )
        
        return content_items
    
    def _create_timer_content(self, node, x, y, tags):
        """Creates visual content for timer nodes."""
        content_items = {}
        current_y = y + NODE_HEADER_HEIGHT + max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        
        # Timer icon
        content_items['timer_icon'] = self.canvas.create_text(
            x + 20, current_y + 10, text="⏰", font=("Segoe UI Emoji", 16),
            fill=COLOR_WARNING, anchor="nw", tags=tags
        )
        
        # Wait time
        time_text = f"Wait: {node.wait_time} {node.time_unit}"
        content_items['time_text'] = self.canvas.create_text(
            x + 50, current_y + 15, text=time_text,
            fill=COLOR_TEXT, anchor="nw", font=FONT_OPTION, tags=tags
        )
        current_y += 35
        
        # Options
        options = []
        if node.show_countdown:
            options.append("Show countdown")
        if node.allow_skip:
            options.append("Allow skip")
        
        if options:
            content_items['options_text'] = self.canvas.create_text(
                x + 20, current_y, text="Options: " + ", ".join(options),
                fill=COLOR_TEXT_MUTED, anchor="nw", font=("Courier", 9), tags=tags
            )
            current_y += 20
        
        # Next node
        if node.next_node:
            content_items['next_text'] = self.canvas.create_text(
                x + 20, current_y, text=f"→ {node.next_node}",
                fill=COLOR_SUCCESS, anchor="nw", font=FONT_OPTION, tags=tags
            )
        
        return content_items
    
    def _create_inventory_content(self, node, x, y, tags):
        """Creates visual content for inventory nodes."""
        content_items = {}
        current_y = y + NODE_HEADER_HEIGHT + max(NODE_BASE_BODY_HEIGHT, node.calculated_text_height + 20)
        
        # Inventory icon
        content_items['inventory_icon'] = self.canvas.create_text(
            x + 20, current_y + 10, text="🎒", font=("Segoe UI Emoji", 16),
            fill=COLOR_ACCENT, anchor="nw", tags=tags
        )
        
        # Auto open info
        auto_text = "Auto-open" if node.auto_open else "Manual open"
        content_items['auto_text'] = self.canvas.create_text(
            x + 50, current_y + 15, text=auto_text,
            fill=COLOR_TEXT_MUTED, anchor="nw", font=FONT_OPTION, tags=tags
        )
        current_y += 35
        
        # Crafting recipes
        if node.crafting_recipes:
            content_items['recipes_label'] = self.canvas.create_text(
                x + 20, current_y, text="Crafting Recipes:",
                fill=COLOR_SUCCESS, anchor="nw", font=FONT_OPTION, tags=tags
            )
            current_y += 20
            
            for i, recipe in enumerate(node.crafting_recipes[:2]):  # Show max 2 recipes
                recipe_text = f"• {recipe.get('name', 'Recipe')} → {recipe.get('result', 'Item')}"
                content_items[f'recipe_{i}'] = self.canvas.create_text(
                    x + 30, current_y, text=recipe_text, fill=COLOR_TEXT,
                    anchor="nw", font=("Courier", 9), tags=tags
                )
                current_y += 18
            
            if len(node.crafting_recipes) > 2:
                content_items['recipes_more'] = self.canvas.create_text(
                    x + 30, current_y, text=f"... and {len(node.crafting_recipes) - 2} more",
                    fill=COLOR_TEXT_MUTED, anchor="nw", font=("Courier", 9), tags=tags
                )
                current_y += 18
        
        # Item actions
        if node.item_actions:
            action_names = [action.get('name', 'Action') for action in node.item_actions[:3]]
            actions_text = "Actions: " + ", ".join(action_names)
            if len(node.item_actions) > 3:
                actions_text += f" +{len(node.item_actions) - 3}"
            
            content_items['actions_text'] = self.canvas.create_text(
                x + 20, current_y, text=actions_text,
                fill=COLOR_TEXT_MUTED, anchor="nw", font=("Courier", 9), tags=tags
            )
        
        return content_items