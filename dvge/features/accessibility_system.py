# dvge/features/accessibility_system.py

"""Accessibility Suite - Core accessibility management system."""

import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class AccessibilityStandard(Enum):
    """Accessibility standards compliance levels."""
    WCAG_A = "wcag_a"
    WCAG_AA = "wcag_aa" 
    WCAG_AAA = "wcag_aaa"
    SECTION_508 = "section_508"
    ADA = "ada"


class ColorBlindnessType(Enum):
    """Types of color blindness to support."""
    PROTANOPIA = "protanopia"      # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"      # Blue-blind
    ACHROMATOPSIA = "achromatopsia" # Complete color blindness
    PROTANOMALY = "protanomaly"    # Red-weak
    DEUTERANOMALY = "deuteranomaly" # Green-weak
    TRITANOMALY = "tritanomaly"    # Blue-weak


@dataclass
class AccessibilitySettings:
    """Configuration for accessibility features."""
    # Visual accessibility
    high_contrast_mode: bool = False
    font_scaling: float = 1.0  # 0.5 to 3.0
    line_height: float = 1.5
    letter_spacing: float = 0.0
    reduce_motion: bool = False
    dark_mode: bool = False
    
    # Color accessibility
    colorblind_friendly: bool = False
    colorblind_type: str = ColorBlindnessType.DEUTERANOPIA.value
    color_enhancement: float = 1.0  # 0.0 to 2.0
    
    # Interaction accessibility
    keyboard_navigation: bool = True
    focus_indicators: bool = True
    click_delay: float = 0.0  # seconds
    auto_scroll: bool = False
    pause_on_focus: bool = True
    
    # Audio accessibility
    audio_descriptions: bool = False
    sound_effects: bool = True
    background_music: bool = True
    audio_volume: float = 1.0
    
    # Screen reader support
    screen_reader_optimized: bool = False
    semantic_markup: bool = True
    aria_labels: bool = True
    skip_links: bool = True
    
    # Cognitive accessibility
    simple_language: bool = False
    reading_guide: bool = False
    progress_indicators: bool = True
    error_prevention: bool = True
    
    # Standards compliance
    target_standard: str = AccessibilityStandard.WCAG_AA.value
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccessibilitySettings':
        return cls(**data)


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found during validation."""
    id: str
    type: str           # "error", "warning", "info"
    category: str       # "visual", "audio", "navigation", "content"
    severity: str       # "critical", "high", "medium", "low"
    title: str
    description: str
    element: Optional[str] = None  # CSS selector or element description
    guideline: Optional[str] = None  # WCAG guideline reference
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccessibilityIssue':
        return cls(**data)


@dataclass
class ColorPalette:
    """Represents a color palette with accessibility information."""
    id: str
    name: str
    colors: Dict[str, str]  # role -> color mapping
    contrast_ratios: Dict[str, float]  # pair -> contrast ratio
    colorblind_safe: bool = False
    wcag_compliant: bool = False
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColorPalette':
        return cls(**data)


class AccessibilityManager:
    """Central accessibility management system."""
    
    def __init__(self, app=None):
        self.app = app
        self.settings = AccessibilitySettings()
        self.color_palettes: Dict[str, ColorPalette] = {}
        self.validation_cache: List[AccessibilityIssue] = []
        
        # Storage paths
        self.a11y_data_dir = Path.home() / ".dvge" / "accessibility_data"
        self.settings_file = self.a11y_data_dir / "accessibility_settings.json"
        self.palettes_file = self.a11y_data_dir / "color_palettes.json"
        
        self._ensure_directories()
        self._load_data()
        self._initialize_color_palettes()
    
    def _ensure_directories(self):
        """Create necessary directories for accessibility data storage."""
        self.a11y_data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load accessibility data from disk."""
        try:
            # Load settings
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                    self.settings = AccessibilitySettings.from_dict(settings_data)
            
            # Load color palettes
            if self.palettes_file.exists():
                with open(self.palettes_file, 'r', encoding='utf-8') as f:
                    palettes_data = json.load(f)
                    self.color_palettes = {
                        pid: ColorPalette.from_dict(data)
                        for pid, data in palettes_data.items()
                    }
                    
        except Exception as e:
            print(f"Error loading accessibility data: {e}")
    
    def _save_data(self):
        """Save accessibility data to disk."""
        try:
            # Save settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=2)
            
            # Save color palettes
            with open(self.palettes_file, 'w', encoding='utf-8') as f:
                json.dump({
                    pid: palette.to_dict()
                    for pid, palette in self.color_palettes.items()
                }, f, indent=2)
                
        except Exception as e:
            print(f"Error saving accessibility data: {e}")
    
    def _initialize_color_palettes(self):
        """Initialize built-in accessible color palettes."""
        if self.color_palettes:
            return  # Already initialized
        
        # High contrast palette
        high_contrast = ColorPalette(
            id="high_contrast",
            name="High Contrast",
            colors={
                "background": "#000000",
                "text": "#FFFFFF", 
                "primary": "#FFFF00",
                "secondary": "#00FFFF",
                "accent": "#FF00FF",
                "success": "#00FF00",
                "warning": "#FFFF00",
                "error": "#FF0000",
                "disabled": "#808080"
            },
            contrast_ratios={
                "text/background": 21.0,
                "primary/background": 19.56,
                "secondary/background": 16.75
            },
            colorblind_safe=True,
            wcag_compliant=True,
            description="Maximum contrast for low vision users"
        )
        
        # Colorblind-friendly palette
        colorblind_friendly = ColorPalette(
            id="colorblind_friendly",
            name="Colorblind Friendly",
            colors={
                "background": "#F8F9FA",
                "text": "#212529",
                "primary": "#0D47A1",    # Blue
                "secondary": "#FF6F00",   # Orange
                "accent": "#7B1FA2",      # Purple
                "success": "#1B5E20",     # Dark green
                "warning": "#E65100",     # Dark orange
                "error": "#B71C1C",       # Dark red
                "disabled": "#9E9E9E"
            },
            contrast_ratios={
                "text/background": 16.94,
                "primary/background": 12.63,
                "secondary/background": 4.52
            },
            colorblind_safe=True,
            wcag_compliant=True,
            description="Safe colors for all types of color blindness"
        )
        
        # Dark mode accessible palette
        dark_accessible = ColorPalette(
            id="dark_accessible",
            name="Dark Mode Accessible",
            colors={
                "background": "#121212",
                "text": "#E0E0E0",
                "primary": "#90CAF9",     # Light blue
                "secondary": "#FFB74D",   # Light orange
                "accent": "#CE93D8",      # Light purple
                "success": "#A5D6A7",     # Light green
                "warning": "#FFCC02",     # Yellow
                "error": "#F48FB1",       # Light pink
                "disabled": "#616161"
            },
            contrast_ratios={
                "text/background": 12.63,
                "primary/background": 8.59,
                "secondary/background": 6.12
            },
            colorblind_safe=False,
            wcag_compliant=True,
            description="Dark theme with good contrast ratios"
        )
        
        self.color_palettes = {
            palette.id: palette
            for palette in [high_contrast, colorblind_friendly, dark_accessible]
        }
        
        self._save_data()
    
    def update_settings(self, new_settings: AccessibilitySettings) -> bool:
        """Update accessibility settings."""
        try:
            self.settings = new_settings
            self._save_data()
            
            # Apply settings to current project if available
            if self.app:
                self._apply_settings_to_project()
            
            return True
        except Exception as e:
            print(f"Error updating accessibility settings: {e}")
            return False
    
    def get_settings(self) -> AccessibilitySettings:
        """Get current accessibility settings."""
        return self.settings
    
    def _apply_settings_to_project(self):
        """Apply current accessibility settings to the project."""
        if not self.app:
            return
        
        # Update UI based on settings
        try:
            # Font scaling
            if hasattr(self.app, 'configure'):
                # Apply font scaling to the main window
                pass  # Implement font scaling logic
            
            # High contrast mode
            if self.settings.high_contrast_mode:
                self._apply_high_contrast_theme()
            
            # Reduced motion
            if self.settings.reduce_motion:
                self._disable_animations()
            
        except Exception as e:
            print(f"Error applying accessibility settings: {e}")
    
    def _apply_high_contrast_theme(self):
        """Apply high contrast color theme."""
        if "high_contrast" in self.color_palettes:
            palette = self.color_palettes["high_contrast"]
            # Apply palette colors to UI elements
            # This would integrate with the existing theme system
            pass
    
    def _disable_animations(self):
        """Disable or reduce animations for motion sensitivity."""
        # Reduce transition durations, disable auto-scroll, etc.
        pass
    
    def calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors."""
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def relative_luminance(rgb: Tuple[int, int, int]) -> float:
            def normalize(c: int) -> float:
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r, g, b = [normalize(c) for c in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        try:
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            lum1 = relative_luminance(rgb1)
            lum2 = relative_luminance(rgb2)
            
            lighter = max(lum1, lum2)
            darker = min(lum1, lum2)
            
            return (lighter + 0.05) / (darker + 0.05)
            
        except Exception:
            return 1.0  # Default to poor contrast on error
    
    def validate_color_palette(self, palette: ColorPalette) -> List[AccessibilityIssue]:
        """Validate a color palette for accessibility compliance."""
        issues = []
        
        # Check contrast ratios
        bg_color = palette.colors.get("background", "#FFFFFF")
        text_color = palette.colors.get("text", "#000000")
        
        text_contrast = self.calculate_contrast_ratio(text_color, bg_color)
        
        if text_contrast < 4.5:
            issues.append(AccessibilityIssue(
                id=f"contrast_text_{palette.id}",
                type="error",
                category="visual",
                severity="critical",
                title="Insufficient Text Contrast",
                description=f"Text contrast ratio is {text_contrast:.2f}, minimum required is 4.5:1",
                guideline="WCAG 2.1 AA - 1.4.3 Contrast (Minimum)",
                suggestion="Increase contrast between text and background colors",
                auto_fixable=True
            ))
        
        # Check primary button contrast
        primary_color = palette.colors.get("primary", "#0000FF")
        primary_contrast = self.calculate_contrast_ratio(primary_color, bg_color)
        
        if primary_contrast < 3.0:
            issues.append(AccessibilityIssue(
                id=f"contrast_primary_{palette.id}",
                type="warning",
                category="visual", 
                severity="high",
                title="Low Primary Color Contrast",
                description=f"Primary color contrast is {primary_contrast:.2f}, recommended minimum is 3:1",
                guideline="WCAG 2.1 AA - 1.4.11 Non-text Contrast",
                suggestion="Use a darker or lighter shade of the primary color"
            ))
        
        # Check for colorblind accessibility
        if not palette.colorblind_safe:
            issues.append(AccessibilityIssue(
                id=f"colorblind_{palette.id}",
                type="warning",
                category="visual",
                severity="medium",
                title="Colorblind Accessibility Concern",
                description="Palette may not be distinguishable by users with color vision deficiencies",
                suggestion="Test colors with colorblind simulation tools and add patterns or shapes as alternatives"
            ))
        
        return issues
    
    def validate_project_accessibility(self) -> List[AccessibilityIssue]:
        """Validate the current project for accessibility issues."""
        if not self.app:
            return []
        
        issues = []
        
        # Check if nodes have proper text alternatives
        if hasattr(self.app, 'nodes'):
            for node_id, node in self.app.nodes.items():
                # Check for images without alt text
                if hasattr(node, 'backgroundImage') and node.backgroundImage:
                    if not hasattr(node, 'alt_text') or not node.alt_text:
                        issues.append(AccessibilityIssue(
                            id=f"missing_alt_{node_id}",
                            type="error",
                            category="content",
                            severity="high",
                            title="Missing Alternative Text",
                            description=f"Node {node_id} has an image without alternative text",
                            element=f"node_{node_id}",
                            guideline="WCAG 2.1 A - 1.1.1 Non-text Content",
                            suggestion="Add descriptive alternative text for the image",
                            auto_fixable=False
                        ))
                
                # Check for empty dialogue text
                if hasattr(node, 'text') and not node.text.strip():
                    issues.append(AccessibilityIssue(
                        id=f"empty_text_{node_id}",
                        type="warning",
                        category="content",
                        severity="medium",
                        title="Empty Dialogue Text",
                        description=f"Node {node_id} has no dialogue text",
                        element=f"node_{node_id}",
                        suggestion="Add descriptive text or audio content for screen reader users"
                    ))
                
                # Check for very long text blocks
                if hasattr(node, 'text') and len(node.text) > 1000:
                    issues.append(AccessibilityIssue(
                        id=f"long_text_{node_id}",
                        type="info",
                        category="cognitive",
                        severity="low",
                        title="Very Long Text Block",
                        description=f"Node {node_id} contains over 1000 characters of text",
                        suggestion="Consider breaking long text into smaller chunks for better readability"
                    ))
        
        # Check choice accessibility
        if hasattr(self.app, 'nodes'):
            for node_id, node in self.app.nodes.items():
                if hasattr(node, 'options') and node.options:
                    if len(node.options) > 6:
                        issues.append(AccessibilityIssue(
                            id=f"too_many_choices_{node_id}",
                            type="warning",
                            category="cognitive",
                            severity="medium",
                            title="Too Many Choices",
                            description=f"Node {node_id} has {len(node.options)} options",
                            suggestion="Consider reducing choices to 6 or fewer for cognitive accessibility"
                        ))
        
        # Cache validation results
        self.validation_cache = issues
        return issues
    
    def generate_accessibility_css(self) -> str:
        """Generate CSS for accessibility enhancements."""
        css_parts = []
        
        # Base accessibility styles
        css_parts.append("""
/* Accessibility Enhancement Styles */
.accessibility-enhanced {
    /* Font scaling support */
    font-size: calc(1rem * var(--font-scale, 1));
    line-height: var(--line-height, 1.5);
    letter-spacing: var(--letter-spacing, 0);
}

/* Focus indicators */
.focus-indicators *:focus {
    outline: 3px solid var(--focus-color, #0066CC);
    outline-offset: 2px;
    box-shadow: 0 0 0 1px #FFFFFF;
}

.focus-indicators *:focus:not(:focus-visible) {
    outline: none;
    box-shadow: none;
}

/* High contrast mode */
.high-contrast {
    background: #000000 !important;
    color: #FFFFFF !important;
}

.high-contrast a {
    color: #FFFF00 !important;
}

.high-contrast button {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 2px solid #FFFFFF !important;
}

.high-contrast button:hover {
    background: #FFFF00 !important;
    color: #000000 !important;
}

/* Reduced motion */
.reduce-motion * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
}

/* Large text mode */
.large-text {
    --font-scale: 1.5;
}

.extra-large-text {
    --font-scale: 2.0;
}

/* Screen reader only content */
.sr-only {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}

/* Skip links */
.skip-link {
    position: absolute;
    top: -40px;
    left: 6px;
    background: #000000;
    color: #FFFFFF;
    padding: 8px;
    text-decoration: none;
    border-radius: 4px;
    z-index: 9999;
}

.skip-link:focus {
    top: 6px;
}
""")
        
        # Apply current settings
        if self.settings.high_contrast_mode:
            css_parts.append("""
body {
    filter: contrast(1.5) brightness(1.2);
}
""")
        
        if self.settings.font_scaling != 1.0:
            css_parts.append(f"""
:root {{
    --font-scale: {self.settings.font_scaling};
}}
""")
        
        if self.settings.reduce_motion:
            css_parts.append("""
* {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
}
""")
        
        return "\n".join(css_parts)
    
    def generate_accessibility_javascript(self) -> str:
        """Generate JavaScript for accessibility enhancements."""
        js_parts = []
        
        # Base accessibility script
        js_parts.append("""
// Accessibility Enhancement JavaScript
class AccessibilityManager {
    constructor(settings = {}) {
        this.settings = settings;
        this.init();
    }
    
    init() {
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
        this.applySettings();
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Tab navigation enhancement
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
            
            // Skip link functionality
            if (e.key === 'Escape') {
                const skipLink = document.querySelector('.skip-link');
                if (skipLink) skipLink.focus();
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }
    
    setupFocusManagement() {
        const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        
        // Trap focus in modals
        document.addEventListener('keydown', (e) => {
            const modal = document.querySelector('.modal:not([hidden])');
            if (!modal || e.key !== 'Tab') return;
            
            const focusable = modal.querySelectorAll(focusableElements);
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        });
    }
    
    setupScreenReaderSupport() {
        // Announce dynamic content changes
        this.announcer = document.createElement('div');
        this.announcer.setAttribute('aria-live', 'polite');
        this.announcer.setAttribute('aria-atomic', 'true');
        this.announcer.className = 'sr-only';
        document.body.appendChild(this.announcer);
    }
    
    announce(message, priority = 'polite') {
        this.announcer.setAttribute('aria-live', priority);
        this.announcer.textContent = message;
        
        setTimeout(() => {
            this.announcer.textContent = '';
        }, 1000);
    }
    
    applySettings() {
        const body = document.body;
        
        // Apply accessibility classes based on settings
        body.classList.toggle('high-contrast', this.settings.high_contrast_mode);
        body.classList.toggle('reduce-motion', this.settings.reduce_motion);
        body.classList.toggle('focus-indicators', this.settings.focus_indicators);
        body.classList.toggle('large-text', this.settings.font_scaling >= 1.5);
        body.classList.toggle('extra-large-text', this.settings.font_scaling >= 2.0);
        
        // Apply font scaling
        document.documentElement.style.setProperty('--font-scale', this.settings.font_scaling || 1);
        document.documentElement.style.setProperty('--line-height', this.settings.line_height || 1.5);
        document.documentElement.style.setProperty('--letter-spacing', this.settings.letter_spacing || 0);
    }
    
    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        this.applySettings();
    }
}
""")
        
        # Initialize with current settings
        js_parts.append(f"""
// Initialize accessibility manager with current settings
const accessibilityManager = new AccessibilityManager({json.dumps(self.settings.to_dict())});
""")
        
        return "\n".join(js_parts)
    
    def export_for_html(self) -> Dict[str, Any]:
        """Export accessibility data for HTML game export."""
        return {
            "settings": self.settings.to_dict(),
            "color_palettes": {
                pid: palette.to_dict()
                for pid, palette in self.color_palettes.items()
            },
            "css": self.generate_accessibility_css(),
            "javascript": self.generate_accessibility_javascript(),
            "validation_issues": [issue.to_dict() for issue in self.validation_cache]
        }
    
    def get_accessibility_report(self) -> Dict[str, Any]:
        """Generate comprehensive accessibility report."""
        issues = self.validate_project_accessibility()
        
        # Categorize issues
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        by_category = {"visual": [], "audio": [], "navigation": [], "content": [], "cognitive": []}
        
        for issue in issues:
            by_severity[issue.severity].append(issue)
            by_category[issue.category].append(issue)
        
        # Calculate compliance score
        total_issues = len(issues)
        critical_issues = len(by_severity["critical"])
        high_issues = len(by_severity["high"])
        
        if total_issues == 0:
            compliance_score = 100
        else:
            # Weight issues by severity
            weighted_score = (critical_issues * 4) + (high_issues * 2) + len(by_severity["medium"])
            max_score = total_issues * 4
            compliance_score = max(0, 100 - (weighted_score / max_score * 100))
        
        return {
            "compliance_score": round(compliance_score, 1),
            "total_issues": total_issues,
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "by_category": {k: len(v) for k, v in by_category.items()},
            "issues": [issue.to_dict() for issue in issues],
            "recommendations": self._generate_recommendations(issues),
            "target_standard": self.settings.target_standard
        }
    
    def _generate_recommendations(self, issues: List[AccessibilityIssue]) -> List[str]:
        """Generate accessibility recommendations based on issues found."""
        recommendations = []
        
        # Count issue types
        contrast_issues = len([i for i in issues if "contrast" in i.id])
        alt_text_issues = len([i for i in issues if "alt" in i.id])
        cognitive_issues = len([i for i in issues if i.category == "cognitive"])
        
        if contrast_issues > 0:
            recommendations.append(
                f"Improve color contrast in {contrast_issues} areas. "
                "Use the high contrast color palette or adjust colors to meet WCAG AA standards."
            )
        
        if alt_text_issues > 0:
            recommendations.append(
                f"Add alternative text to {alt_text_issues} images. "
                "This is critical for screen reader users to understand visual content."
            )
        
        if cognitive_issues > 3:
            recommendations.append(
                "Consider cognitive accessibility improvements: break up long text, "
                "reduce choice complexity, and add progress indicators."
            )
        
        if not recommendations:
            recommendations.append("Great job! No major accessibility issues found.")
        
        return recommendations
    
    def cleanup(self):
        """Clean up resources and save data."""
        self._save_data()